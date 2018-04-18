# Import python modules
import logging, time, threading, math

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class Peripheral:
    """ Parent class for peripheral devices e.g. sensors and actuators. """

    # Initialize peripheral mode and error
    _mode = None
    _error = None

    # Initialize health metrics
    _health = None
    _minimum_health = 80.0
    _missed_readings = 0
    _readings_count = 0
    _readings_per_health_update = 20

    # Initialize thread terminator
    thread_is_active = True

    # Initialize timing variabless
    sampling_interval_seconds = 5
    last_update_seconds = None
    last_update_interval_seconds = None


    def __init__(self, name, state, config, simulate=False):
        """ Initializes peripheral. """

        # Initialize passed in arguments
        self.name = name
        self.state = state
        self.config = config
        self.simulate = simulate

        # Initialize logger
        extra = {'console_name':self.name, 'file_name': self.name}
        logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(logger, extra)

        # Log simulation mode if enabled
        if self.simulate:
            self.logger.info("Simulating sensor")

        # Initialize modes and errors
        self.mode = Modes.INIT
        self.error = Errors.NONE


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
    def health(self):
        """ Gets health value. """
        return self._health


    @health.setter
    def health(self, value):
        """ Safely updates health in device state each time 
            it is c hanged. """
        self._health = value
        self.logger.debug("Health: {}".format(value))
        with threading.Lock():
            self.report_health(self._health)


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
            elif self.mode == Modes.RESET:
                self.run_reset_mode()
            elif self.mode == Modes.SHUTDOWN:
                self.run_shutdown_mode
            else:
                self.error = Errors.INVALID_MODE
                self.logger.critical("Entered invalid mode")


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
                self.logger.debug("Updating peripheral, time delta: {:.3f} sec".format(self.last_update_interval_seconds))
                self.last_update_seconds = time.time()
                self.update()

            # Check for error or calibrate transition
            if self.mode == Modes.ERROR or self.mode == Modes.CALIBRATE:
                break

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)
            
            # Update every 100ms
            time.sleep(0.100)


    def run_calibrate_mode(self):
        """ Runs calibrate mode. Currently just does the same thing as normal
            mode except variable reporting functions only update peripheral 
            state instead of both peripheral and environment. Transitions to 
            ERROR or NORMAL."""
        self.logger.info("Entered CALIBRATE")

        self._update_complete = True
        self.last_update_seconds = time.time()
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


    def run_error_mode(self):
        """ Runs error mode. Clears reported values, waits for reset mode 
            command then transitions to RESET. """
        self.logger.info("Entered ERROR")

        # Clear reported values
        self.clear_reported_values()
        
        # Wait for reset mode command
        while self.thread_is_active:
            if self.commanded_mode == Modes.RESET:
                self.mode == self.commanded_mode
                self.commanded_mode = None
                break
            time.sleep(0.1) # 100ms


    def run_reset_mode(self):
        """ Runs reset mode. Clears error state then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Clear error state
        self.error = Errors.NONE

        # Transition to init
        self.mode = Modes.INIT


    def run_shutdown_mode(self):
        """ Runs shutdown mode. Shuts down peripheral, waits for 
            initialize command"""
        self.logger.info("Entered SHUTDOWN")

        # Shutdown peripheral
        self.shutdown()

        # Wait for initialize mode command
        while self.thread_is_active:
            if self.commanded_mode == Modes.INIT:
                self.mode = self.commanded_mode
                self.commanded_mode = None
                break

            # Update every 100ms
            time.sleep(0.1)



    def report_sensor_value(self, sensor, variable, value, simple=False):
        """ Report sensor value to environment sensor dict and reported sensor 
            stats dict. """

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
        with threading.Lock():
            self.state.environment["actuator"]["reported"][variable] = value


    def report_health(self, value):
        """ Report peripheral health. """
        with threading.Lock():
            self.state.peripherals[self.name]["health"] = value


    def report_peripheral_value(self, variable, value):
        """ Reports a peripherals value to peripheral dict in shared state. """
        with threading.Lock():
            self.state.peripherals[self.name][variable] = value


    def update_health(self):
        """ Updates sensor health. """

        # Increment readings count
        self._readings_count += 1

        # Update health after specified number of readings
        if self._readings_count == self._readings_per_health_update:
            good_readings = self._readings_per_health_update - self._missed_readings
            health = float(good_readings) / self._readings_per_health_update * 100
            self.health = int(health)

            # Check health is satisfactory
            if self.health < self._minimum_health:
                self.logger.warning("Unacceptable sensor health")

                # Set error
                self.error = Errors.FAILED_HEALTH_CHECK

                # Transition to error mode
                self.mode = Modes.ERROR


    def magnitude(self, x):
        """ Gets magnitude of provided value. """
        return int(math.floor(math.log10(x)))
