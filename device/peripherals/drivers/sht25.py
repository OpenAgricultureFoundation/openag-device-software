# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.temperature_humidity import TemperatureHumidity

# Import device modes and errors
from device.utilities.mode import Mode
from device.utilities.error import Error

# Import device comms
import device.comms.i2c as I2C



class SHT25(TemperatureHumidity):
    """ A temperature and humidity sensor. """

    def __init__(self, *args, **kwargs):
        super(TemperatureHumidity, self).__init__(*args, **kwargs)
        self.i2c = I2C.get_i2c_device(0x40, busnum=2)
        time.sleep(0.5)


    def quickly_check_hardware_state(self):
        """ Quickly check hardware state. """
        self.logger.debug("Quickly checking hardware state")


    def initialize_hardware(self):
        """ Initialize hardware. """
        self.logger.debug("Initializing hardware")


    def get_temperature(self):
        """ Get sensor temperature. """

        try:
            with threading.Lock():
                self.i2c.writeRaw8(0xF3)

            time.sleep(0.5)

            with threading.Lock():
                data0 = self.i2c.readRaw8()
                data1 = self.i2c.readRaw8()

            # Convert the data
            temp = data0 * 256 + data1
            temp = -46.85 + ((temp * 175.72) / 65536.0)
            self.temperature = float("%.1f"%(temp))

            self.logger.info(self.temperature)
       
        except:
            self.logger.info("Bad reading")


    def get_humidity(self):
        """ Get sensor humidity. """
        try:
            self.humidity = 23
        except:
            self.logger.exception("Unable to get humidity")
            self.mode = Mode.ERROR
            self.error = Error.UNKNOWN