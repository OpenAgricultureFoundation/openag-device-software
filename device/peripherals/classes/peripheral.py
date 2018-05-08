# Import python modules
import logging, time, threading, math, json

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors

# Import device comms
from device.comms.i2c import I2C


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
    _default_sampling_interval_seconds = 10
    _min_sampling_interval_seconds = 2
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

        # Load config parameters
        self.parameters = self.config["parameters"]

        # Load setup dict
        self.load_setup_dict_from_file()

        # Load setup uuid
        self.setup_uuid = self.setup_dict["uuid"]


########################## Setter & Getter Functions ##########################


    @property
    def mode(self):
        """ Gets mode value. """
        return self._mode


    @mode.setter
    def mode(self, value):
        """ Safely updates peripheral mode in device state object. """
        self._mode = value
        self.logger.error("Setting mode to {}".format(value))
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



############################ State Machine Functions ##########################


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
                self.run_shutdown_mode()
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

            # Check for error, calibrate, or shutdown transition
            if (self.mode == Modes.ERROR) or (self.mode == Modes.CALIBRATE):
                break

            # Check for events
            if self.request != None:
                request = self.request
                self.request = None
                self.process_event(request)

            # Check for reset or shutdown transition
            if (self.mode == Modes.RESET) or (self.mode == Modes.SHUTDOWN):
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

            # Update every 100ms
            time.sleep(0.1)


    def run_reset_mode(self):
        """ Runs reset mode. Clears error state then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Reset sensor
        self.reset()

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


############################# Main Helper Functions ###########################

    def establish_i2c_connection(self): 
        """ Establishes i2c connection. Gets i2c parameters from config and 
            opens i2c communication if sensor is not simulated. """

        # Get basic i2c parameters
        self.bus = int(self.parameters["communication"]["bus"])
        self.address = int(self.parameters["communication"]["address"], 16)

        # Get mux i2c parameters TODO: if enabled
        self.mux = int(self.parameters["communication"]["mux"], 16)
        self.channel = int(self.parameters["communication"]["channel"])

        # Open i2c communication if sensor not simulated
        if not self.simulate:
            self.logger.info("Initializing i2c bus={}, mux=0x{:02X}, channel={}, address=0x{:02X}".format(
                self.bus, self.mux, self.channel, self.address))
            self.i2c = I2C(bus=self.bus, mux=self.mux, channel=self.channel, address=self.address)


    def load_setup_dict_from_file(self): 
        """ Loads setup dict from setup filename parameter. """
        self.logger.debug("Loading setup file")
        file_name = self.parameters["setup"]["file_name"]
        self.setup_dict = json.load(open("device/peripherals/setups/" + file_name + ".json"))


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
        """ Reports an actuator value. """
        with threading.Lock():
            self.state.environment["actuator"]["reported"][variable] = value


    def set_desired_actuator_value(self, actuator, variable, value):
        """ Sets and actuators desried value. """
        with threading.Lock():
            self.state.environment["actuator"]["desired"][variable] = value


    def report_health(self, value):
        """ Reports a peripherals health. """
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



############################## Event Functions ################################


    def process_event(self, request):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        self.logger.debug("Processing event request: `{}`".format(request))

        # Get request parameters
        try:
            request_type = request["type"]
            value = request["value"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            self.response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}

        # Process general event requests
        if request_type == "Reset":
            self.response = self.process_reset_event()
        elif request_type == "Shutdown":
            self.response = self.process_shutdown_event()
        elif request_type == "Set Sampling Interval":
            self.response = self.process_set_sampling_interval_event(value)
        else:
            # Process peripheral specific requests
            self.process_peripheral_specific_event(request_type, value)


    def process_reset_event(self):
        """ Processes reset event. """
        self.logger.debug("Processing reset event")

        # Check sensor is in normal, error, or calibration mode
        if (self.mode != Modes.NORMAL) and (self.mode != Modes.ERROR) and \
            (self.mode != Modes.CALIBRATE) and (self.mode != Modes.SHUTDOWN):
            error_message = "Unable to reset peripheral from {} mode!".format(self.mode)
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}

        # Transition to reset mode on next state machine update
        self.mode = Modes.RESET

        # Return event response
        response = {"status": 200, "message": "Resetting!"}
        return response


    def process_shutdown_event(self):
        """ Processes shutdown event. """
        self.logger.debug("Processing shutdown event")

        # Check sensor isn't already in shutdown mode
        if self.mode == Modes.SHUTDOWN:
            error_message = "Device already in shutdown mode!"
            self.logger.info(error_message)
            response = {"status": 200, "message": error_message}
        
        # Transition to shutdown mode on next state machine update
        self.mode = Modes.SHUTDOWN

        # Return event response
        response = {"status": 200, "message": "Shutting down!"}
        return response


    def process_set_sampling_interval_event(self, value):
        """ Processes shutdown event. """
        self.logger.debug("Processing set sampling interval event")

        # Check sensor is in normal or shutdown mode
        if (self.mode != Modes.NORMAL) and (self.mode != Modes.SHUTDOWN):
            error_message = "Unable to set sampling interval from {} mode!".format(self.mode)
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}

        # Get desired sampling interval. TODO: error handle bad type
        desired_sampling_interval_seconds = float(value)

        # Check desired sampling interval larger than min interval
        if desired_sampling_interval_seconds < self._min_sampling_interval_seconds:
            error_message = "Unable to set sampling interval below {} seconds.".format(self._min_sampling_interval_seconds)
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}

        # Set new sampling interval
        self.sampling_interval_seconds = desired_sampling_interval_seconds

        # Return event response
        response = {"status": 200, "message": "Set sampling interval!"}
        return response


############################# Utility Functions ###############################


    def magnitude(self, x):
        """ Gets magnitude of provided value. """
        return int(math.floor(math.log10(x)))


    def get_bit_from_byte(self, bit, byte):
        """ Gets a bit from a byte. """
        mask = 0x1 << bit
        return (byte & mask) >> bit

