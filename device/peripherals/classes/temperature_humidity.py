# Import python modules
import threading, logging, time

# Import peripheral parent class
from ..classes.peripheral import Peripheral


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


    def initialize_state(self):
        """ Initializes peripheral specific config. """
        parameters = self.config_dict["parameters"]
        self.bus = parameters["communication"]["bus"]
        self.mux = parameters["communication"]["mux"]
        self.channel = parameters["communication"]["channel"]
        self.address = parameters["communication"]["address"]
        self.temperature_name = parameters["variables"]["sensor"]["temperature"]
        self.humidity_name = parameters["variables"]["sensor"]["humidity"]
        self.temperature = None
        self.humidity = None
        self.quickly_check_hardware_state()


    def update(self):
        """ Updates peripheral. """
        self.get_temperature()
        self.get_humidity()


    def shutdown(self):
        """ Shuts down peripheral. """
        self.clear_reported_values(self)


    def clear_reported_values(self):
        """ Clears reported values. """
        self.temperature = None
        self.humidity = None
