# Import standard python modules
import json

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_nested_dict_safely

# Import peripheral parent class
from device.peripherals.classes.peripheral.manager import PeripheralManager
from device.peripherals.classes.peripheral.exceptions import DriverError

# Import driver modules
from device.peripherals.modules.usb_camera.events import USBCameraEvents
from device.peripherals.modules.usb_camera.driver import USBCameraDriver


class USBCameraManager(PeripheralManager, USBCameraEvents):  # type: ignore
    """Manages a usb camera."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Instantiates manager Instantiates parent class, and initializes 
        camera variable name."""

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Get usb mux parameters
        self.usb_mux_comms = self.communication.get("usb_mux_comms", None)
        self.usb_mux_channel = self.communication.get("usb_mux_channel", None)

        # Initialize sampling parameters
        self.min_sampling_interval_seconds = (120)
        self.default_sampling_interval_seconds = 3600  # every hour

    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.debug("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = USBCameraDriver(
                name=self.name,
                vendor_id=int(self.properties.get("vendor_id"), 16),
                product_id=int(self.properties.get("product_id"), 16),
                resolution=self.properties.get("resolution"),
                usb_mux_comms=self.usb_mux_comms,
                usb_mux_channel=self.usb_mux_channel,
                i2c_lock=self.i2c_lock,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except DriverError as e:
            self.logger.exception("Unable to initialize")
            self.health = 0.0
            self.mode = Modes.ERROR

    def setup(self) -> None:
        """Sets up manager."""
        self.logger.info("No setup required")

    def update(self) -> None:
        """Updates camera, captures an image."""
        try:
            self.driver.capture()
            self.health = 100.0
        except DriverError as e:
            self.logger.error("Unable to update")
            self.mode = Modes.ERROR
            self.health = 0

    def reset(self) -> None:
        """ Resets camera. """
        self.logger.info("Resetting")
        self.clear_reported_values()

    def shutdown(self) -> None:
        """ Shuts down camera. """
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        ...
