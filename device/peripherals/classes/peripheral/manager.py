# Import python modules
import logging, time, threading, math, json

# Import python types
from typing import Dict, Optional

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.logger import Logger

# Import device comms
from device.communication.i2c.mux_simulator import MuxSimulator

# Import device state
from device.state import State


class PeripheralManager:
    """ Parent class for peripheral devices e.g. sensors and actuators. """

    # Initialize peripheral mode and error
    _mode = None
    _error = None

    # Initialize thread terminator
    thread_is_active = True

    # Initialize timing variabless
    default_sampling_interval_seconds = 5
    min_sampling_interval_seconds = 2
    last_update_seconds = None
    last_update_interval_seconds = None

    def __init__(
        self,
        name: str,
        state: State,
        config: Dict,
        i2c_lock: threading.Lock,
        simulate: bool = False,
        mux_simulator: MuxSimulator = None,
    ) -> None:
        """ Initializes peripheral. """

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
        """ Gets health value. """
        value = self.state.get_peripheral_value(self.name, "health")
        if value != None:
            return float(value)
        return None

    @health.setter
    def health(self, value: float) -> None:
        """ Sets health value in shared state. """
        self.state.set_peripheral_value(self.name, "health", round(value, 2))

    # TODO: Use state functions on remaining properties

    @property
    def mode(self) -> Optional[str]:
        """ Gets mode value. """
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """ Safely updates peripheral mode in device state object. """
        self._mode = value
        self.state.set_peripheral_value(self.name, "mode", value)

    @property
    def commanded_mode(self) -> Optional[str]:
        """ Gets commanded mode from shared state object. """
        value = self.state.get_peripheral_value(self.name, "commanded_mode")
        if value != None:
            return str(value)
        return None

    @commanded_mode.setter
    def commanded_mode(self, value: str) -> None:
        """ Safely updates commanded mode in state object. """
        self.state.set_peripheral_value(self.name, "commanded_mode", value)

    @property
    def setup_uuid(self) -> Optional[str]:
        """ Gets setup uuid from shared state object. """
        value = self.state.get_peripheral_value(self.name, "setup_uuid")
        if value != None:
            return str(value)
        return None

    @setup_uuid.setter
    def setup_uuid(self, value: str) -> None:
        """ Safely updates setup uuid in state object. """
        self.state.set_peripheral_value(self.name, "setup_uuid", value)

    @property
    def sampling_interval_seconds(self) -> float:
        """ Gets sampling interval from shared state object. """

        # Get stored sampling interval
        peripheral_state = self.state.peripherals.get(self.name, {})
        stored = peripheral_state.get("stored", {})
        stored_sampling_interval = stored.get("sampling_interval_seconds", None)

        # Check if stored sampling interval exists
        if stored_sampling_interval != None:
            return float(stored_sampling_interval)

        # Otherwise set sampling interval seconds to default value and return
        self.sampling_interval_seconds = self.default_sampling_interval_seconds
        return self.default_sampling_interval_seconds

    @sampling_interval_seconds.setter
    def sampling_interval_seconds(self, value: float) -> None:
        """Safely updates sampling interval in state object."""
        with self.state.lock:
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            self.state.peripherals[self.name]["stored"][
                "sampling_interval_seconds"
            ] = value

    @property
    def request(self) -> Optional[Dict]:
        """ Gets request from shared state object. """
        value = self.state.get_peripheral_value(self.name, "request")
        if value != None:
            return dict(value)
        return None

    @request.setter
    def request(self, value: Optional[Dict]) -> None:
        """ Safely updates request in state object. """
        self.state.set_peripheral_value(self.name, "request", value)

    @property
    def response(self) -> Optional[Dict]:
        """ Gets response from shared state object. """
        value = self.state.get_peripheral_value(self.name, "response")
        if value != None:
            return dict(value)
        return None

    @response.setter
    def response(self, value: Dict) -> None:
        """ Safely updates request in state object. """
        self.state.set_peripheral_value(self.name, "response", value)

    def spawn(self) -> None:
        """ Spawns peripheral thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()

    def run_state_machine(self) -> None:
        """ Runs peripheral state machine. """
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
        """ Runs initialization mode. Initializes peripheral state then 
            transitions to SETUP. Transitions to ERROR on error. """
        self.logger.info("Entered INIT")

        # Initialize peripheral
        self.initialize()

        # Transition to SETUP if not ERROR
        if self.mode != Modes.ERROR:
            self.mode = Modes.SETUP

    def run_setup_mode(self) -> None:
        """ Runs setup mode. Sets up peripheral then transitions to NORMAL on 
            completion or ERROR on error. """
        self.logger.info("Entered SETUP")

        # Setup peripheral
        self.setup()

        # Transition to NORMAL if not ERROR
        if self.mode != Modes.ERROR:
            self.mode = Modes.NORMAL

    def run_normal_mode(self) -> None:
        """ Runs normal operation mode. Every sampling interval gets reported 
            sensor / actuator state, and sets desired actuator state. 
            Transitions to ERROR on error. """
        self.logger.info("Entered NORMAL")

        self._update_complete = True
        self.last_update_seconds = time.time()
        while self.thread_is_active:

            # Update every sampling interval
            self.last_update_interval_seconds = time.time() - self.last_update_seconds
            if self.sampling_interval_seconds < self.last_update_interval_seconds:
                self.logger.debug(
                    "Updating peripheral, delta: {:.3f}".format(
                        self.last_update_interval_seconds
                    )
                )
                self.last_update_seconds = time.time()
                self.update()

            # Check for update error
            if self.mode == Modes.ERROR:
                break

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)  # type: ignore

            # Check for state transition
            transition_modes = [
                Modes.CALIBRATE, Modes.MANUAL, Modes.RESET, Modes.SHUTDOWN, Modes.ERROR
            ]
            if self.mode in transition_modes:
                break

            # Update every 100ms
            time.sleep(0.100)

    def run_calibrate_mode(self) -> None:
        """ Runs calibrate mode. Currently just does the same thing as normal
            mode except variable reporting functions only update peripheral 
            state instead of both peripheral and environment. Transitions to 
            ERROR or NORMAL."""
        self.logger.info("Entered CALIBRATE")

        self._update_complete = True
        self.last_update_seconds = time.time() - self.sampling_interval_seconds
        while self.thread_is_active:

            # Update every sampling interval
            self.last_update_interval_seconds = time.time() - self.last_update_seconds
            if self.sampling_interval_seconds < self.last_update_interval_seconds:
                self.logger.debug(
                    "Updating peripheral, time delta: {:.3f} sec".format(
                        self.last_update_interval_seconds
                    )
                )
                self.last_update_seconds = time.time()
                self.update()

            # Check for transition to error or reset
            if self.mode == Modes.ERROR or self.mode == Modes.RESET:
                break

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)  # type: ignore

            # Update every 100ms
            time.sleep(0.100)

    def run_manual_mode(self) -> None:
        """ Runs manual mode. Waits for new events and checks for transition to
            normal, reset, shutdown, or error."""
        self.logger.info("Entered MANUAL")

        while self.thread_is_active:

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)  # type: ignore

            # Check for transition to normal, reset, shutdown, or error
            transition_modes = [Modes.NORMAL, Modes.RESET, Modes.SHUTDOWN, Modes.ERROR]
            if self.mode in transition_modes:
                break

            # Update every 100ms
            time.sleep(0.100)

    def run_error_mode(self) -> None:
        """ Runs error mode. Clears reported values, waits for reset mode 
            command then transitions to RESET. """
        self.logger.info("Entered ERROR")

        # Clear reported values
        self.clear_reported_values()

        # Wait for command from device manager or user
        # Reset device every hour incase error was anomalous
        start_time = time.time()
        while self.thread_is_active:

            # Check for reset mode command from device manager and for hourly reset event
            if self.commanded_mode == Modes.RESET or time.time() - start_time > 3600:
                self.mode == self.commanded_mode
                self.commanded_mode = None
                break

            # Check for new user commanded events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)  # type: ignore

            # Check for transition to reset or shutdown
            transition_modes = [Modes.RESET, Modes.SHUTDOWN]
            if self.mode in transition_modes:
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_reset_mode(self) -> None:
        """ Runs reset mode. Clears error state then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Reset peripheral
        self.reset()

        # Transition to init
        self.mode = Modes.INIT

    def run_shutdown_mode(self) -> None:
        """ Runs shutdown mode. Shuts down peripheral, waits for 
            initialize command"""
        self.logger.info("Entered SHUTDOWN")

        # Shutdown peripheral
        self.shutdown()

        # Wait for command from device or user
        last_update_seconds = time.time() - self.sampling_interval_seconds
        while self.thread_is_active:
            # Check for initialize mode command from device manager
            if self.commanded_mode == Modes.INIT:
                self.mode = self.commanded_mode
                self.commanded_mode = None
                break

            # Check for new user commanded events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)  # type: ignore

            # Check for transition to error or reset
            if self.mode == Modes.ERROR or self.mode == Modes.RESET:
                break

            # Update every 100ms
            time.sleep(0.1)

            # Log shutdown state every update interval seconds
            last_update_interval_seconds = time.time() - last_update_seconds
            if self.sampling_interval_seconds < last_update_interval_seconds:
                self.logger.debug("Peripheral is shutdown, waiting for reset")
                last_update_seconds = time.time()

    def load_setup_dict_from_file(self) -> Dict:
        """ Loads setup dict from setup filename parameter. """
        self.logger.debug("Loading setup file")
        file_name = self.parameters["setup"]["file_name"]
        setup_dict = json.load(
            open("device/peripherals/modules/" + file_name + ".json")
        )
        return dict(setup_dict)

    def initialize(self) -> None:
        """ Initializes peripheral. """
        self.logger.debug("No initialization required.")

    def setup(self) -> None:
        """ Sets up peripheral. """
        self.logger.debug("No setup required")

    def update(self) -> None:
        """ Updates peripheral. """
        self.logger.debug("No update required")

    def reset(self) -> None:
        """ Resets peripheral. """
        self.logger.debug("No reset required")

    def shutdown(self) -> None:
        """ Shutsdown peripheral. """
        self.logger.debug("No shutdown required")

    def clear_reported_values(self) -> None:
        """Clears reported values. Child class should overwrite."""
        self.logger.debug("No values to clear")
