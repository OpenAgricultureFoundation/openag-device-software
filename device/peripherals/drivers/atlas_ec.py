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


    @property
    def output_parameter_ec(self):
        """ Gets output parameter electrical conductivity state. """
        response_message = self.process_command("O,?", 0.3)
        if response_message != None:
            if "EC" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_ec.setter
    def output_parameter_ec(self, value):
        """ Sets output parameter electrical conductivity state. """ 
        if value:  
            self.process_command("O,EC,1", 0.3)
        else:
            self.process_command("O,EC,0", 0.3)

    @property
    def output_parameter_tds(self):
        """ Gets output parameter total dissolved solids state. """
        response_message = self.process_command("O,?", 0.3)
        if response_message != None:
            if "TDS" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_tds.setter
    def output_parameter_tds(self, value):
        """ Sets output parameter total dissolved solids state. """ 
        if value:  
            self.process_command("O,TDS,1", 0.3)
        else:
            self.process_command("O,TDS,0", 0.3)

    @property
    def output_parameter_s(self):
        """ Gets output parameter salinity state. """
        response_message = self.process_command("O,?", 0.3)
        if response_message != None:
            # Note: Can't just check if substring in string..`S` in `TDS`,`SG`
            parameters = response_message.split(",")
            for parameter in parameters:
                if parameter == "S":
                    return True
            return False
        else:
            return None


    @output_parameter_s.setter
    def output_parameter_s(self, value):
        """ Sets output parameter salinity state. """ 
        if value:  
            self.process_command("O,S,1", 0.3)
        else:
            self.process_command("O,S,0", 0.3)


    @property
    def output_parameter_sg(self):
        """ Gets output parameter specific gravity state. """
        response_message = self.process_command("O,?", 0.3)
        if response_message != None:
            if "SG" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_sg.setter
    def output_parameter_sg(self, value):
        """ Sets output parameter specific gravity state. """ 
        if value:  
            self.process_command("O,SG,1", 0.3)
        else:
            self.process_command("O,SG,0", 0.3)




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
        self.logger.debug("Warming sensor")

        # Set device operation parameters
        self.protocol_lock = True
        self.led = True
        self.output_parameter_ec = True # enable electrical conductivity output
        self.output_parameter_tds = False # disable total dissolved solids output
        self.output_parameter_s = False # disable salinity output
        self.output_parameter_sg = False # disable specific gravity output
        # TODO: set probe type
        # TODO: set output parameters

        while True:
            self.logger.info("Waiting")
            time.sleep(5)

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
        """ Performs initial health check by....Finishes 
            within 200ms. """
        self.logger.info("Performing initial health check")

        try:
            if self.status != None:
                self.logger.debug("Status not none!")
            else:
                failed_health_check = True

            self.logger.info("Passed initial health check")
        except Exception:
            self.logger.exception("Failed initial health check")
            self.error = Error.FAILED_HEALTH_CHECK
            self.mode = Mode.ERROR


    def update_ec(self):
        """ Updates sensor ec. """
        self.logger.debug("Getting EC")

        try:
            value = self.read_value()
            self.ec = float("{:.1f}".format(value))
        except:
            self.logger.exception("Bad reading")
            self._missed_readings += 1
    

    def clear_reported_values(self):
        """ Clears reported values. """
        self.ec = None