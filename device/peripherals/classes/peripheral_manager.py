# Import python modules
import logging, time, threading, math, json

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors
from device.utilities.logger import Logger

# Import device comms
from device.comms.i2c import I2C


class PeripheralManager:
    """ Parent class for peripheral devices e.g. sensors and actuators. """

    # Initialize peripheral mode and error
    _mode = None
    _error = None

    # Initialize thread terminator
    thread_is_active = True

    # Initialize timing variabless
    _default_sampling_interval_seconds = 5
    _min_sampling_interval_seconds = 2
    last_update_seconds = None
    last_update_interval_seconds = None


    def __init__(self, name, state, config, simulate=False, mux_simulator=None):
        """ Initializes peripheral. """

        # Initialize passed in parameters
        self.name = name
        self.state = state
        self.config = config
        self.simulate = simulate
        self.mux_simulator = mux_simulator

        # Initialize logger
        self.logger = Logger(
            name = "Manager({})".format(self.name),
            dunder_name = __name__,
        )

        # Initialize modes and errors
        self.mode = Modes.INIT
        self.error = Errors.NONE

        # Load config parameters
        self.parameters = self.config["parameters"]

        # Load setup dict and uuid
        self.setup_dict = self.load_setup_dict_from_file()
        self.setup_uuid = self.setup_dict["uuid"]


    @property
    def health(self) -> None:
        """ Gets health value. """
        return self.state.get_peripheral_value(self.name, "health")


    @health.setter
    def health(self, value: dict) -> None:
        """ Sets health value in shared state. """
        self.state.set_peripheral_value(self.name, "health", value)


    # TODO: Use state functions on remaining properties


    @property
    def mode(self):
        """ Gets mode value. """
        return self._mode


    @mode.setter
    def mode(self, value):
        """ Safely updates peripheral mode in device state object. """
        self._mode = value
        with threading.Lock():
            if self.name not in self.state.peripherals:
                self.state.peripherals[self.name] = {}
            self.state.peripherals[self.name]["mode"] = value


    @property
    def commanded_mode(self):
        """ Gets commanded mode from shared state object. """
        if self.name in self.state.peripherals and \
            "commanded_mode" in self.state.peripherals[self.name]:
            return self.state.peripherals[self.name]["commanded_mode"]
        else:
            return None


    @commanded_mode.setter
    def commanded_mode(self, value):
        """ Safely updates commanded mode in state object. """
        with threading.Lock():
            self.state.peripherals[self.name]["commanded_mode"] = value


    @property
    def setup_uuid(self):
        """ Gets setup uuid from shared state object. """
        if self.name in self.state.peripherals and \
            "setup_uuid" in self.state.peripherals[self.name]:
            return self.state.peripherals[self.name]["setup_uuid"]
        else:
            return None


    @setup_uuid.setter
    def setup_uuid(self, value):
        """ Safely updates setup uuid in state object. """
        with threading.Lock():
            self.state.peripherals[self.name]["setup_uuid"] = value


    @property
    def sampling_interval_seconds(self):
        """ Gets sampling interval from shared state object. """
        if self.name in self.state.peripherals and \
            "stored" in self.state.peripherals[self.name] and \
            "sampling_interval_seconds" in self.state.peripherals[self.name]["stored"]:
            return self.state.peripherals[self.name]["stored"]["sampling_interval_seconds"]
        else:
            self.sampling_interval_seconds = self._default_sampling_interval_seconds
            return self._default_sampling_interval_seconds


    @sampling_interval_seconds.setter
    def sampling_interval_seconds(self, value):
        """ Safely updates sampling interval in state object. """
        with threading.Lock():
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            self.state.peripherals[self.name]["stored"]["sampling_interval_seconds"] = value


    @property
    def request(self):
        """ Gets request from shared state object. """
        if self.name in self.state.peripherals and \
            "request" in self.state.peripherals[self.name]:
            return self.state.peripherals[self.name]["request"]
        else:
            return None


    @request.setter
    def request(self, value):
        """ Safely updates request in state object. """
        with threading.Lock():
            self.state.peripherals[self.name]["request"] = value


    @property
    def response(self):
        """ Gets response from shared state object. """
        if self.name in self.state.peripherals and \
            "response" in self.state.peripherals[self.name]:
            return self.state.peripherals[self.name]["response"]
        else:
            return None


    @response.setter
    def response(self, value):
        """ Safely updates request in state object. """
        with threading.Lock():
            self.state.peripherals[self.name]["response"] = value


    def spawn(self):
        """ Spawns peripheral thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()


    def run_state_machine(self):
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


    def run_init_mode(self):
        """ Runs initialization mode. Initializes peripheral state then 
            transitions to SETUP. Transitions to ERROR on error. """
        self.logger.info("Entered INIT")

        # Initialize peripheral
        self.initialize()

        # Transition to SETUP if not ERROR
        if self.mode != Modes.ERROR:
            self.mode = Modes.SETUP


    def run_setup_mode(self):
        """ Runs setup mode. Sets up peripheral then transitions to NORMAL on 
            completion or ERROR on error. """
        self.logger.info("Entered SETUP")

        # Setup peripheral
        self.setup()

        # Transition to NORMAL if not ERROR
        if self.mode != Modes.ERROR:
            self.mode = Modes.NORMAL


    def run_normal_mode(self):
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
                self.logger.debug("Updating peripheral, delta: {:.3f}".format(self.last_update_interval_seconds))
                self.last_update_seconds = time.time()
                self.update()

            # Check for update error
            if self.mode == Modes.ERROR:
                break

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)

            # Check for state transition
            transition_modes = [
                Modes.CALIBRATE, 
                Modes.MANUAL, 
                Modes.RESET, 
                Modes.SHUTDOWN, 
                Modes.ERROR,
            ]
            if self.mode in transition_modes:
                break

            # Update every 100ms
            time.sleep(0.100)


    def run_calibrate_mode(self):
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
                self.logger.debug("Updating peripheral, time delta: {:.3f} sec".format(self.last_update_interval_seconds))
                self.last_update_seconds = time.time()
                self.update()

            # Check for transition to error or reset
            if self.mode == Modes.ERROR or self.mode == Modes.RESET:
                break

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)
            
            # Update every 100ms
            time.sleep(0.100)


    def run_manual_mode(self):
        """ Runs manual mode. Waits for new events and checks for transition to
            normal, reset, shutdown, or error."""
        self.logger.info("Entered MANUAL")

        while self.thread_is_active:

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)

            # Check for transition to normal, reset, shutdown, or error
            transition_modes = [Modes.NORMAL, Modes.RESET, Modes.SHUTDOWN, Modes.ERROR]
            if self.mode in transition_modes:
                break
            
            # Update every 100ms
            time.sleep(0.100)


    def run_error_mode(self):
        """ Runs error mode. Clears reported values, waits for reset mode 
            command then transitions to RESET. """
        self.logger.info("Entered ERROR")

        # Clear reported values
        self.clear_reported_values()
        
        
        # Wait for command from device manager or user
        while self.thread_is_active:
           
            # Check for reset mode command from device manager
            if self.commanded_mode == Modes.RESET:
                self.mode == self.commanded_mode
                self.commanded_mode = None
                break

            # Check for new user commanded events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)

            # Check for transition to reset or shutdown
            transition_modes = [Modes.RESET, Modes.SHUTDOWN]
            if self.mode in transition_modes:
                break

            # Update every 100ms
            time.sleep(0.1)


    def run_reset_mode(self):
        """ Runs reset mode. Clears error state then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Reset peripheral
        self.reset()

        # Transition to init
        self.mode = Modes.INIT


    def run_shutdown_mode(self):
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
                self.process_event(request)

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


    def load_setup_dict_from_file(self): 
        """ Loads setup dict from setup filename parameter. """
        self.logger.debug("Loading setup file")
        file_name = self.parameters["setup"]["file_name"]
        setup_dict = json.load(open("device/peripherals/modules/" + file_name + ".json"))
        return setup_dict


    def initialize(self):
        """ Initializes peripheral. """
        self.logger.debug("No initialization required.") 


    def setup(self):
        """ Sets up peripheral. """       
        self.logger.debug("No setup required")


    def update(self):
        """ Updates peripheral. """
        self.logger.debug("No update required")


    def reset(self):
        """ Resets peripheral. """
        self.logger.debug("No reset required")


    def shutdown(self):
        """ Shutsdown peripheral. """
        self.logger.debug("No shutdown required")
