# Import python modules
import threading

# Import peripheral parent class
from ..peripheral import Peripheral


class TemperatureHumidity(Peripheral):
    """ Parent class for temperature and humidity sensors. """
    _temperature = None
    _humidity = None


    def initialize_peripheral_config(self):
        """ Initializes peripheral specific config. """
        self.temperature_name = self.config["variables"]["temperature"]["name"]
        self.humidity_name = self.config["variables"]["humidity"]["name"]


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

    def setup_peripheral(self):
        """ Setup peripheral. """

        self._temperature = None
        self._humidity = None
        with threading.Lock():
            self.env.report_sensor_value(self.name, self.temperature_name, self._temperature, simple=True)
            self.env.report_sensor_value(self.name, self.humidity_name, self._humidity, simple=True)


    def initialize_peripheral(self):
        """ Initializes peripheral. """
        try:
            self.logger.debug("Sensor initialized")
        except:
            self.logger.exception("Unable to initialize")
            self.state = self.states.ERROR
            self.error = self.errors.UNKNOWN


    def update_peripheral(self):
        """ Updates peripheral. """
        self.get_temperature()
        self.get_humidity()


    def reset_peripheral(self):
        """ Reset peripheral. """
        self.temperature = None
        self.humidity = None
