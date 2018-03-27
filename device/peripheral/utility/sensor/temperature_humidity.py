# Import python modules
import threading

# Import peripheral parent class
from ..peripheral import Peripheral




class TemperatureHumidity(Peripheral):
    """ Parent class for temperature and humidity sensors. """
    
    # Initialize environment variables
    _temperature = None
    _humidity = None


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
            self.report_sensor_value(self.name, self.temperature_name, 
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
            self.report_sensor_value(self.name, self.humidity_name, 
                                            self._humidity)


    def initialize_peripheral(self):
        """ Initializes peripheral specific config. """
        config = self.state.device["config"]["peripherals"][self.name]
        self.bus = config["communication"]["bus"]
        self.mux = config["communication"]["mux"]
        self.channel = config["communication"]["channel"]
        self.address = config["communication"]["address"]
        self.temperature_name = config["variables"]["temperature"]["name"]
        self.humidity_name = config["variables"]["humidity"]["name"]
        self.temperature = None
        self.humidity = None


    def setup_peripheral(self):
        """ Sets up peripheral. """
        try:
            self.logger.debug("Sensor setup")
        except:
            self.logger.exception("Unable to setup")
            self.mode = self.states.ERROR
            self.error = self.errors.UNKNOWN


    def update_peripheral(self):
        """ Updates peripheral. """
        self.get_temperature()
        self.get_humidity()


    def reset_peripheral(self):
        """ Reset peripheral. """
        self.temperature = None
        self.humidity = None


    def errorize_peripheral(self):
        """ Errorizes perpheral. """
        self.temperature = None
        self.humidity = None
