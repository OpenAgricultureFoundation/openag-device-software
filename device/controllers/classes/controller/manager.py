# Import standard python modules
import json, time

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import state machine parent class
from device.utilities.statemachine import manager, modes

# Import device utilities
from device.utilities import logger
from device.utilities.statemachine.manager import StateMachineManager
from device.utilities.state.main import State

# Import manager elements
from device.controllers.classes.controller import modes


class ControllerManager(StateMachineManager):
    """Manages all controllers."""

    # Initialize timing variables
    default_sampling_interval = 5  # seconds
    last_update = None  # seconds
    last_update_interval = None  # Seconds

    def __init__(self, name: str, state: State, config: Dict) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__()

        # Initialize passed in parameters
        self.name = name
        self.state = state
        self.config = config

        # Initialize logger
        logname = "Manager({})".format(self.name)
        self.logger = logger.Logger(logname, "controllers")

        # Load config parameters
        self.parameters = self.config.get("parameters", {})
        self.variables = self.parameters.get("variables", {})
        self.communication = self.parameters.get("communication", {})

        # Enforce communication to be empty dict if none
        if self.communication == None:
            self.communication = {}

        # Load setup dict and uuid
        self.setup_dict = self.load_setup_dict_from_file()
        self.setup_uuid = self.setup_dict.get("uuid", None)

        # Pull out setup properties if they exist
        self.properties = self.setup_dict.get("properties", {})

        # Initialize state machine transitions
        self.transitions = {
            modes.INIT: [modes.NORMAL, modes.ERROR, modes.SHUTDOWN],
            modes.NORMAL: [modes.RESET, modes.ERROR, modes.SHUTDOWN],
            modes.RESET: [modes.INIT, modes.ERROR, modes.SHUTDOWN],
            modes.ERROR: [modes.RESET, modes.SHUTDOWN],
        }

        # Initialize state machine mode
        self.mode = modes.INIT

    @property
    def mode(self) -> str:
        """Gets mode value."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Safely updates controller mode in device state object."""
        self._mode = value
        self.state.set_controller_value(self.name, "mode", value)

    @property
    def setup_uuid(self) -> Optional[str]:
        """Gets setup uuid from shared state object."""
        value = self.state.get_controller_value(self.name, "setup_uuid")
        if value != None:
            return str(value)
        return None

    @setup_uuid.setter
    def setup_uuid(self, value: str) -> None:
        """Safely updates setup uuid in state object."""
        self.state.set_controller_value(self.name, "setup_uuid", value)

    @property
    def sampling_interval(self) -> float:
        """Gets sampling interval from shared state object."""

        # Get stored sampling interval
        controller_state = self.state.controllers.get(self.name, {})
        stored = controller_state.get("stored", {})
        stored_sampling_interval = stored.get("sampling_interval", None)

        # Check if stored sampling interval exists
        if stored_sampling_interval != None:
            return float(stored_sampling_interval)

        # Otherwise set sampling interval seconds to default value and return
        self.sampling_interval = self.default_sampling_interval
        return self.default_sampling_interval

    @sampling_interval.setter
    def sampling_interval(self, value: float) -> None:
        """Safely updates sampling interval in state object."""
        with self.state.lock:
            if "stored" not in self.state.controllers[self.name]:
                self.state.controllers[self.name]["stored"] = {}
            self.state.controllers[self.name]["stored"]["sampling_interval"] = value

    ##### STATE MACHINE FUNCTIONS #############################################

    def run(self) -> None:
        """Runs controller state machine."""

        # Loop forever
        while True:

            # Check if thread is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == modes.INIT:
                self.run_init_mode()
            elif self.mode == modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == modes.RESET:
                self.run_reset_mode()
            elif self.mode == modes.ERROR:
                self.run_error_mode()
            elif self.mode == modes.SHUTDOWN:
                self.run_shutdown_mode()
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = modes.INVALID
                self.is_shutdown = True
                break

    def run_init_mode(self) -> None:
        """Runs init mode. Executes child class initialize function, checks for
        any resulting transitions (e.g. errors) then transitions to setup mode
        on the next state machine update."""
        self.logger.info("Entered INIT")

        # Initialize controller
        self.initialize_controller()

        # Check for transitions
        if self.new_transition(modes.INIT):
            return

        # Transition to normal mode on next state machine update
        self.mode = modes.NORMAL

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
            if self.sampling_interval < self.last_update_interval:
                message = "Updating controller, delta: {:.3f}".format(
                    self.last_update_interval
                )
                self.logger.debug(message)
                self.last_update = time.time()
                self.update_controller()

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

    def run_error_mode(self) -> None:
        """Runs error mode. Clears reported values then waits for new 
        events and transitions. Tries to reset every hour."""
        self.logger.info("Entered ERROR")

        # Clear reported values
        self.clear_reported_values()

        # Initialize vars
        start_time = time.time()

        # Loop forever
        while True:

            # Check for hourly reset
            if time.time() - start_time > 3600:  # 1 hour
                self.mode = modes.RESET
                break

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.ERROR):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_reset_mode(self) -> None:
        """Runs reset mode. Executes child class reset function, checks for any
        resulting transitions (e.g. errors) then transitions to init mode."""
        self.logger.info("Entered RESET")

        # Reset controller
        self.reset_controller()

        # Check for transitions
        if self.new_transition(modes.RESET):
            return

        # Transition to init on next state machine update
        self.mode = modes.INIT

    def run_shutdown_mode(self) -> None:
        """Runs shutdown mode. Executes child class shutdown function then
        waits for new events and transitions. Logs shutdown state every update
        interval."""
        self.logger.info("Entered SHUTDOWN")

        # Shutdown controller
        self.shutdown_controller()
        self.is_shutdown = True

    ##### HELPER FUNCTIONS ####################################################

    def load_setup_dict_from_file(self) -> Dict:
        """Loads setup dict from setup filename parameter."""
        self.logger.debug("Loading setup file")
        setup = self.parameters.get("setup", None)
        if setup == None:
            return {}
        file_name = setup["file_name"]
        setup_dict = json.load(
            open("device/controllers/modules/" + file_name + ".json")
        )
        return dict(setup_dict)

    def initialize_controller(self) -> None:
        """Initializes controller."""
        self.logger.debug("No initialization required.")

    def update_controller(self) -> None:
        """Updates controller."""
        self.logger.debug("No update required")

    def reset_controller(self) -> None:
        """ Resets controller. """
        self.logger.info("Resetting")
        self.clear_reported_values()

    def shutdown_controller(self) -> None:
        """ Shuts down controller. """
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.logger.debug("No values to clear")
