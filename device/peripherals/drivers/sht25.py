# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device comms
from device.comms.mux_i2c import MuxI2C

# Import device modes and errors
from device.utilities.mode import Mode
from device.utilities.error import Error


class SHT25(Peripheral):
    """ Temperature and humidity sensor. """

    # Initialize environment variables
    _temperature = None
    _humidity = None


    @property
    def temperature(self):
        """ Gets temperature value. """
        return self._temperature


    @temperature.setter
    def temperature(self, value):
        """ Safely updates temperature in environment state each time
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
        """ Safely updates humidity in environment state each time 
            it is changed. """
        self._humidity = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.humidity_name, self._humidity)
        

    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, initializes i2c 
            mux parameters, and initializes sensor variable names. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize i2c mux parameters
        self.parameters = self.config["parameters"]
        self.bus = int(self.parameters["communication"]["bus"])
        self.mux = int(self.parameters["communication"]["mux"], 16)
        self.channel = int(self.parameters["communication"]["channel"])
        self.address = int(self.parameters["communication"]["address"], 16)
        self.logger.info("Initializing i2c bus={}, mux=0x{:02X}, channel={}, address=0x{:02X}".format(
            self.bus, self.mux, self.channel, self.address))
        self.i2c = MuxI2C(self.bus, self.mux, self.channel, self.address)

        # Initialize sensor variable names
        self.temperature_name = self.parameters["variables"]["sensor"]["temperature"]
        self.humidity_name = self.parameters["variables"]["sensor"]["humidity"]


    def initialize(self):
        """ Initializes sensor. Checks sensor is healthy. Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.temperature = None
        self.humidity = None

        # Check sensor health
        if not self.is_healthy():
            self.error = Error.FAILED_HEALTH_CHECK
            self.mode = Mode.ERROR


    def is_healthy(self):
        try:
            self.logger.info("")
            self.i2c.writeRaw8(0xF3)
            return True
        except Exception:
            self.logger.exception("Failed health check".format(self.name))
            return False


    def warm(self):
        """ Warms sensor. Useful for sensors with warm up times >200ms """
        self.logger.debug("Warming sensor")


    def update(self):
        """ Updates peripheral. """
        if self.simulate:
            self.temperature = 33.3
            self.humidity = 33.3
        else:
            self.get_temperature()
            self.get_humidity()


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


    def shutdown(self):
        """ Shuts down sensor. """
        self.clear_reported_values(self)


    def clear_reported_values(self):
        """ Clears reported values. """
        self.temperature = None
        self.humidity = None