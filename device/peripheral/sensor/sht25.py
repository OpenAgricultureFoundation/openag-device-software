# Import python modules
import threading

# Import peripheral parent class
from device.peripheral.utility.sensor.temperature_humidity import TemperatureHumidity

# Import device modes and errors
from device.utility.mode import Mode
from device.utility.error import Error


class SHT25(TemperatureHumidity):
    """ A temperature and humidity sensor. """

    def quickly_check_hardware_state(self):
        """ Quickly check hardware state. """
        self.logger.debug("{}: Quickly checking hardware state".format(self.name))


    def initialize_hardware(self):
        """ Initialize hardware. """
        self.logger.debug("{}: Initializing hardware".format(self.name))


    def get_temperature(self):
        """ Get sensor temperature. """
        try:
            self.temperature = 22.0
            self.logger.debug("{}: Got temperature: {}".format(self.name, self.temperature))
        except:
            self.logger.exception("Unable to get temperature")
            self.mode = Mode.ERROR
            self.error = Error.UNKNOWN


    def get_humidity(self):
        """ Get sensor humidity. """
        try:
            self.humidity = 23
            self.logger.debug("{}: Got humidity: {}".format(self.name, self.humidity))
        except:
            self.logger.exception("Unable to get humidity")
            self.mode = Mode.ERROR
            self.error = Error.UNKNOWN