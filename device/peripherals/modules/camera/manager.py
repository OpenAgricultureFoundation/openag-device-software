# Import standard python modules
import abc
import json

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities import logger, accessors

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.modules.camera import exceptions, events

from device.peripherals.modules.camera.drivers.base_driver import CameraDriver


class CameraManager(manager.PeripheralManager):  # type: ignore
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

        self.logger.debug("Instantiating")

    def initialize_peripheral(self) -> None:
        """ Initializes peripheral."""
        self.logger.debug("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            # Initialize min sampling interval
            num_cameras = self.parameters.get("num_cameras", 1)
            self.min_sampling_interval = 120 * num_cameras
            self.logger.info(str(self.parameters.values()))

            # Create driver
            driver_module = "device.peripherals.modules.camera.drivers." + self.parameters.get("driver_module")
            driver_class = self.parameters.get("driver_class")
            self.driver = self.get_driver(driver_module, driver_class)(
                name=self.name,
                vendor_id=int(self.properties.get("vendor_id"), 16),
                product_id=int(self.properties.get("product_id"), 16),
                resolution=self.properties.get("resolution"),
                num_cameras=num_cameras,
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

    ##### EVENT FUNCTIONS ##############################################################

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == events.CAPTURE:
            return self.capture()
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == events.CAPTURE:
            self._capture()
        else:
            message = "Invalid event request type in queue: {}".format(request["type"])
            self.logger.error(message)

    def capture(self) -> Tuple[str, int]:
        """Pre-processes capture event request."""
        self.logger.debug("Pre-processing capture event request")

        # Add event request to event queue
        request = {"type": events.CAPTURE}
        self.event_queue.put(request)

        # Successfully turned on
        return "Capturing image, will take a few moments", 200

    def _capture(self) -> None:
        """Processes capture event request."""
        self.logger.debug("Processing capture event request")
        try:
            self.driver.capture()
        except:
            self.mode = modes.ERROR
            message = "Unable to turn on, unhandled exception"
            self.logger.exception(message)

    @staticmethod
    def get_driver(module_name: str, class_name: str) -> abc.ABCMeta:
        module_instance = __import__(module_name, fromlist=[class_name])
        class_instance = getattr(module_instance, class_name)
        return class_instance
