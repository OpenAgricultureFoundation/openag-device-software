# Import standard python modules
import json

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities import logger, accessors

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.modules.usb_camera import driver, exceptions


class USBCameraManager(manager.PeripheralManager):  # type: ignore
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
        self.min_sampling_interval = 120  # seconds
        self.default_sampling_interval = 3600  # every hour

    def initialize_peripheral(self) -> None:
        """ Initializes peripheral."""
        self.logger.debug("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.USBCameraDriver(
                name=self.name,
                vendor_id=int(self.properties.get("vendor_id"), 16),
                product_id=int(self.properties.get("product_id"), 16),
                resolution=self.properties.get("resolution"),
                num_cameras=self.properties.get("num_cameras", 1),
                usb_mux_comms=self.usb_mux_comms,
                usb_mux_channel=self.usb_mux_channel,
                i2c_lock=self.i2c_lock,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except exceptions.DriverError as e:
            self.logger.debug("Unable to initialize: {}".format(e))
            self.health = 0.0
            self.mode = modes.ERROR

    def update_peripheral(self) -> None:
        """Updates peripheral, captures an image."""
        try:
            self.driver.capture()
            self.health = 100.0
        except exceptions.DriverError as e:
            self.logger.debug("Unable to update: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0
