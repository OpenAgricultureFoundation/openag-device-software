# Import python modules
import logging, time, threading

# Import device modes and errors
from device.utility.mode import Mode
from device.utility.error import Error


class Peripheral:
    """ Parent class for peripheral devices e.g. sensors and actuators. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize peripheral mode and error
    _mode = None
    _error = None

    # Initialize timing variables
    sampling_interval_sec = 2
    last_update_time = None


    def __init__(self, name, state):
        """ Initializes peripheral. """
        self.name = name
        self.state = state
        self.mode = Mode.INIT
        self.error = Error.NONE
        self.initialize_peripheral()


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
    def error(self):
        """ Gets error value. """
        return self._error


    @error.setter
    def error(self, value):
        """ Safely updates peripheral error in system object each time
            it is changed. """
        self._error= value
        with threading.Lock():
            if self.name not in self.state.peripherals:
                self.state.peripherals[self.name] = {}
            self.state.peripherals[self.name]["error"] = value


    def commanded_mode(self):
        """ Gets the peripheral's commanded mode. """
        if self.name in self.state.peripherals and \
            "commanded_mode" in self.state.peripherals[self.name]:
            return self.state.peripherals[self.name]["commanded_mode"]
        else:
            return None


    def spawn(self):
        """ Spawns peripheral thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()


    def run_state_machine(self):
        """ Runs peripheral state machine. """
        self.logger.info("Starting state machine")
        while True:
            if self.mode == Mode.INIT:
                self.run_init_mode()
            elif self.mode == Mode.SETUP:
                self.run_setup_mode()
            elif self.mode == Mode.NOM:
                self.run_nom_mode()
            elif self.mode == Mode.ERROR:
                self.run_error_mode()
            elif self.mode == Mode.RESET:
                self.run_reset_mode()


    def run_init_mode(self):
        """ Runs initialization mode. Initializes sensor then transitions to 
            normal operating mode. Transitions to error mode on error. """
        self.logger.info("{} entered INIT".format(self.name))
        self.initialize_peripheral()
        self.mode = Mode.NOM


    def run_setup_mode(self):
        """ Runs setup mode. Waits for device to enter initialization mode 
            then transitions to initialization state. """
        self.logger.info("{} entered SETUP".format(self.name))
        self.setup_peripheral()
        while self.state.device["mode"] != Mode.INIT:
            time.sleep(0.100) # 100ms
        self.mode = Mode.INIT


    def run_nom_mode(self):
        """ Runs normal operation mode. Gets temperature and humidity reading
            every <sampling_rate> seconds. Transitions to reset if commanded. 
            Transitions to error mode on error. """
        self.logger.info("{} entered NOM".format(self.name))
        self.last_update_time_sec = time.time()
        while True:
            if self.sampling_interval_sec < time.time() - self.last_update_time_sec:
                self.update_peripheral()
                self.last_update_time_sec = time.time()
            else:
                time.sleep(0.100) # 100ms

            if self.commanded_mode() == Mode.RESET:
                self.mode = self.commanded_mode()
                continue
            elif self.mode == Mode.ERROR:
                continue


    def run_error_mode(self):
        """ Runs error mode. Errorizes peripheral. Waits for reset mode 
            command then transitions to reset mode. """
        self.logger.info("{} entered ERROR".format(self.name))

        self.errorize_peripheral()
        
        while True:
            if self.commanded_mode == Mode.RESET:
                self.mode == commanded_mode
                continue
            time.sleep(0.1) # 100ms


    def run_reset_mode(self):
        """ Runs reset mode. Resets peripheral then transitions to 
            initialization mode. """
        self.logger.info("{} entered RESET".format(self.name))
        self.error = Error.NONE
        self.mode = Mode.INIT
        self.reset_peripheral()


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
        self.state.environment["actuator"]["reported"][variable] = value