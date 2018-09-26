# Import python modules
import logging, time, threading, math, json

# Import python types
from typing import Dict, Optional, List

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.modes import Modes
from device.utilities.statemachine import Manager, Transitions

# Import device comms
from device.communication.i2c.mux_simulator import MuxSimulator

# Import device state
from device.state.main import State

# Import peripheral modules
from device.peripherals.classes.peripheral.events import PeripheralEvents

# Define state machine transitions table
TRANSITION_TABLE = {
    Modes.INIT: [Modes.SETUP, Modes.SHUTDOWN, Modes.ERROR],
    Modes.SETUP: [Modes.NORMAL, Modes.SHUTDOWN, Modes.ERROR],
    Modes.NORMAL: [
        Modes.CALIBRATE,
        Modes.MANUAL,
        Modes.RESET,
        Modes.SHUTDOWN,
        Modes.ERROR,
    ],
    Modes.MANUAL: [
        Modes.NORMAL,
        Modes.CALIBRATE,
        Modes.RESET,
        Modes.SHUTDOWN,
        Modes.ERROR,
    ],
    Modes.CALIBRATE: [Modes.RESET, Modes.SHUTDOWN, Modes.ERROR],
    Modes.ERROR: [Modes.RESET, Modes.SHUTDOWN],
    Modes.SHUTDOWN: [Modes.RESET],
    Modes.RESET: [Modes.INIT],
}


class PeripheralManager(Manager):  # type: ignore
    """Parent class for peripheral devices e.g. sensors and actuators."""

    # Initialize peripheral mode and error
    _mode = None
    _error = None

    # Initialize thread terminator
    thread_is_active = True

    # Initialize timing variabless
    default_sampling_interval = 5  # seconds
    min_sampling_interval = 2  # seconds
    last_update = None  # seconds
    last_update_interval = None  # Seconds

    def __init__(
        self,
        name: str,
        state: State,
        config: Dict,
        i2c_lock: threading.Lock,
        simulate: bool = False,
        mux_simulator: MuxSimulator = None,
    ) -> None:
        """Initializes manager."""

        # Initialize passed in parameters
        self.name = name
        self.state = state
        self.config = config
        self.i2c_lock = i2c_lock
        self.simulate = simulate
        self.mux_simulator = mux_simulator

        # Initialize logger
        logname = "Manager({})".format(self.name)
        extra = {"console_name": logname, "file_name": logname}
        logger = logging.getLogger("peripherals")
        self.logger = logging.LoggerAdapter(logger, extra)

        # Initialize transitions
        self.transitions = Transitions(self, TRANSITION_TABLE)

        # Initialize events
        self.events = PeripheralEvents(self)

        # Initialize modes and errors
        self.mode = Modes.INIT
        self.error = "None"

        # Load config parameters
        self.parameters = self.config["parameters"]
        self.variables = self.parameters.get("variables", {})
        self.communication = self.parameters.get("communication", {})

        # Ensure communication is a dict
        if self.communication == None:
            self.communication = {}

        # Get standard i2c config parameters if they exist
        self.bus = self.communication.get("bus", None)
        self.address = self.communication.get("address", None)
        self.mux = self.communication.get("mux", None)
        self.channel = self.communication.get("channel", None)

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

    # TODO: Use state functions on remaining properties

    @property
    def mode(self) -> Optional[str]:
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

    def spawn(self) -> None:
        """Spawns peripheral thread."""
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()

    def run_state_machine(self) -> None:
        """Runs peripheral state machine."""
        while self.thread_is_active:
            if self.mode == Modes.INIT:
                self.run_init_mode()
            elif self.mode == Modes.SETUP:
                self.run_setup_mode()
            elif self.mode == Modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == Modes.ERROR:
                self.run_error_mode()
            elif self.mode == Modes.CALIBRATE:
                self.run_calibrate_mode()
            elif self.mode == Modes.MANUAL:
                self.run_manual_mode()
            elif self.mode == Modes.RESET:
                self.run_reset_mode()
            elif self.mode == Modes.SHUTDOWN:
                self.run_shutdown_mode()
            else:
                self.error = "Invalid mode"
                self.logger.critical(self.error)

    def run_init_mode(self) -> None:
        """Runs init mode. Executes child class initialize function, checks for any 
        resulting transitions (e.g. errors) then transitions to setup mode on the 
        next state machine update."""
        self.logger.info("Entered Modes.INIT")

        # Initialize peripheral
        self.initialize()

        # Check for transitions
        if self.transitions.is_new(Modes.INIT):
            return

        # Transition to setup mode on next state machine update
        self.mode = Modes.SETUP

    def run_setup_mode(self) -> None:
        """Runs setup mode. Executes child class setup function, checks for any
        resulting transitions (e.g. errors) then transitions to normal mode on the
        next state machine update."""
        self.logger.info("Entered Modes.SETUP")

        # Setup peripheral
        self.setup()

        # Check for transitions
        if self.transitions.is_new(Modes.SETUP):
            return

        # Transition to normal mode on next state machine update
        self.mode = Modes.NORMAL

    def run_normal_mode(self) -> None:
        """Runs normal mode. Executes child class update function every sampling
        interval. Checks for events and transitions after each update."""
        self.logger.info("Entered Modes.NORMAL")

        # Initialize vars
        self._update_complete = True
        self.last_update = time.time()

        # Loop until shutdown
        while self.thread_is_active:

            # Update every sampling interval
            self.last_update_interval = time.time() - self.last_update
            if self.sampling_interval < self.last_update_interval:
                message = "Updating peripheral, delta: {:.3f}".format(
                    self.last_update_interval
                )
                self.logger.debug(message)
                self.last_update = time.time()
                self.update()

            # Check for transitions
            if self.transitions.is_new(Modes.NORMAL):
                break

            # Check for events
            self.events.check()

            # Check for transitions
            if self.transitions.is_new(Modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.100)

    def run_calibrate_mode(self) -> None:
        """Runs calibrate mode. Performs same function as normal mode except for 
        variable reporting functions only update peripheral state instead of both 
        peripheral and environment."""
        self.logger.info("Entered Modes.CALIBRATE")

        # Initialize vars
        self._update_complete = True
        self.last_update = time.time() - self.sampling_interval

        # Loop until shutdown
        while self.thread_is_active:

            # Update every sampling interval
            self.last_update_interval = time.time() - self.last_update
            if self.sampling_interval < self.last_update_interval:
                self.logger.debug(
                    "Updating peripheral, time delta: {:.3f} sec".format(
                        self.last_update_interval
                    )
                )
                self.last_update = time.time()
                self.update()

            # Check for transitions
            if self.transitions.is_new(Modes.CALIBRATE):
                break

            # Check for events
            self.events.check()

            # Check for transitions
            if self.transitions.is_new(Modes.CALIBRATE):
                break

            # Update every 100ms
            time.sleep(0.100)

    def run_manual_mode(self) -> None:
        """Runs manual mode. Waits for events and transitions."""
        self.logger.info("Entered Modes.MANUAL")

        # Loop until thread is shutdown
        while self.thread_is_active:

            # Check for events
            self.events.check()

            # Check for transitions
            if self.transitions.is_new(Modes.MANUAL):
                break

            # Update every 100ms
            time.sleep(0.100)

    def run_error_mode(self) -> None:
        """Runs error mode. Clears reported values then waits for new 
        events and transitions. Tries to reset every hour."""
        self.logger.info("Entered Modes.ERROR")

        # Clear reported values
        self.clear_reported_values()

        # Initialize vars
        start_time = time.time()

        # Loop until thread is shutdown
        while self.thread_is_active:

            # Check for hourly reset
            if time.time() - start_time > 3600:  # 1 hour
                self.mode = Modes.RESET
                break

            # Check for events
            self.events.check()

            # Check for transitions
            if self.transitions.is_new(Modes.ERROR):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_reset_mode(self) -> None:
        """Runs reset mode. Executes child class reset function, checks for any
        resulting transitions (e.g. errors) then transitions to init mode."""
        self.logger.info("Entered Modes.RESET")

        # Reset peripheral
        self.reset()

        # Check for transitions
        if self.transitions.is_new(Modes.RESET):
            return

        # Transition to init on next state machine update
        self.mode = Modes.INIT

    def run_shutdown_mode(self) -> None:
        """Runs shutdown mode. Executes child class shutdown function then waits for 
        new events and transitions. Logs shutdown state every update interval."""
        self.logger.info("Entered Modes.SHUTDOWN")

        # Shutdown peripheral
        self.shutdown()

        # Wait for command from device or user
        last_update = time.time() - self.sampling_interval
        while self.thread_is_active:

            # Log shutdown state every update interval
            last_update_interval = time.time() - last_update
            if self.sampling_interval < last_update_interval:
                self.logger.debug("Peripheral is shutdown, waiting for reset")
                last_update = time.time()

            # Check for events
            self.events.check()

            # Check for transitions
            if self.transitions.is_new(Modes.SHUTDOWN):
                break

            # Update every 100ms
            time.sleep(0.1)

    def load_setup_dict_from_file(self) -> Dict:
        """Loads setup dict from setup filename parameter."""
        self.logger.debug("Loading setup file")
        file_name = self.parameters["setup"]["file_name"]
        setup_dict = json.load(
            open("device/peripherals/modules/" + file_name + ".json")
        )
        return dict(setup_dict)

    def initialize(self) -> None:
        """Initializes peripheral. """
        self.logger.debug("No initialization required.")

    def setup(self) -> None:
        """Sets up peripheral. """
        self.logger.debug("No setup required")

    def update(self) -> None:
        """Updates peripheral."""
        self.logger.debug("No update required")

    def reset(self) -> None:
        """Resets peripheral."""
        self.logger.debug("No reset required")

    def shutdown(self) -> None:
        """Shutsdown peripheral."""
        self.logger.debug("No shutdown required")

    def clear_reported_values(self) -> None:
        """Clears reported values. Child class should overwrite."""
        self.logger.debug("No values to clear")
