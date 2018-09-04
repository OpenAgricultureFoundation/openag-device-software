# Import standard python modules
import time, os, datetime, glob, threading

# Import python types
from typing import Optional, Tuple, Dict, Any, List

# Import device comms
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import I2CError
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import usb_device_matches
from device.utilities.threaded import acquire_lock, release_lock

# Import peripheral modules
from device.peripherals.common.dac5578.driver import DAC5578Driver
from device.peripherals.classes.peripheral.exceptions import DriverError, InitError
from device.peripherals.modules.usb_camera.exceptions import (
    GetCameraError,
    EnableCameraError,
    DisableCameraError,
    CaptureError,
    CaptureImageError,
)


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
        i2c_lock: Optional[threading.Lock] = None,
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
        self.logger = Logger(name="Driver({})".format(name), dunder_name=__name__)

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            self.directory = "device/peripherals/modules/usb_camera/tests/images/"
        else:
            self.directory = "images/"

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
            raise InitError(logger=self.logger) from e

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
            if usb_device_matches(camera, vendor_id, product_id):
                matches.append(camera)

        return matches

    def get_camera(self) -> str:
        """Gets camera path."""

        # Get camera paths that match vendor and product ID
        cameras = self.list_cameras(self.vendor_id, self.product_id)

        # Check only one active camera
        if len(cameras) < 1:
            message = "no active cameras"
            raise GetCameraError(message=message, logger=self.logger)
        elif len(cameras) > 1:
            message = "too many active cameras"
            raise GetCameraError(message=message, logger=self.logger)

        # Successfuly got one camera
        return cameras[0]

    def enable_camera(self, retry: bool = True) -> None:
        """Enables camera by setting dac output high."""
        self.logger.debug("Enabling camera")

        # Turn on usb mux channel
        try:
            self.dac5578.set_high(
                channel=self.usb_mux_channel, retry=retry
            )  # type: ignore
        except DriverError as e:
            raise EnableCameraError(logger=self.logger) from e

        # Wait for camera to initialize
        time.sleep(5)

    def disable_camera(self, retry: bool = True) -> None:
        """Disables camera by setting dac output low."""
        self.logger.debug("Disabling camera")

        # Turn off usb mux channel
        try:
            self.dac5578.set_low(
                channel=self.usb_mux_channel, retry=retry
            )  # type: ignore
        except DriverError as e:
            raise DisableCameraError(logger=self.logger) from e

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
                raise DisableCameraError(logger=self.logger) from e

            # Check for timeout
            if time.time() - start_time > 5:  # 5 second timeout
                message = "timed out"
                raise DisableCameraError(message=message, logger=self.logger)

            # Update every 100ms
            time.sleep(0.1)

    def capture(self, retry: bool = True) -> None:
        """Manages usb mux and captures an image."""

        # Check if not using usb mux
        if self.dac5578 == None:
            return self.capture_image()

        # "Lock camera threads
        acquire_lock("usb-camera-dac5578")

        # Manage 'mux' and capture image
        try:
            self.enable_camera()
            self.capture_image()
            self.disable_camera()
        except DriverError as e:
            raise CaptureError(logger=self.logger) from e

        # Unlock camera threads
        release_lock("usb-camera-dac5578")

    def capture_image(self) -> None:
        """Captures an image."""

        # Name image according to ISO8601
        timestr = datetime.datetime.utcnow().strftime("%Y-%m-%d-T%H:%M:%SZ")
        filename = timestr + "_" + self.name + ".png"

        # Build filepath string
        filepath = self.directory + filename

        # Check if simulated
        if self.simulate:
            self.logger.info("Simulating saving image to: {}".format(filepath))
            command = "cp device/peripherals/modules/usb_camera/tests/simulation_image.png {}".format(
                filepath
            )
            os.system(command)
            return

        # Camera not simulated, get camera path
        try:
            camera = self.get_camera()
        except GetCameraError as e:
            raise CaptureImageError(logger=self.logger) from e

        # Capture image
        self.logger.info("Capturing image from: {} to: {}".format(camera, filepath))
        try:
            command = "fswebcam -d {} -r {} --png 9 --no-banner --save {}".format(
                camera, self.resolution, filepath
            )
            self.logger.debug("command = {}".format(command))
            os.system(command)
        except Exception as e:
            raise CaptureImageError(logger=self.logger) from e

        # TODO: Wait for file in destination and do some prelim checks:
        #  - filesize not too small?
        #  - all black? all white?
