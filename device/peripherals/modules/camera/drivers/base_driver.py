from abc import ABC, abstractmethod

import threading, os

from typing import Optional, Tuple, Dict, Any, List

from device.utilities import logger
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

from django.conf import settings


class CameraDriver(ABC):

    @abstractmethod
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

        # universal paths
        self.IMAGE_DIR = settings.DATA_PATH + "/images/"
        self.MODULE_DIR = "device/peripherals/modules/usb_camera/"
        self.SIMULATE_IMAGE_DIR = self.MODULE_DIR + "tests/images/"
        self.DUMMY_IMAGE_PATH = self.MODULE_DIR + "dummy.png"
        self.ACTIVE_IMAGE_PATH = self.MODULE_DIR + "active.png"
        self.SIMULATION_IMAGE_PATH = self.MODULE_DIR + "tests/simulation_image.png"

        # Initialize parameters
        self.name = name
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.resolution = resolution
        self.num_cameras = num_cameras
        self.simulate = simulate
        self.usb_mux_enabled = True

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")

        # Check if simulating
        if self.simulate:
            self.logger.info("Simulating driver")
            # image uploads needs images in the usual spot, just like a real one.
            #self.directory = self.SIMULATE_IMAGE_DIR
            self.directory = self.IMAGE_DIR
            self.usb_mux_enabled = False
        else:
            self.directory = self.IMAGE_DIR

            # Check directory exists else create it
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)

            # Check if using usb mux
            if usb_mux_comms is None \
                    or usb_mux_channel is None:
                self.usb_mux_enabled = False
                return

            # Initialize usb mux properties
            self.bus = usb_mux_comms.get("bus")
            self.mux = usb_mux_comms.get("mux")
            self.channel = usb_mux_comms.get("channel")
            self.address = usb_mux_comms.get("address")

            # Check if using default bus
            if self.bus == "default":
                self.logger.debug("Using default i2c bus")
                self.bus = os.getenv("DEFAULT_I2C_BUS")

                # Convert exported value from non-pythonic none to pythonic None
                if self.bus == "none":
                    self.bus = None

                if self.bus is not None:
                    self.bus = int(self.bus)

            # Check if using default mux
            if self.mux == "default":
                self.logger.debug("mux is default")
                self.mux = os.getenv("DEFAULT_MUX_ADDRESS")

                # Convert exported value from non-pythonic none to pythonic None
                if self.mux == "none":
                    self.mux = None
                self.logger.debug("mux = {}".format(self.mux))

            # Convert i2c config params from hex to int if they exist
            if self.address is not None:
                address = int(self.address, 16)
            if self.mux is not None:
                self.mux = int(self.mux, 16)

    @abstractmethod
    def capture(self, retry: bool = True) -> None:
        """Captures an image from a camera or set of non-unique cameras."""
        self.logger.debug("Capturing")
        return

    def _simulate_capture(self, filename: str) -> bool:
        # Check if simulated
        if self.simulate:
            message = "Simulating capture, saving image to: {}".format(filename)
            self.logger.info(message)
            command = "cp {} {}".format(self.SIMULATION_IMAGE_PATH, filename)
            os.system(command)
            return True
        return False

