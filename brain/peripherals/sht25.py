# Import python modules
import logging, time, threading

# Import all possible states & errors
from states import States
from errors import Errors


class SHT25(object):
    """ A temperature and humidity sensor. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize state and error lists
    states = States()
    errors = Errors()

    # Initialize state & error variables
    _state = None
    _error = None

    # Initialize sensor variables
    _temperature = None
    _humidity = None

    # Initialize timeing variables
    sampling_interval_sec = 2
    last_update_time = None


    def __init__(self, name, config, env, sys):
        """ Initializes SHT25. """
        self.name = name
        self.env = env
        self.sys = sys
        self.bus = config["comms"]["bus"]
        self.mux = config["comms"]["mux"]
        self.channel = config["comms"]["channel"]
        self.address = config["comms"]["address"]
        self.temperature_name = config["variables"]["temperature"]["name"]
        self.temperature_unit = config["variables"]["temperature"]["unit"]
        self.humidity_name = config["variables"]["humidity"]["name"]
        self.humidity_unit = config["variables"]["humidity"]["unit"]

        # Set state & error values
        self.state = self.states.SETUP
        self.error = self.errors.NONE


    @property
    def state(self):
        """ Gets state value. """
        return self._state


    @state.setter
    def state(self, value):
        """ Safely updates peripheral state in system object each time
            it is changed. """
        self._state = value
        with threading.Lock():
            if self.name not in self.sys.peripheral_state:
                self.sys.peripheral_state[self.name] = {}
            self.sys.peripheral_state[self.name]["state"] = self._state


    def commanded_state(self):
        """ Gets the peripheral's commanded state. """
        if self.name in self.sys.peripheral_state and \
            "commanded_state" in self.sys.peripheral_state[self.name]:
            return self.sys.peripheral_state[self.name]["commanded_state"]
        else:
            return None


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
            if self.name not in self.sys.peripheral_state:
                self.sys.peripheral_state[self.name] = {}
            self.sys.peripheral_state[self.name]["error"] = self._error


    @property
    def temperature(self):
        """ Gets temperature value. """
        return self._temperature


    @temperature.setter
    def temperature(self, value):
        """ Safely updates temperature in environment object each time
            it is changed. """
        self._temperature = value
        with threading.Lock():
            self.env.report_sensor_value(self.name, self.temperature_name, 
                                        self._temperature)

    @property
    def humidity(self):
        """ Gets humidity value. """
        return self._humidity


    @humidity.setter
    def humidity(self, value):
        """ Safely updates humidity in environment object each time 
            it is changed. """
        self._humidity = value
        with threading.Lock():
            self.env.report_sensor_value(self.name, self.humidity_name, 
                                        self._humidity)


    def run(self):
        """ Spawns peripheral thread. """
        t = threading.Thread(target=self.state_machine)
        t.daemon = True
        t.start()


    def state_machine(self):
        """ Runs state machine. """
        self.logger.debug("Starting state machine")
        while True:
            if self.state == self.states.SETUP:
                self.setup_state()
            elif self.state == self.states.INIT:
                self.init_state()
            elif self.state == self.states.NOS:
                self.nos_state()
            elif self.state == self.states.ERROR:
                self.error_state()
            elif self.state == self.states.RESET:
                self.reset_state()


    def setup_state(self):
        """ Runs setup state. Waits for system to enter initialization state 
            then transitions to initialization state. """
        self.logger.debug("Entered SETUP state")
        while self.sys.state != self.states.INIT:
            time.sleep(0.100) # 100ms
        self.state = self.states.INIT


    def init_state(self):
        """ Runs initialization state. Initializes sensor then transitions to 
            normal operating state. Transitions to error state on error. """
        self.logger.debug("Entered INIT state")
        self.initialize_sensor()
        self.state = self.states.NOS


    def nos_state(self):
        """ Runs normal operation state. Gets temperature and humidity reading
            every <sampling_rate> seconds. Transitions to reset if commanded. 
            Transitions to error state on error. """
        self.logger.debug("Entered NOS state")
        self.last_update_time_ms = time.time()
        while True:
            if self.sampling_interval_sec < time.time() - self.last_update_time_ms:
                self.get_temperature()
                self.get_humidity()
                self.last_update_time_ms = time.time()
            else:
                time.sleep(0.100) # 100ms

            if self.commanded_state() == self.states.RESET:
                self.state = self.commanded_state()
                continue

            if self.state == self.states.ERROR:
                continue

    def error_state(self):
        """ Runs error state. Waits for commaned state to be set to reset,
            then transitions to reset state. """
        self.logger.debug("Entered ERROR state")
        while (self.sys.state != self.states.RESET and \
            self.commanded_state() != self.states.RESET):
            time.sleep(0.1) # 100ms
        self.state = self.states.RESET


    def reset_state(self):
        """ Runs reset state. Resets device state then transitions to 
            initialization state. """
        self.logger.debug("Entered RESET state")
        self.temperature = None
        self.humidity = None
        self.error = self.errors.NONE
        self.state = self.state.INIT


    def initialize_sensor(self):
        """ Initializes sensor. """
        try:
            self.logger.debug("Sensor initialized")
        except:
            self.logger.exception("Unable to initialize")
            self.state = self.states.ERROR
            self.error = self.errors.UNKNOWN


    def get_temperature(self):
        """ Get sensor temperature. """
        try:
            self.temperature = 22.0
            self.logger.debug("Got temperature: {}".format(self.temperature))
        except:
            self.logger.exception("Unable to get temperature")
            self.state = self.states.ERROR
            self.error = self.errors.UNKNOWN


    def get_humidity(self):
        """ Get sensor humidity. """
        try:
            self.humidity = 23
            self.logger.debug("Got humidity: {}".format(self.humidity))
        except:
            self.logger.exception("Unable to get humidity")
            self.state = self.states.ERROR
            self.error = self.errors.UNKNOWN