# Import standard python modules
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.health import Health
from device.utilities.error import Error

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import led array and events
from device.peripherals.modules.elp_usb500w02ml21.camera import ELPUSB500W02ML21Camera
from device.peripherals.modules.elp_usb500w02ml21.events import ELPUSB500W02ML21Events


class ELPUSB500W02ML21(PeripheralManager, ELPUSB500W02ML21Events):
    """ Manages an ELP USB500W02M-L21 camera. """

    def __init__(self, *args, **kwargs):
        """ Instantiates manager Instantiates parent class, and initializes 
            camera variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize camera
        self.camera = ELPUSB500W02ML21Camera(
            name = self.name, 
            directory = self.parameters["directory"],
            simulate = self.simulate,
        )

        # Default to taking an image every hour
        self._min_sampling_interval_seconds = 120
        self._default_sampling_interval_seconds = 1800 # 3600


    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.info("Initializing")


        # Initialize health
        self.health = 100

        # Initialize camera
        error = self.camera.probe()

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
        error = self.camera.capture()

        # Check for errors:
        if error.exists():
            error.report("Manager unable to update")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            self.health = self.camera.health
            return

        # Update reported values
        self.health = self.camera.health
        
        
    def reset(self) -> None:
        """ Resets camera. """
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

        # Reset camera
        self.camera.reset()

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
