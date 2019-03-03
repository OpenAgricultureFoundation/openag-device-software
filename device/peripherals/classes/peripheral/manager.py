# Import python modules
import os, logging, time, threading, math, json

# Import python types
from typing import Dict, Optional, List, Any, Tuple

# Import device utilities
from device.utilities import logger
from device.utilities.statemachine.manager import StateMachineManager
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.state.main import State

# Import manager elements
from device.peripherals.classes.peripheral import modes, events


class PeripheralManager(StateMachineManager):
    """Parent class for peripheral devices e.g. sensors and actuators."""

    # Initialize timing variables
    default_sampling_interval = 5  # seconds
    min_sampling_interval = 2  # seconds
    last_update = None  # seconds
    last_update_interval = None  # Seconds

    def __init__(
        self,
        name: str,
        state: State,
        config: Dict,
        i2c_lock: threading.RLock,
        simulate: bool = False,
        mux_simulator: MuxSimulator = None,
    ) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__()

        # Initialize passed in parameters
        self.name = name
        self.state = state
        self.config = config
        self.i2c_lock = i2c_lock
        self.simulate = simulate
        self.mux_simulator = mux_simulator

        # Initialize logger
        logname = "Manager({})".format(self.name)
        self.logger = logger.Logger(logname, "peripherals")

        # Load config parameters
        self.parameters = self.config.get("parameters", {})
        self.variables = self.parameters.get("variables", {})
        self.communication = self.parameters.get("communication", {})

        # Enfore communication to be empty dict if none
        if self.communication == None:
            self.communication = {}

        # Get standard i2c config parameters if they exist
        self.bus = self.communication.get("bus")
        self.address = self.communication.get("address")
        self.mux = self.communication.get("mux")
        self.channel = self.communication.get("channel")

        # Check if using default bus
        if self.bus == "default":
            self.logger.debug("Using default i2c bus")
            self.bus = os.getenv("DEFAULT_I2C_BUS")

        # Convert exported value from non-pythonic none to pythonic None
        if self.bus == "none":
            self.bus = None

        if self.bus != None:
            self.bus = int(self.bus)  # type: ignore

        # Check if using default mux
        if self.mux == "default":
            self.logger.debug("mux is default")
            self.mux = os.getenv("DEFAULT_MUX_ADDRESS")

        # Convert exported value from non-pythonic none to pythonic None
        if self.mux == "none":
            self.mux = None
        self.logger.debug("mux = {}".format(self.mux))

        # Convert i2c config params from hex to int if they exist
        if self.address != None:
            self.address = int(self.address, 16)
        if self.mux != None:
            self.mux = int(self.mux, 16)

        # Load setup dict and uuid
        self.setup_dict = self.load_setup_dict_from_file()
        self.setup_uuid = self.setup_dict.get("uuid", None)

        # Pull out setup properties if they exist
        self.properties = self.setup_dict.get("properties", {})

        # Initialize state machine transitions
        self.transitions = {
            modes.INIT: [modes.SETUP, modes.ERROR, modes.SHUTDOWN],
            modes.SETUP: [modes.NORMAL, modes.ERROR, modes.SHUTDOWN],
            modes.NORMAL: [
                modes.CALIBRATE,
                modes.MANUAL,
                modes.RESET,
                modes.ERROR,
                modes.SHUTDOWN,
            ],
            modes.MANUAL: [
                modes.NORMAL,
                modes.CALIBRATE,
                modes.RESET,
                modes.ERROR,
                modes.SHUTDOWN,
            ],
            modes.CALIBRATE: [modes.RESET, modes.ERROR, modes.SHUTDOWN],
            modes.RESET: [modes.INIT, modes.ERROR, modes.SHUTDOWN],
            modes.ERROR: [modes.RESET, modes.SHUTDOWN],
        }

        # Initialize state machine mode
        self.mode = modes.INIT

    @property
    def health(self) -> Optional[float]:
        """Gets health value."""
        value = self.state.get_peripheral_value(self.name, "health")
        if value != None:
            return float(value)
        return None

    @health.setter
    def health(self, value: float) -> None:
        """Sets health value in shared state."""
        self.state.set_peripheral_value(self.name, "health", round(value, 2))

    @property
    def mode(self) -> str:
        """Gets mode value."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Safely updates peripheral mode in device state object."""
        self._mode = value
        self.state.set_peripheral_value(self.name, "mode", value)

    @property
    def setup_uuid(self) -> Optional[str]:
        """Gets setup uuid from shared state object."""
        value = self.state.get_peripheral_value(self.name, "setup_uuid")
        if value != None:
            return str(value)
        return None

    @setup_uuid.setter
    def setup_uuid(self, value: str) -> None:
        """Safely updates setup uuid in state object."""
        self.state.set_peripheral_value(self.name, "setup_uuid", value)

    @property
    def sampling_interval(self) -> float:
        """Gets sampling interval from shared state object."""

        # Get stored sampling interval
        peripheral_state = self.state.peripherals.get(self.name, {})
        stored = peripheral_state.get("stored", {})
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
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            self.state.peripherals[self.name]["stored"]["sampling_interval"] = value

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs peripheral state machine."""

        # Loop forever
        while True:

            # Check if thread is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == modes.INIT:
                self.run_init_mode()
            elif self.mode == modes.SETUP:
                self.run_setup_mode()
            elif self.mode == modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == modes.CALIBRATE:
                self.run_calibrate_mode()
            elif self.mode == modes.MANUAL:
                self.run_manual_mode()
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
        """Runs init mode. Executes child class initialize function, checks for any 
        resulting transitions (e.g. errors) then transitions to setup mode on the 
        next state machine update."""
        self.logger.info("Entered INIT")

        # Initialize peripheral
        self.initialize_peripheral()

        # Check for transitions
        if self.new_transition(modes.INIT):
            return

        # Transition to setup mode on next state machine update
        self.mode = modes.SETUP

    def run_setup_mode(self) -> None:
        """Runs setup mode. Executes child class setup function, checks for any
        resulting transitions (e.g. errors) then transitions to normal mode on the
        next state machine update."""
        self.logger.info("Entered SETUP")

        # Setup peripheral
        self.setup_peripheral()

        # Check for transitions
        if self.new_transition(modes.SETUP):
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

    def run_calibrate_mode(self) -> None:
        """Runs calibrate mode. Performs same function as normal mode except for 
        variable reporting functions only update peripheral state instead of both 
        peripheral and environment."""
        self.logger.info("Entered CALIBRATE")

        # Initialize vars
        self._update_complete = True
        self.last_update = time.time() - self.sampling_interval

        # Loop forever
        while True:

            # Update every sampling interval
            self.last_update_interval = time.time() - self.last_update
            if self.sampling_interval < self.last_update_interval:
                self.logger.debug(
                    "Updating peripheral, time delta: {:.3f} sec".format(
                        self.last_update_interval
                    )
                )
                self.last_update = time.time()
                self.update_peripheral()

            # Check for transitions
            if self.new_transition(modes.CALIBRATE):
                break

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.CALIBRATE):
                break

            # Update every 100ms
            time.sleep(0.100)

    def run_manual_mode(self) -> None:
        """Runs manual mode. Waits for events and transitions."""
        self.logger.info("Entered MANUAL")

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.MANUAL):
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

        # Reset peripheral
        self.reset_peripheral()

        # Check for transitions
        if self.new_transition(modes.RESET):
            return

        # Transition to init on next state machine update
        self.mode = modes.INIT

    def run_shutdown_mode(self) -> None:
        """Runs shutdown mode. Executes child class shutdown function then waits for 
        new events and transitions. Logs shutdown state every update interval."""
        self.logger.info("Entered SHUTDOWN")

        # Shutdown peripheral
        self.shutdown_peripheral()
        self.is_shutdown = True

    ##### HELPER FUNCTIONS #############################################################

    def load_setup_dict_from_file(self) -> Dict:
        """Loads setup dict from setup filename parameter."""
        self.logger.debug("Loading setup file")
        file_name = self.parameters["setup"]["file_name"]
        setup_dict = json.load(
            open("device/peripherals/modules/" + file_name + ".json")
        )
        return dict(setup_dict)

    def initialize_peripheral(self) -> None:
        """Initializes peripheral."""
        self.logger.debug("No initialization required.")

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("No setup required")

    def update_peripheral(self) -> None:
        """Updates peripheral."""
        self.logger.debug("No update required")

    def reset_peripheral(self) -> None:
        """ Resets peripheral. """
        self.logger.info("Resetting")
        self.clear_reported_values()

    def shutdown_peripheral(self) -> None:
        """ Shuts down peripheral. """
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.logger.debug("No values to clear")

    ##### EVENT FUNCTIONS ##############################################################

    def create_event(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Creates a new event, checks for matching event type, pre-processes request, 
        then adds to event queue."""
        self.logger.debug("Creating event request: `{}`".format(request))

        # Get request parameters
        try:
            type_ = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400

        # Process general event requests
        if type_ == events.RESET:
            return self.reset()  # defined in parent class
        elif type_ == events.SHUTDOWN:
            return self.shutdown()  # defined in parent class
        elif type_ == events.SET_SAMPLING_INTERVAL:
            return self.set_sampling_interval(request)
        elif type_ == events.ENABLE_CALIBRATION_MODE:
            return self.enable_calibration_mode()
        elif type_ == events.ENABLE_MANUAL_MODE:
            return self.enable_manual_mode()
        else:
            return self.create_peripheral_specific_event(request)

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event. This method should be 
        overridden in child class."""
        return "Unknown event request type", 400

    def check_events(self) -> None:
        """Checks for a new event. Only processes one event per call, even if there are 
        multiple in the queue. Events are processed first-in-first-out (FIFO)."""

        # Check for new events
        if self.event_queue.empty():
            return

        # Get request
        request = self.event_queue.get()
        self.logger.debug("Received new request: {}".format(request))

        # Get request parameters
        try:
            type_ = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.exception(message)
            return

        # Execute request
        if type_ == events.RESET:
            self._reset()  # defined in parent class
        elif type_ == events.SHUTDOWN:
            self._shutdown()  # defined in parent class
        elif type_ == events.SET_SAMPLING_INTERVAL:
            self._set_sampling_interval(request)
        elif type_ == events.ENABLE_CALIBRATION_MODE:
            self._enable_calibration_mode()
        elif type_ == events.ENABLE_MANUAL_MODE:
            self._enable_manual_mode()
        else:
            self.check_peripheral_specific_events(request)

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events. This method should be 
        overwritten in child class."""
        type_ = request.get("type")
        self.logger.error("Invalid event request type in queue: {}".format(type_))

    def set_sampling_interval(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes set sampling interval event request."""
        self.logger.debug("Pre-processing set sampling interval event request")

        # Verify value in request
        try:
            value = request["value"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400

        # Safely get desired sampling interval
        try:
            interval = float(value)
        except ValueError:
            message = "Invalid sampling interval value"
            self.logger.debug(message)
            return message, 400

        # Check desired sampling interval larger than min interval
        msi = self.min_sampling_interval
        if interval < msi:
            message = "Unable to set sampling interval below {} seconds.".format(msi)
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.SET_SAMPLING_INTERVAL, "interval": interval}
        self.event_queue.put(request)

        # Return event response
        return "Setting sampling interval", 200

    def _set_sampling_interval(self, request: Dict[str, Any]) -> None:
        """Processes set sampling interval event request."""
        self.logger.debug("Processing set sampling interval event request")

        # Set sampling interval
        interval = request.get("interval")
        self.sampling_interval = float(interval)  # type: ignore

    def enable_calibration_mode(self) -> Tuple[str, int]:
        """Pre-processes enable calibration mode event request."""
        self.logger.debug("Pre-processing enable calibration mode event request")

        # Check if sensor alread in calibration mode
        if self.mode == modes.CALIBRATE:
            message = "Already in calibration mode"
            self.logger.debug(message)
            return message, 200

        # Check valid transition
        if not self.valid_transition(self.mode, modes.CALIBRATE):
            message = "Unable to enable calibration mode from {} mode".format(self.mode)
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.ENABLE_CALIBRATION_MODE}
        self.event_queue.put(request)

        # Return response
        return "Enabling calibration mode", 200

    def _enable_calibration_mode(self) -> None:
        """Processes enable calibration mode event request."""
        self.logger.debug("Processing enable calibration mode event request")

        # Check valid transitions
        if not self.valid_transition(self.mode, modes.CALIBRATE):
            message = "Tried to enable calibration mode from {}".format(self.mode)
            self.logger.critical(message)
            return

        # Transition to calibration mode on next state machine update
        self.mode = modes.CALIBRATE

    def enable_manual_mode(self) -> Tuple[str, int]:
        """Pre-processes enable manual mode event request."""
        self.logger.debug("Pre-processing enable manual mode event request")

        # Check if sensor alread in manual mode
        if self.mode == modes.MANUAL:
            message = "Already in manual mode"
            self.logger.debug(message)
            return message, 200

        # Check valid transition
        if not self.valid_transition(self.mode, modes.MANUAL):
            message = "Unable to enable manual mode from {} mode".format(self.mode)
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.ENABLE_MANUAL_MODE}
        self.event_queue.put(request)

        # Return response
        return "Enabling manual mode", 200

    def _enable_manual_mode(self) -> None:
        """Processes enable manual mode event request."""
        self.logger.debug("Processing enable manual mode event request")

        # Check peripheral is in acceptible mode
        if not self.valid_transition(self.mode, modes.MANUAL):
            message = "Unable to enable manual mode from {} mode".format(self.mode)
            self.logger.critical(message)
            return

        # Transition to manual mode on next state machine update
        self.mode = modes.MANUAL
