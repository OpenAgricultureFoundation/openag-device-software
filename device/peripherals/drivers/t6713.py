# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device comms
from device.comms.i2c import I2C


from device.utilities.modes import Modes
from device.utilities.errors import Errors


class T6713(Peripheral):
    """ Co2 sensor. """

    # Initialize sensor parameters
    _co2 = None
    _status = None

    # Initialize health metrics
    _health = None
    _minimum_health = 80.0
    _missed_readings = 0
    _readings_count = 0
    _readings_per_health_update = 20


    @property
    def co2(self):
        """ Gets co2 value. """
        return self._co2


    @co2.setter
    def co2(self, value):
        """ Safely updates co2 in environment state each time
            it is changed. """   
        self.logger.debug("Co2: {}".format(value))    
        self._co2 = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.co2_name, value)


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
        self.co2_name = self.parameters["variables"]["sensor"]["co2"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.co2 = None
        self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()
            

    def perform_initial_health_check(self):
        """ Performs initial health check by trying to send a `get temperature
            reading command` and verifying sensor acknowledges. Finishes 
            within 200ms. """
        try:
            # Do something
            self.logger.info("Passed initial health check")
        except Exception:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR


    def setup(self):
        """ Sets up sensor. Useful for sensors with warm up times >200ms """
        self.logger.debug("Setting up sensor")

        # TODO: Get sensor status and check for warming...this is important


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.co2 = 444
            self.health = 100
        else:
            self.update_co2()
            self.update_health()


    def update_co2(self):
        """ Updates sensor co2. """
        self.logger.debug("Getting co2")
        try:
            # Send read status command
            with threading.Lock():
                self.i2c.write([0x04, 0x13, 0x8b, 0x00, 0x01]) 
            
            # Wait for sensor to process
            time.sleep(0.1) 

            # Read sensor data
            with threading.Lock():
                xx, xx, msb, lsb = self.i2c.read(4) 

            # Convert sensor data
            co2 = msb*256 + lsb 

            # Set significant figures
            co2 = int(co2)

            # Update status in shared state
            self.co2 = co2

        except:
            self.logger.exception("Bad status reading")
            self._missed_readings += 1


    def get_status(self):
        """ Gets status of the sensor. """
        self.logger.debug("Getting status")
        try:
            # Send read status command
            with threading.Lock():
                self.i2c.write([0x04, 0x13, 0x8a, 0x00, 0x01]) 
            
            # Wait for sensor to process
            time.sleep(0.1) 

            # Read sensor data
            with threading.Lock():
                xx, xx, msb, lsb = i2c.read(4) 

            # Convert sensor data
            status = msb*256 + lsb 

            # Update status in shared state
            self.status = status

        except:
            self.logger.exception("Bad status reading")
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
        self.co2 = None


# TODO: use these or delete them...
# # Initialize register addresses
# REGISTER_FIRMWARE_REVISTION = 0x1389
# REGISTER_STATUS = 0x138A
# REGISTER_GAS_PPM = 0x138B
# REGISTER_RESET_DEVICE = 0x03E8
# REGISTER_START_SINGLE_POINT_CALIBRATION = 0x3EC
# REGISTER_SLAVE_ADDRESS = 0x0FA5
# REGISTER_ABC_LOGIC_ENABLE_DISABLE = 0x03EE

# # Initialize function codes
# FUNCTION_READ_INPUT_REGISTERS = 0x04
# FUNCTION_WRITE_SINGLE_COIL = 0x05
# FUNCTION_WRITE_SINGLE_REGISTER = 0x06

# # Initialize status register bit breakout
# STATUS_ERROR_CONDITION = 0x0001
# STATUS_FLASH_ERROR = 0x0002
# STATUS_CALIBRATION_ERROR = 0x0004
# STATUS_I2C = 0x0200
# STATUS_WARM_UP_MODE = 0x0400
# STATUS_SINGLE_POINT_CALIBRATION = 0x0800