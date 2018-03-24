# Import python modules
import threading

# Import peripheral parent class
from device.peripheral.utility.sensor.temperature_humidity import TemperatureHumidity


class SHT25(TemperatureHumidity):
    """ A temperature and humidity sensor. """


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