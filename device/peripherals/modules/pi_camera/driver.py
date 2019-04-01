# Import standard python modules
import time, os, datetime, glob, threading

# Import python types
from typing import Optional, Tuple, Dict, Any, List

# Import Django settings (for DATA_PATH)
from django.conf import settings

# Import picamera
from picamera import PiCamera

# Import device utilities
from device.utilities import logger
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

PLATFORM = os.getenv("PLATFORM")

# Initialize file paths
IMAGE_DIR = settings.DATA_PATH + "/images/"
MODULE_DIR = "device/peripherals/modules/usb_camera/"
SIMULATE_IMAGE_DIR = MODULE_DIR + "tests/images/"
DUMMY_IMAGE_PATH = MODULE_DIR + "dummy.png"
ACTIVE_IMAGE_PATH = MODULE_DIR + "active.png"
SIMULATION_IMAGE_PATH = MODULE_DIR + "tests/simulation_image.png"


class PiCameraDriver:
    """Driver for a usb camera."""

    def __init__(
        self,
        name: str,
        vendor_id: int,
        product_id: int,
        resolution: str,
        num_cameras: int = 1,
        simulate: bool = False,
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

        # pi camera is only for Raspberry Pi.
        if PLATFORM is not None and PLATFORM == "raspberry-pi":
            self.camera = PiCamera()
        else:
            self.logger.info(
                "pi_camera module: Not running on raspberry-pi OS. Turning on simulation mode."
            )
            self.simulate = True

        # Check if simulating
        if self.simulate:
            self.logger.info("Simulating driver")
            self.directory = SIMULATE_IMAGE_DIR
        else:
            self.directory = IMAGE_DIR

        # Check directory exists else create it
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def capture(self, retry: bool = True) -> None:
        """Captures an image from a camera or set of non-unique cameras."""
        self.logger.debug("Capturing")
        timestring = datetime.datetime.utcnow().strftime("%Y-%m-%d_T%H-%M-%SZ")
        filename = "{}_{}.png".format(self.directory, self.name)

        # Check if simulated
        if self.simulate:
            message = "Simulating capture, saving image to: {}".format(filename)
            self.logger.info(message)
            command = "cp {} {}".format(SIMULATION_IMAGE_PATH, filename)
            os.system(command)
            return

        # Capture image
        resolution_array = self.resolution.split("x")
        self.camera.resolution = (int(resolution_array[0]), int(resolution_array[1]))
        self.camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        # Get timestring in ISO8601 format

        self.camera.capture(IMAGE_DIR + filename)
        self.camera.stop_preview()
