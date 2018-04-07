# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.temperature_humidity import TemperatureHumidity

# Import device modes and errors
from device.utilities.mode import Mode
from device.utilities.error import Error


class SHT25(TemperatureHumidity):
    """ Temperature and humidity sensor. """

    def __init__(self, *args, **kwargs):
        super(TemperatureHumidity, self).__init__(*args, **kwargs)
        

    def quickly_check_hardware_state(self):
        """ Quickly check hardware state. """
        self.logger.debug("Quickly checking hardware state")


    def initialize_hardware(self):
        """ Initialize hardware. """
        self.logger.debug("Initializing hardware")


    def get_temperature(self):
        """ Get sensor temperature. """
        self.logger.debug("Getting temperature")
        try:
            # Send read temperature command (no-hold master)
            with threading.Lock():
                self.i2c.writeRaw8(0xF3)
                
            # Wait for sensor to process
            time.sleep(0.5)

                # Read sensor data
            with threading.Lock():
                data0 = self.i2c.readRaw8()
                data1 = self.i2c.readRaw8()

            # Convert temperature data
            temperature = data0 * 256 + data1
            temperature = -46.85 + ((temperature * 175.72) / 65536.0)

            # Set significant figures and update shared state
            self.temperature = float("%.1f"%(temperature))
            self.logger.debug("Temperature: {}".format(self.temperature))
       
        except:
            self.logger.exception("Bad temperature reading")


    def get_humidity(self):
        """ Get sensor humidity. """
        self.logger.debug("Getting humidity")
        try:
            # Send read humidity command (no-hold master)
            with threading.Lock():
                self.i2c.writeRaw8(0xF5)

            # Wait for sensor to process
            time.sleep(0.5)

            # Read sensor
            with threading.Lock():
                data0 = self.i2c.readRaw8()
                data1 = self.i2c.readRaw8()

            # Convert humidity data
            humidity = data0 * 256 + data1
            humidity = -6 + ((humidity * 125.0) / 65536.0)
            
            # Set significant figures and update shared state
            self.humidity = float("%.1f"%(humidity))
            self.logger.debug("Humidity: {}".format(self.humidity))
        
        except:
            self.logger.exception("Bad humidity reading")