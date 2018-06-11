# Import standard python modules
from typing import Tuple, Optional 
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error

# Import device drivers
from device.peripherals.common.usb_camera.driver import USBCameraDriver


class ELPUSB500W02ML21Camera:
    """ ELP USB500W02M-L21 usb camera. """

    def __init__(self, name: str, directory: str, simulate: bool = False) -> None:
        """ Instantiates camera. """

        # Initialize logger
        self.logger = Logger(
            name = "Camera({})".format(name),
            dunder_name = __name__,
        )
        
        # Initialize name and simulation status
        self.name = name
        self.simulate = simulate
        self.directory = directory

        # Initialize driver
        self.driver = USBCameraDriver(
            name = name,
            resolution = (2592, 1944),
            vendor_id = 0x05A3,
            product_id = 0x9520,
            directory = directory,
        )

        # Initialize health metrics
        self.health = 100.0


    def probe(self) -> Error:
        """ Probes camera. """
        self.logger.info("Probing")

        # Check if simulating
        if self.simulate:
            self.logger.info("Probe simulated!")
            return Error(None)
        
        # Probe driver
        _, error = self.driver.get_camera()

        # Check for errors:
        if error.exists():
            error.report("Probe failed")
            self.health = 0.0
            return error

        # Successfully probed!
        self.logger.info("Probe successful!")
        return Error(None)


    def capture(self) -> Error:
        """ Captures an image. """

        # Check for simulate
        if self.simulate:
            return Error(None)

        # Capture image
        error = self.driver.capture()

        # Check for errors
        if error.exists():
            error.report("Camera unable to capture image")
            self.health = 0.0
            return error

        # Capture successful!
        return Error(None)


    def reset(self) -> None:
        """ Resets camera. """
        self.health = 100.0