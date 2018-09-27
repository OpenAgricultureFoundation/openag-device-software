# Import standard python modules
import time, os, datetime, glob, threading

# Import python types
from typing import Optional, Tuple, Dict, Any, List

# Import device utilities
from device.utilities import logger, accessors
from device.communication.i2c.main import I2C
from device.communication.i2c.exceptions import I2CError
from device.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.common.dac5578.driver import DAC5578Driver
from device.peripherals.common.dac5578.exceptions import DriverError as DAC5578DriverError
from device.peripherals.modules.usb_camera import exceptions

# Initialize file paths
IMAGE_PATH = "data/images/"
SIMULATE_IMAGE_PATH = "device/peripherals/modules/usb_camera/tests/images/"


class USBCameraDriver:
    """Driver for a usb camera."""

    def __init__(
        self,
        name: str,
        vendor_id: int,
        product_id: int,
        resolution: str,
        simulate: bool = False,
        usb_mux_comms: Optional[Dict[str, Any]] = None,
        usb_mux_channel: Optional[int] = None,
        i2c_lock: Optional[threading.RLock] = None,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes USB camera camera."""

        # Initialize parameters
        self.name = name
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.resolution = resolution
        self.simulate = simulate

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, __name__)

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            self.directory = SIMULATE_IMAGE_PATH
        else:
            self.directory = IMAGE_PATH

        # Check directory exists else create it
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Check if using usb mux
        if usb_mux_comms == None or usb_mux_channel == None:
            self.dac5578 = None
            return

        # Get optional i2c parameters
        mux = usb_mux_comms.get("mux", None)  # type: ignore
        if mux != None:
            mux = int(mux, 16)

        # Using usb mux, initialize driver
        try:
            self.dac5578 = DAC5578Driver(
                name=name,
                i2c_lock=i2c_lock,  # type: ignore
                bus=usb_mux_comms.get("bus", None),  # type: ignore
                address=int(usb_mux_comms.get("address", None), 16),  # type: ignore
                mux=mux,
                channel=usb_mux_comms.get("channel", None),  # type: ignore
                simulate=simulate,
                mux_simulator=mux_simulator,
            )
            self.usb_mux_channel = usb_mux_channel
        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

    def list_cameras(
        self, vendor_id: Optional[int] = None, product_id: Optional[int] = None
    ) -> List[str]:
        """Returns list of cameras that match the provided vendor id and 
        product id."""

        # List all cameras
        cameras = glob.glob("/dev/video*")

        # Check if filtering by product and vendor id
        if vendor_id == None and product_id == None:
            return cameras

        # Check for product and vendor id matches
        matches = []
        for camera in cameras:
            vid = vendor_id
            pid = product_id
            if accessors.usb_device_matches(camera, vid, pid):  # type: ignore
                matches.append(camera)

        return matches

    def get_camera(self) -> str:
        """Gets camera path."""

        # Get camera paths that match vendor and product ID
        cameras = self.list_cameras(self.vendor_id, self.product_id)

        # Check only one active camera
        if len(cameras) < 1:
            message = "no active cameras"
            raise exceptions.GetCameraError(message=message, logger=self.logger)
        elif len(cameras) > 1:
            message = "too many active cameras"
            raise exceptions.GetCameraError(message=message, logger=self.logger)

        # Successfuly got one camera
        return cameras[0]

    def enable_camera(self, retry: bool = True) -> None:
        """Enables camera by setting dac output high."""
        self.logger.debug("Enabling camera")

        # Turn on usb mux channel
        try:
            channel = self.usb_mux_channel
            self.dac5578.set_high(channel=channel, retry=retry)  # type: ignore
        except DAC5578DriverError as e:
            raise exceptions.EnableCameraError(logger=self.logger) from e

        # Wait for camera to initialize
        time.sleep(5)

    def disable_camera(self, retry: bool = True) -> None:
        """Disables camera by setting dac output low."""
        self.logger.debug("Disabling camera")

        # Turn off usb mux channel
        try:
            channel = self.usb_mux_channel
            self.dac5578.set_low(channel=channel, retry=retry)  # type: ignore
        except DAC5578DriverError as e:
            raise exceptions.DisableCameraError(logger=self.logger) from e

        # Wait for camera to power down
        start_time = time.time()
        while True:  # 5 second timeout

            # Look for camera
            try:
                camera = self.get_camera()

                # Check if camera powered down
                if camera == None:
                    self.logger.debug("Camera powered down")
                    return

            # TODO: Handle specific exceptions
            except Exception as e:
                raise exceptions.DisableCameraError(logger=self.logger) from e

            # Check for timeout
            if time.time() - start_time > 5:  # 5 second timeout
                message = "timed out"
                raise exceptions.DisableCameraError(message=message, logger=self.logger)

            # Update every 100ms
            time.sleep(0.1)

    def capture(self, retry: bool = True) -> None:
        """Manages usb mux and captures an image."""

        # Check if not using usb mux
        if self.dac5578 == None:
            return self.capture_image()

        # TODO: Lock camera threads

        # Manage 'mux' and capture image
        try:
            self.enable_camera()
            self.capture_image()
            self.disable_camera()
        except DAC5578DriverError as e:
            raise exceptions.CaptureError(logger=self.logger) from e

        # TODO: Unlock camera threads

    def capture_image(self) -> None:
        """Captures an image."""

        # Name image according to ISO8601
        timestr = datetime.datetime.utcnow().strftime("%Y-%m-%d-T%H:%M:%SZ")
        filename = timestr + "_" + self.name + ".png"

        # Specify filepaths
        image_path = self.directory + filename
        base_path = "device/peripherals/modules/usb_camera"
        dummy_path = "{}/dummy.png".format(base_path)
        active_path = "{}/active.jpg".format(base_path)

        # Check if simulated
        if self.simulate:
            self.logger.info(
                "Simulating capture, saving simulation image to: {}".format(image_path)
            )
            command = "cp device/peripherals/modules/usb_camera/tests/simulation_image.png {}".format(
                image_path
            )
            os.system(command)
            return

        # Camera not simulated, get camera path
        try:
            camera = self.get_camera()
        except exceptions.GetCameraError as e:
            raise exceptions.CaptureImageError(logger=self.logger) from e

        # Capture image
        try:
            # Take 3 low res images to clear out buffer
            self.logger.debug("Capturing dummy images")
            command = "fswebcam -d {} -r '320x240' ".format(camera, dummy_path)
            for i in range(3):
                os.system(command)

            # Try taking up to 3 real images
            self.logger.debug("Capturing active image")
            command = "fswebcam -d {} -r {} --png 9 -F 10 --no-banner --save {}".format(
                camera, self.resolution, active_path
            )
            valid_image = False
            for i in range(3):
                os.system(command)
                size = os.path.getsize(active_path)

                # Check if image meets minimum size constraint
                # TODO: Check lighting conditions (if box is dark, images are small)
                if size > 160000:  # 160kB
                    valid_image = True
                    break

            # Check if active image is valid, if so copy to images/ directory
            if not valid_image:
                self.logger.warning("Unable to capture a valid image")
            else:
                self.logger.info("Captured image, saved to {}".format(image_path))
                os.rename(active_path, image_path)

        except Exception as e:
            raise exceptions.CaptureImageError(logger=self.logger) from e
