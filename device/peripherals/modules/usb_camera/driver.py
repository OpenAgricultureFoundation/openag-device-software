# Import standard python modules
import time, os, datetime, glob, threading

# Import python types
from typing import Optional, Tuple, Dict, Any, List

# Import device utilities
from device.utilities import logger, usb
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.common.dac5578.driver import DAC5578Driver
from device.peripherals.common.dac5578.exceptions import DriverError as DAC5578DriverError
from device.peripherals.modules.usb_camera import exceptions

# Initialize file paths
IMAGE_DIR = "data/images/"
MODULE_DIR = "device/peripherals/modules/usb_camera/"
SIMULATE_IMAGE_DIR = MODULE_DIR + "tests/images/"
DUMMY_IMAGE_PATH = MODULE_DIR + "dummy.png"
ACTIVE_IMAGE_PATH = MODULE_DIR + "active.png"
SIMULATION_IMAGE_PATH = MODULE_DIR + "tests/simulation_image.png"


class USBCameraDriver:
    """Driver for a usb camera."""

    def __init__(
        self,
        name: str,
        vendor_id: int,
        product_id: int,
        resolution: str,
        num_cameras: int = 1,
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
        self.num_cameras = num_cameras
        self.simulate = simulate

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            self.directory = SIMULATE_IMAGE_DIR
        else:
            self.directory = IMAGE_DIR

        # Check directory exists else create it
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Check if using usb mux
        if usb_mux_comms == None or usb_mux_channel == None:
            self.usb_mux_enabled = False
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
            self.usb_mux_enabled = True
        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

    def capture(self, retry: bool = True) -> None:
        """Captures an image from a camera or set of non-unique cameras."""
        self.logger.debug("Capturing")

        # Capture images
        try:
            # with self.usb_camera_lock:
            self.enable_cameras(wait_for_enable=True, timeout=10)
            self.capture_images()
            self.disable_cameras(wait_for_disable=True, timeout=10)
        except DAC5578DriverError as e:
            raise exceptions.CaptureError(logger=self.logger) from e
        except Exception as e:
            message = "Unable to capture, unhandled exception: {}".format(type(e))
            self.logger.warning(message)
            raise exceptions.CaptureError(logger=self.logger) from e

    def capture_images(self) -> None:
        """Captures an image from each active camera."""
        self.logger.debug("Capturing images")

        # Get real or simulated camera paths
        if not self.simulate:
            camera_paths = usb.get_camera_paths(self.vendor_id, self.product_id)
        else:
            camera_paths = []
            for i in range(self.num_cameras):
                camera_paths.append("simulate_path")

        # Capture an image from each active camera
        for index, camera_path in enumerate(camera_paths):

            # Get timestring in ISO8601 format
            timestring = datetime.datetime.utcnow().strftime("%Y-%m-%d-T%H:%M:%SZ")

            # Get filename for individual camera or camera instance in set
            if self.num_cameras == 1:
                filename = "{}_{}.png".format(timestring, self.name)
            else:
                filename = "{}_{}-{}.png".format(timestring, self.name, index + 1)

            # Create image path
            image_path = self.directory + filename

            # Capture image
            self.capture_image(camera_path, image_path)

    def capture_image(self, camera_path: str, image_path: str) -> None:
        """Captures an image."""
        self.logger.debug("Capturing image")

        # Capture image
        try:
            # Check if simulated
            if self.simulate:
                message = "Simulating capture, saving image to: {}".format(image_path)
                self.logger.info(message)
                command = "cp {} {}".format(SIMULATION_IMAGE_PATH, image_path)
                os.system(command)
                return

            # Take 3 low res images to clear out buffer
            self.logger.debug("Capturing dummy images")
            command = "fswebcam -d {} -r '320x240' ".format(
                camera_path, DUMMY_IMAGE_PATH
            )
            for i in range(3):
                os.system(command)

            # Try taking up to 3 real images
            self.logger.debug("Capturing active image")
            command = "fswebcam -d {} -r {} --png 9 -F 10 --no-banner --save {}".format(
                camera_path, self.resolution, ACTIVE_IMAGE_PATH
            )
            valid_image = False
            for i in range(3):
                os.system(command)
                size = os.path.getsize(ACTIVE_IMAGE_PATH)

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
                os.rename(ACTIVE_IMAGE_PATH, image_path)

        except Exception as e:
            raise exceptions.CaptureImageError(logger=self.logger) from e

    def enable_cameras(
        self, wait_for_enable: bool = False, timeout: float = 5, retry: bool = True
    ) -> None:
        """Enables camera by setting dac output high."""
        self.logger.debug("Enabling cameras")

        # Check if using usb mux
        if not self.usb_mux_enabled:
            return

        # Turn on usb mux channel
        try:
            channel = self.usb_mux_channel
            self.dac5578.set_high(channel=channel, retry=retry)
        except DAC5578DriverError as e:
            raise exceptions.EnableCameraError(logger=self.logger) from e

        # Check if waiting for enable
        if not wait_for_enable:
            return

        # Wait for camera to be enabled
        self.logger.debug("Waiting for cameras to become enabled")

        # Check if simulated
        if self.simulated:
            self.logger.debug("Simulated camera enable complete")
            return

        # Initialize timing variables
        start_time = time.time()

        # Loop forever
        while True:

            # Look for camera
            try:
                camera_paths = usb.get_camera_paths(self.vendor_id, self.product_id)

                # Check if camera powered down
                if len(camera_paths) == self.num_cameras:
                    self.logger.debug("All cameras enabled")
                    return

            except Exception as e:
                raise exceptions.DisableCameraError(logger=self.logger) from e

            # Check for timeout
            if time.time() - start_time > timeout:
                message = "timed out"
                raise exceptions.EnableCameraError(message=message, logger=self.logger)

            # Update every 100ms
            time.sleep(0.1)

    def disable_cameras(
        self, wait_for_disable: bool = False, timeout: float = 5, retry: bool = True
    ) -> None:
        """Disables camera by setting dac output low."""
        self.logger.debug("Disabling cameras")

        # Check if using usb mux
        if not self.usb_mux_enabled:
            return

        # Turn off usb mux channel
        try:
            channel = self.usb_mux_channel
            self.dac5578.set_low(channel=channel, retry=retry)
        except DAC5578DriverError as e:
            raise exceptions.DisableCameraError(logger=self.logger) from e

        # Check if waiting for disable
        if not wait_for_disable:
            return

        # Wait for camera to be disabled
        self.logger.debug("Waiting for cameras to become disabled")

        # Check if simulated
        if self.simulated:
            self.logger.debug("Simulated camera disable complete")
            return

        # Initialize timing variables
        start_time = time.time()

        # Loop forever
        while True:

            # Look for camera
            try:
                camera_paths = usb.get_camera_paths(self.vendor_id, self.product_id)

                # Check if all cameras are disables
                if camera_paths == []:
                    self.logger.debug("All cameras disabled")
                    return

            except Exception as e:
                raise exceptions.DisableCameraError(logger=self.logger) from e

            # Check for timeout
            if time.time() - start_time > timeout:
                message = "timed out"
                raise exceptions.DisableCameraError(message=message, logger=self.logger)

            # Update every 100ms
            time.sleep(0.1)
