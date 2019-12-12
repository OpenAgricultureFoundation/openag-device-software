# Import standard python modules
import abc
import json
import time

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities import logger, accessors

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.modules.camera import exceptions, events
from device.peripherals.modules.camera.drivers.base_driver import CameraDriver
from device.recipe import modes as recipe_modes


class CameraManager(manager.PeripheralManager):  # type: ignore
    """Manages a camera peripheral."""

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

        # Initialize light control parameters
        self.lighting_control = self.parameters.get("lighting_control", {})
        self.lighting_control_enabled = self.lighting_control.get("enabled", False)

        # Initialize recipe modes
        self.previous_recipe_mode = recipe_modes.NORECIPE

        self.logger.debug("Instantiating")

    @property
    def recipe_mode(self) -> str:
        """Gets recipe mode."""
        return self.state.recipe.get("mode", recipe_modes.NORECIPE)

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

            # TODO: Add simulation code
            if self.simulate:
                self.logger.debug("Simulating initialization")
                return

            # Create driver
            driver_module = (
                "device.peripherals.modules.camera.drivers."
                + self.parameters.get("driver_module")
            )
            driver_class = self.parameters.get("driver_class")
            self.logger.debug("Getting driver")
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
            self.logger.exception("Unable to initialize")
            self.health = 0.0
            self.mode = modes.ERROR
        except ModuleNotFoundError as e:
            self.logger.exception(
                "Unable to import module, assuming can't import picamera b/c not running on a raspberry pi"
            )
            self.health = 0.0
            self.mode = modes.ERROR

    def update_peripheral(self) -> None:
        """Updates peripheral, captures an image."""
        try:
            self.set_lighting_conditions()
            if self.simulate:
                self.logger.debug("Simulating capture")
            else:
                self.driver.capture()
            self.reset_lighting_conditions()
            self.health = 100.0
        except exceptions.DriverError as e:
            self.logger.debug("Unable to update: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0

    ##### OVERRIDE PARENT METHODS ######################################################

    def run_normal_mode(self) -> None:
        """Runs normal mode. Executes child class update function every sampling
        interval. Checks for events and transitions after each update."""
        self.logger.info("Entered NORMAL")

        # Initialize vars
        self._update_complete = True
        self.last_update = time.time()

        # Loop forever
        while True:

            # Update every sampling interval
            self.last_update_interval = time.time() - self.last_update
            if self.sampling_interval < self.last_update_interval or self.new_recipe():
                message = "Updating peripheral, delta: {:.3f}".format(
                    self.last_update_interval
                )
                self.logger.debug(message)
                self.last_update = time.time()
                self.update_peripheral()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.100)

    ##### HELPER FUNCTIONS #############################################################

    def new_recipe(self) -> bool:
        """Checks if a new recipe has been started."""
        if self.recipe_mode != self.previous_recipe_mode:
            self.previous_recipe_mode = self.recipe_mode
            if self.recipe_mode == recipe_modes.NORMAL:
                self.logger.debug("Started new recipe")
                return True
        # self.previous_recipe_mode = self.recipe_mode
        return False

    def set_lighting_conditions(self) -> None:
        """Sets light conditions to a flat white spectrum."""
        self.logger.debug("Setting lighting conditions")

        # Verify lighting control is enabled
        if not self.lighting_control_enabled:
            self.logger.debug("Lighting control is not enabled")
            return

        # Get lighting control parameters
        recipient_type = self.lighting_control.get("recipient_type")
        recipient_name = self.lighting_control.get("recipient_name")
        distance = self.lighting_control.get("distance")
        intensity = self.lighting_control.get("intensity")
        spectrum = self.lighting_control.get("spectrum")

        # Initialize event requests
        manual_mode_request = {"type": "Enable Manual Mode"}
        set_spd_request = {
            "type": "Set SPD",
            "distance": distance,
            "intensity": intensity,
            "spectrum": spectrum,
        }

        # Get manager
        if recipient_type == "Peripheral":
            manager = self.coordinator.peripherals.get(recipient_name)
        elif recipient_type == "Controller":
            manager = self.coordinator.controllers.get(recipient_name)
        else:
            return self.logger.error(f"Invalid recipient type: `{recipient_type}`")

        # Verify manager exists
        if manager == None:
            return self.logger.error(f"Invalid recipient name: `{recipient_name}`")

        # Wait up to a minute for light manager to enter normal mode
        # i.e. transition out of init/setup mode
        start_time = time.time()
        while manager.mode != "NORMAL":
            self.logger.debug("Waiting for light manager to enter normal mode")
            self.check_events()
            if self.new_transition(modes.NORMAL):
                return
            if time.time() - start_time > 60:
                return self.logger.warning(
                    "Light manager did not enter normal mode before timeout"
                )
            time.sleep(0.1)  # Update every 100 ms
        self.logger.debug("Light manager entered normal mode")

        # Put light manager in manual mode
        self.logger.debug("Sending light manager into manual mode")
        self.coordinator.send_event(recipient_type, recipient_name, manual_mode_request)

        # Wait up to a minute for light manager to enter manual mode
        start_time = time.time()
        while manager.mode != "MANUAL":
            self.logger.debug("Waiting for light manager to enter manual mode")
            self.check_events()
            if self.new_transition(modes.NORMAL):
                return
            if time.time() - start_time > 60:
                return self.logger.warning(
                    "Light manager did not enter manual mode before timeout"
                )
            time.sleep(0.1)  # Update every 100 ms
        self.logger.debug("Light manager entered manual mode")

        # Set light manager's spectral power distribution
        self.coordinator.send_event(recipient_type, recipient_name, set_spd_request)

        # Wait up to a minute for light manager's reported spd to update
        start_time = time.time()
        while (
            manager.desired_distance != distance
            and manager.desired_intensity != intensity
            and manager.desired_spectrum != spectrum
        ):
            self.logger.debug("Waiting for manager to update desired spd")
            self.check_events()
            if self.new_transition(modes.NORMAL):
                return
            if time.time() - start_time > 60:
                return self.logger.warning(
                    "Light manager did update desired spd before timeout"
                )
            time.sleep(0.1)  # Update every 100 ms
        self.logger.debug("Light manager updated desired spd")

        # Give light a few more seconds to stabilize
        time.sleep(3)

    def reset_lighting_conditions(self) -> None:
        """Resets light conditions to their previous state."""
        self.logger.debug("Resetting lighting conditions")

        # Verify lighting control is enabled
        if not self.lighting_control_enabled:
            self.logger.debug("Lighting control is not enabled")
            return

        # Get parameters
        recipient_type = self.lighting_control.get("recipient_type")
        recipient_name = self.lighting_control.get("recipient_name")

        # Initialize event request
        reset_mode_request = {"type": "Reset"}

        # Reset light manager
        self.coordinator.send_event(recipient_type, recipient_name, reset_mode_request)

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
            self.set_lighting_conditions()
            if self.simulate:
                self.logger.debug("Simulating capture")
            else:
                self.driver.capture()
            self.reset_lighting_conditions()

        except:
            self.mode = modes.ERROR
            message = "Unable to turn on, unhandled exception"
            self.logger.exception(message)

    @staticmethod
    def get_driver(module_name: str, class_name: str) -> abc.ABCMeta:
        module_instance = __import__(module_name, fromlist=[class_name])
        class_instance = getattr(module_instance, class_name)
        return class_instance
