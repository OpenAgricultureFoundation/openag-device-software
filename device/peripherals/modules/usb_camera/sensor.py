# Import standard python modules
from typing import Tuple, Optional
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error

# Import device drivers
from device.peripherals.modules.usb_camera.driver import USBCameraDriver


class USBCameraSensor:
    """ A usb camera sensor. """

    def __init__(
        self,
        name: str,
        directory: str,
        vendor_id: int,
        product_id: int,
        resolution: str,
        simulate: bool = False,
        usb_mux_comms=None,
        usb_mux_channel=None,
    ) -> None:
        """ Instantiates camera. """

        # Initialize logger
        self.logger = Logger(name="Sensor({})".format(name), dunder_name=__name__)

        # Initialize name and simulation status
        self.name = name
        self.simulate = simulate
        self.directory = directory

        # Initialize driver
        self.driver = USBCameraDriver(
            name=name,
            vendor_id=vendor_id,
            product_id=product_id,
            resolution=resolution,
            directory=directory,
            simulate=simulate,
            usb_mux_comms=usb_mux_comms,
            usb_mux_channel=usb_mux_channel,
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
            error.report("Sensor probe failed")
            self.logger.error(error.latest())
            self.health = 0.0
            return error

        # Successfully probed!
        self.logger.info("Probe successful!")
        return Error(None)

    def capture(self) -> Error:
        """ Captures an image. """
        # self.logger.debug("Capturing image")

        # Capture image
        error = self.driver.capture()

        # Check for errors
        if error.exists():
            error.report("Sensor unable to capture image")
            self.logger.error(error.latest())
            self.health = 0.0
            return error

        # Capture successful!
        return Error(None)

    def reset(self) -> None:
        """ Resets camera. """
        self.health = 100.0
