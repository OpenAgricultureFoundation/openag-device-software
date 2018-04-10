# Import python modules
import logging, time, threading

# Import atlas device parent class
from device.peripherals.classes.atlas import Atlas

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class AtlasDO(Atlas):
    """ Atlas DOsensor. """

    # Initialize sensor parameters
    _do = None
    _accuracy_value = 0.05 # mg/L


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """
        super().__init__(*args, **kwargs)
        self.do_name = self.parameters["variables"]["sensor"]["do"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.do = None
        self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()
            

    def setup(self):
        """ Sets up sensor. Programs device operation parameters into 
            sensor driver circuit. Transitions to NORMAL on completion 
            and ERROR on error. """
        self.logger.debug("Setting up sensor")

        try:
            # Verify correct driver stamp
            info = self.info
            if self.info["device"] != "DO":
                self.logger.critical("Incorrect driver circuit. Expecting DO, received {}".format(info["device"]))
                raise exception("Incorrect hardware configuration")

            # Lock i2c protocol and set output parameters on supported firmware
            if float(info["firmware_version"]) >= 1.95:
                self.protocol_lock = True 
                self.output_parameter_mg = True # Enable mg/L output
                self.output_parameter_percent = False # Disable percent saturation output
            else:
                self.logger.warning("Using old circuit stamp, consider upgrading")
            
            # Enable status led
            self.led = True 

        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.do = 4.44
            self.health = 100
        else:
            self.update_do()
            self.update_health()


    def shutdown(self):
        """ Shuts down sensor. Clears reported values, resets sensor health,
            then sets device into sleep mode. """
        self.clear_reported_values()
        self.health = 100
        self.sleep = True


    def update_do(self):
        """ Updates sensor do. """
        self.logger.debug("Updating DO")
        try:
            # Get DO from device
            response_string = self.process_command("R", processing_seconds=0.6)
            raw_do = float(response_string)

            # Set significant figures based off error magnitude
            error_magnitude = self.magnitude(self._accuracy_value)
            significant_figures = error_magnitude * -1
            self.do = round(raw_do, significant_figures)

        except:
            self.logger.exception("Bad reading")
            self._missed_readings += 1
    

    def clear_reported_values(self):
        """ Clears reported values. """
        self.do = None


    @property
    def do(self):
        """ Gets DO value. """
        return self._do


    @do.setter
    def do(self, value):
        """ Safely updates do in environment state each time
            it is changed. """   
        self.logger.debug("DO: {}".format(value))    
        self._do = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.do_name, value)


    @property
    def output_parameter_mg(self):
        """ Gets output parameter mg/L state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
        if response_message != None:
            if "mg" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_mg.setter
    def output_parameter_mg(self, value):
        """ Sets output parameter mg/L state. """ 
        if value:  
            self.process_command("O,mg,1", processing_seconds=0.3)
        else:
            self.process_command("O,mg,0", processing_seconds=0.3)

    @property
    def output_parameter_percent(self):
        """ Gets output parameter percent saturation state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
        if response_message != None:
            if "%" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_percent.setter
    def output_parameter_percent(self, value):
        """ Sets output parameter percent saturations state. """ 
        if value:  
            self.process_command("O,%,1", processing_seconds=0.3)
        else:
            self.process_command("O,%,0", processing_seconds=0.3)