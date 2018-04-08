# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device comms
from device.comms.i2c import I2C

# Import device modes and errors
from device.utilities.mode import Mode
from device.utilities.error import Error


class AtlasPH(Peripheral):
    """ Atlas pH sensor. """

    # Initialize sensor parameters
    _ph = None
    _status = None

    # Initialize health metrics
    _health = None
    _minimum_health = 80.0
    _missed_readings = 0
    _readings_count = 0
    _readings_per_health_update = 20


    @property
    def ph(self):
        """ Gets pH value. """
        return self._ph


    @ph.setter
    def ph(self, value):
        """ Safely updates ph in environment state each time
            it is changed. """   
        self.logger.debug("pH: {}".format(value))    
        self._ph = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.ph_name, value)


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
        self.ph_name = self.parameters["variables"]["sensor"]["ph"]

        # Remove me
        self.simulate = True


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.ph = None
        self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()
            

    def perform_initial_health_check(self):
        """ Performs initial health check by trying to send a `get temperature
            reading command` and verifying sensor acknowledges. Finishes 
            within 200ms. """
        try:
            # TODO: Do something
            self.logger.info("Passed initial health check")
        except Exception:
            self.logger.exception("Failed initial health check")
            self.error = Error.FAILED_HEALTH_CHECK
            self.mode = Mode.ERROR


    def warm(self):
        """ Warms sensor. Useful for sensors with warm up times >200ms """
        self.logger.debug("Warming sensor")
        # TODO: Do something


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.ph = 7.77
            self.health = 100
        else:
            self.update_ph()
            self.update_health()


    def update_ph(self):
        """ Updates sensor ph. """
        self.logger.debug("Getting pH")
        try:
            # Send read command
            with threading.Lock():
                bytes = bytearray("R\00", 'utf8') # Create byte array
                self.i2c.write_raw(bytes) # Send get ph command
            
            # Wait for sensor to process
            time.sleep(0.9) 

            # Read sensor data
            with threading.Lock():
                data = self.i2c.read(8) 
                if len(data) != 8:
                    self.logger.critial("Requested 8 bytes but only received {}".format(len(data)))
                # TODO: throw an error if we dont get 8 bytes back...
                # Need to flush the bus...
                # Extra laggard bytes will mess up other sensors...
                # TODO: before each read, flush the bus...do this in i2c.py

            # Convert status data
            status = data[0] 

            # Convert ph data
            raw = float(data[1:].decode('utf-8').strip("\x00"))

            # Set significant figures
            ph = float("{:.1f}".format(raw))

            # Update status in shared state
            self.ph = ph

        except:
            self.logger.exception("Bad pH reading")
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
                self.error = Error.FAILED_HEALTH_CHECK

                # Transition to error mode
                self.mode = Mode.ERROR


    def shutdown(self):
        """ Shuts down sensor. """

        # Clear reported values
        self.clear_reported_values()

        # Set sensor health
        self.health = 100


    def clear_reported_values(self):
        self.ph = None