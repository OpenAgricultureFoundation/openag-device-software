# Import python modules
import logging, time, threading

# Import atlas device parent class
from device.peripherals.classes.atlas import Atlas

# Import device comms
from device.comms.i2c import I2C

# Import device modes and errors
from device.utilities.mode import Mode
from device.utilities.error import Error


class AtlasEC(Atlas):
    """ Atlas EC sensor. """

    # Initialize sensor parameters
    _ec = None
    _status = None


    @property
    def ec(self):
        """ Gets EC value. """
        return self._ec


    @ec.setter
    def ec(self, value):
        """ Safely updates ec in environment state each time
            it is changed. """   
        self.logger.debug("EC: {}".format(value))    
        self._ec = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.ec_name, value)


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """
        super().__init__(*args, **kwargs)
        self.ec_name = self.parameters["variables"]["sensor"]["ec"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.ec = None
        self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()
            

    def warm(self):
        """ Warms sensor. Useful for sensors with warm up times >200ms """
        self.logger.debug("Sensor does not require warming")
        # TODO: Do something


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.ec = 2.8
            self.health = 100
        else:
            self.update_ec()
            self.update_health()


    def shutdown(self):
        """ Shuts down sensor. """

        # Clear reported values
        self.clear_reported_values()

        # Set sensor health
        self.health = 100


    def perform_initial_health_check(self):
        """ Performs initial health check by trying to send a `get temperature
            reading command` and verifying sensor acknowledges. Finishes 
            within 200ms. """
        try:
                


            self.logger.info("Passed initial health check")
        except Exception:
            self.logger.exception("Failed initial health check")
            self.error = Error.FAILED_HEALTH_CHECK
            self.mode = Mode.ERROR


    def update_ec(self):
        """ Updates sensor ec. """
        self.logger.debug("Getting EC")
        raw = self.read_value() # Get sensor reading
        ec = float("{:.1f}".format(raw)) # Set significant figures
        self.ec = ec # Update status in shared state


    def clear_reported_values(self):
        """ Clears reported values. """
        self.ec = None