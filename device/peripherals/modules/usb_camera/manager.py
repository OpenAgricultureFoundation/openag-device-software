# Import standard python modules
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.health import Health
from device.utilities.error import Error

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import led array and events
from device.peripherals.modules.usb_camera.sensor import USBCameraSensor
from device.peripherals.modules.usb_camera.events import USBCameraEvents


class USBCameraManager(PeripheralManager, USBCameraEvents):
    """ Manages a usb camera. """

    def __init__(self, *args, **kwargs):
        """ Instantiates manager Instantiates parent class, and initializes 
            camera variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize camera
        self.sensor = USBCameraSensor(
            name = self.name, 
            directory = self.parameters["directory"],
            vendor_id = int(self.setup_dict["properties"]["vendor_id"], 16),
            product_id = int(self.setup_dict["properties"]["product_id"], 16),
            resolution = self.setup_dict["properties"]["resolution"],
            simulate = self.simulate,
        )

        # Initialize sampling parameters
        self._min_sampling_interval_seconds = 120 # should never take more than 2 minutes to capture an image
        self._default_sampling_interval_seconds = 3600 # every hour


    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.info("Initializing")

        # Initialize health
        self.health = 100

        # Initialize camera
        error = self.sensor.probe()

        # Check for errors
        if error.exists():
            error.report("Manager unable to initialize")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            return

        # Successful initialization!
        self.logger.info("Initialized successfully")


    def setup(self) -> None:
        """ Sets up manager. Programs device operation parameters into 
            camera driver circuit. """
        self.logger.info("No setup required")


    def update(self) -> None:
        """ Updates camera when in normal mode. """

        # Capture image
        error = self.sensor.capture()

        # Check for errors:
        if error.exists():
            error.report("Manager unable to update")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            self.health = self.sensor.health
            return

        # Update reported values
        self.health = self.sensor.health
        
        
    def reset(self) -> None:
        """ Resets camera. """
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

        # Reset camera
        self.sensor.reset()

        # Sucessfully reset!
        self.logger.debug("Successfully reset!")


    def shutdown(self) -> None:
        """ Shuts down camera. """
        self.logger.info("Shutting down")

        # Clear reported values
        self.clear_reported_values()

        # Successfully shutdown
        self.logger.info("Successfully shutdown!")


    def clear_reported_values(self):
        """ Clears reported values. """
        ...
