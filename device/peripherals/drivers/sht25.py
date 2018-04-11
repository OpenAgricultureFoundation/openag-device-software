# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device comms
from device.comms.i2c import I2C

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class SHT25(Peripheral):
    """ Temperature and humidity sensor. """

    # Initialize sensor parameters
    _temperature = None
    _humidity = None

    # Initialize health metrics
    _health = None
    _minimum_health = 80.0
    _missed_readings = 0
    _readings_count = 0
    _readings_per_health_update = 20


    @property
    def temperature(self):
        """ Gets temperature value. """
        return self._temperature


    @temperature.setter
    def temperature(self, value):
        """ Safely updates temperature in environment state each time
            it is changed. """   
        self.logger.debug("Temperature: {}".format(value))    
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
        self.logger.debug("Humidity: {}".format(value))
        self._humidity = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.humidity_name, self._humidity)


    @property
    def health(self):
        """ Gets health value. """
        return self._health


    @health.setter
    def health(self, value):
        """ Safely updates health in device state each time 
            it is changed. """
        self._health = value
        self.logger.debug("Health: {}".format(value))
        with threading.Lock():
            self.report_health(self._health)
        

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
        self.i2c = I2C(bus=self.bus, mux=self.mux, channel=self.channel, address=self.address)

        # Initialize sensor variable names
        self.temperature_name = self.parameters["variables"]["sensor"]["temperature"]
        self.humidity_name = self.parameters["variables"]["sensor"]["humidity"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.temperature = None
        self.humidity = None
        self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()
            

    def perform_initial_health_check(self):
        """ Performs initial health check by trying to send a `get temperature
            reading command` and verifying sensor acknowledges. Finishes 
            within 200ms. """
        try:
            # self.i2c.write([0xF3])
            self.logger.info("Passed initial health check")
        except Exception:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR


    def setup(self):
        """ Sets up sensor. Useful for sensors with warm up times >200ms """
        self.logger.debug("Setting up sensor")


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.temperature = 33.3
            self.humidity = 33.3
            self.health = 100
        else:
            self.update_temperature()
            self.update_humidity()
            self.update_health()


    def update_temperature(self):
        """ Updates sensor temperature. """
        self.logger.debug("Getting temperature")

        try:
            # Send read temperature command (no-hold master)
            with threading.Lock():
                self.i2c.write([0xF3])
                
            # Wait for sensor to process
            time.sleep(0.5)

            # Read sensor data
            with threading.Lock():
                msb, lsb = self.i2c.read(2)

            # Convert temperature data and set significant figures
            raw = msb * 256 + lsb
            temperature = -46.85 + ((raw * 175.72) / 65536.0)
            temperature = float("{:.0f}".format(temperature))

            # Update temperature in shared state
            self.temperature = temperature
            
        except:
            self.logger.exception("Bad temperature reading")
            self._missed_readings += 1


    def update_humidity(self):
        """ Updates sensor humidity. """
        self.logger.debug("Getting humidity")
        try:
            # Send read humidity command (no-hold master)
            with threading.Lock():
                self.i2c.write([0xF5])

            # Wait for sensor to process
            time.sleep(0.5)

            # Read sensor
            with threading.Lock():
                msb, lsb = self.i2c.read(2) # Read sensor data

            # Convert humidity data and set significant figures
            raw = msb * 256 + lsb
            humidity = -6 + ((raw * 125.0) / 65536.0)
            humidity = float("{:.0f}".format(humidity))
            
            # Update humidity in shared state
            self.humidity = humidity
        
        except:
            self.logger.exception("Bad humidity reading")
            self._missed_readings += 1


    def update_health(self):
        """ Updates sensor health. """

        # Increment readings count
        self._readings_count += 1

        # Update health after specified number of readings
        if self._readings_count == self._readings_per_health_update:
            good_readings = self._readings_per_health_update - self._missed_readings
            health = float(good_readings) / self._readings_per_health_update * 100
            self.health = int(health)

            # Check health is satisfactory
            if self.health < self._minimum_health:
                self.logger.warning("Unacceptable sensor health")

                # Set error
                self.error = Errors.FAILED_HEALTH_CHECK

                # Transition to error mode
                self.mode = Modes.ERROR


    def shutdown(self):
        """ Shuts down sensor. """

        # Clear reported values
        self.clear_reported_values()

        # Set sensor health
        self.health = 100


    def clear_reported_values(self):
        self.temperature = None
        self.humidity = None