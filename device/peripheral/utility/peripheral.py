# Import python modules
import logging, time, threading

# Import device modes and errors
from device.utility.mode import Mode
from device.utility.error import Error


class Peripheral:
    """ Parent class for peripheral devices e.g. sensors and actuators. """

    # Initialize peripheral mode and error
    _mode = None
    _error = None

    # Initialize thread terminator
    thread_is_active = True

    # Initialize timing variabless
    sampling_interval_sec = 2
    last_update_time = None


    def __init__(self, name, state):
        """ Initializes peripheral. """
        self.name = name
        self.state = state

        # Initialize logger
        extra = {'console_name':self.verbose_name, 'file_name': self.name}
        logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(logger, extra)

        # Initialize remaining state
        self.mode = Mode.INIT
        self.error = Error.NONE
        self.initialize_state()


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
    def error(self):
        """ Gets error value. """
        return self._error


    @error.setter
    def error(self, value):
        """ Safely updates peripheral in shared state. """
        self._error= value
        with threading.Lock():
            if self.name not in self.state.peripherals:
                self.state.peripherals[self.name] = {}
            self.state.peripherals[self.name]["error"] = value


    @property
    def verbose_name(self):
        """ Gets verbose name from shared state object. """
        if self.name in self.state.device["config"]["peripherals"] and \
            "verbose_name" in self.state.device["config"]["peripherals"][self.name]:
            return self.state.device["config"]["peripherals"][self.name]["verbose_name"]
        else:
            return None       


    def spawn(self):
        """ Spawns peripheral thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()


    def run_state_machine(self):
        """ Runs peripheral state machine. """
        while self.thread_is_active:
            if self.mode == Mode.INIT:
                self.run_init_mode()
            elif self.mode == Mode.WARMING:
                self.run_warming_mode()
            elif self.mode == Mode.NORMAL:
                self.run_normal_mode()
            elif self.mode == Mode.ERROR:
                self.run_error_mode()
            elif self.mode == Mode.RESET:
                self.run_reset_mode()
            elif self.mode == Mode.SHUTDOWN:
                self.run_shutdown_mode
            else:
                self.error = Error.INVALID_MODE
                self.logger.critical("Entered invalid mode")


    def run_init_mode(self):
        """ Runs initialization mode. Initializes peripheral state then 
            transitions to WARMING. Transitions to ERROR on error. """
        self.logger.info("Entered INIT")

        # Initialize peripheral state
        self.initialize_state()

        # Transition to WARMING if not ERROR
        if self.mode != Mode.ERROR:
            self.mode = Mode.WARMING


    def run_warming_mode(self):
        """ Runs warming mode. Initializes peripheral hardware then 
            transitions to NORMAL. Transitions to ERROR on error. """
        self.logger.info("Entered WARMING")

        # Initialize peripheral hardware
        self.initialize_hardware()

        # Transition to NORMAL
        self.mode = Mode.NORMAL


    def run_normal_mode(self):
        """ Runs normal operation mode. Every sampling interval gets reported 
            sensor / actuator state, and sets desired actuator state. 
            Transitions to ERROR on error. """
        self.logger.info("Entered NORMAL")
        
        self.last_update_time_sec = time.time()
        while self.thread_is_active:
            # Update every sampling interval
            if self.sampling_interval_sec < time.time() - self.last_update_time_sec:
                self.update()
                self.last_update_time_sec = time.time()

            # Update every 100ms
            time.sleep(0.100) # 100ms

            # Transition to ERROR on error
            if self.mode == Mode.ERROR:
                break


    def run_error_mode(self):
        """ Runs error mode. Clears reported values, waits for reset mode 
            command then transitions to RESET. """
        self.logger.info("Entered ERROR")

        # Clear reported values
        self.clear_reported_values()
        
        # Wait for reset mode command
        while self.thread_is_active:
            if self.commanded_mode == Mode.RESET:
                self.mode == self.commanded_mode
                self.commanded_mode = None
                break
            time.sleep(0.1) # 100ms


    def run_reset_mode(self):
        """ Runs reset mode. Clears error state then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Clear error state
        self.error = Error.NONE

        # Transition to init
        self.mode = Mode.INIT


    def run_shutdown_mode(self):
        """ Runs shutdown mode. Shuts down peripheral, waits for 
            initialize command"""
        self.logger.info("Entered SHUTDOWN")

        # Shutdown peripheral
        self.shutdown()

        # Wait for initialize mode command
        while self.thread_is_active:
            if self.commanded_mode == Mode.INIT:
                self.mode = self.commanded_mode
                self.commanded_mode = None
                break

            # Update every 100ms
            time.sleep(0.1)


    def report_sensor_value(self, sensor, variable, value, simple=False):
        """ Report sensor value to environment sensor dict and reported sensor 
            stats dict. """
        self.logger.debug("Reporting sensor value")

        # Force simple if value is None (don't want to try averaging `None`)
        if value == None:
            simple = True

        with threading.Lock():
            # Update individual instantaneous
            by_type = self.state.environment["reported_sensor_stats"]["individual"]["instantaneous"]
            if variable not in by_type:
                by_type[variable] = {}
            by_var = self.state.environment["reported_sensor_stats"]["individual"]["instantaneous"][variable]
            by_var[sensor] = value

            if simple:
                # Update simple sensor value with reported value
                self.state.environment["sensor"]["reported"][variable] = value

            else:
                # Update individual average
                by_type = self.state.environment["reported_sensor_stats"]["individual"]["average"]
                if variable not in by_type:
                    by_type[variable] = {}
                if sensor not in by_type:
                    by_type[sensor] = {"value": value, "samples": 1}
                else:
                    stored_value = by_type[sensor]["value"]
                    stored_samples = by_type[sensor]["samples"]
                    new_samples = (stored_samples + 1)
                    new_value = (stored_value * stored_samples + value) / new_samples
                    by_type[sensor]["value"] = new_value
                    by_type[sensor]["samples"] = new_samples

                # Update group instantaneous
                by_var_i = self.state.environment["reported_sensor_stats"]["individual"]["instantaneous"][variable]
                num_sensors = 0
                total = 0
                for sensor in by_var_i:
                    if by_var_i[sensor] != None:
                        total += by_var_i[sensor]
                        num_sensors += 1
                new_value = total / num_sensors
                self.state.environment["reported_sensor_stats"]["group"]["instantaneous"][variable] = {"value": new_value, "samples": num_sensors}

                # Update group average
                by_type = self.state.environment["reported_sensor_stats"]["group"]["average"]
                if variable not in by_type:
                    by_type[variable] = {"value": value, "samples": 1}
                else:
                    stored_value = by_type[variable]["value"]
                    stored_samples = by_type[variable]["samples"]
                    new_samples = (stored_samples + 1)
                    new_value = (stored_value * stored_samples + value) / new_samples
                    by_type[variable]["value"] = new_value
                    by_type[variable]["samples"] = new_samples

                # Update simple sensor value with instantaneous group value
                self.state.environment["sensor"]["reported"][variable] = self.state.environment["reported_sensor_stats"]["group"]["instantaneous"][variable]["value"]


    def report_actuator_value(self, actuator, variable, value):
        """ Report an actuator value. """
        self.logger.debug("Reporting actuator value")

        self.state.environment["actuator"]["reported"][variable] = value