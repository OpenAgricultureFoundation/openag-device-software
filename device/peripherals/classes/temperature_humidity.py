# Import python modules
import threading, logging, time

# Import peripheral i2c mux parent class
from device.peripherals.classes.peripheral_i2c_mux import PeripheralI2CMux




class TemperatureHumidity(PeripheralI2CMux):
    """ Parent class for temperature and humidity sensors. """
    
    # Initialize environment variables
    _temperature = None
    _humidity = None

    def __init__(self, *args, **kwargs):
        super(PeripheralI2CMux, self).__init__(*args, **kwargs)



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
            self.report_sensor_value(self.name, self.temperature_name, self._temperature)

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
            self.report_sensor_value(self.name, self.humidity_name, self._humidity)


    def initialize_state(self):
        """ Initializes peripheral specific config. """
        self.temperature_name = self.parameters["variables"]["sensor"]["temperature"]
        self.humidity_name = self.parameters["variables"]["sensor"]["humidity"]
        self.temperature = None
        self.humidity = None


        self.quickly_check_hardware_state()


    def update(self):
        """ Updates peripheral. """
        if self.simulate:
            self.temperature = 33.3
            self.humidity = 33.3
        else:
            self.get_temperature()
            self.get_humidity()

    def shutdown(self):
        """ Shuts down peripheral. """
        self.clear_reported_values(self)


    def clear_reported_values(self):
        """ Clears reported values. """
        self.temperature = None
        self.humidity = None
