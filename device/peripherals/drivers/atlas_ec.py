# Import python modules
import logging, time, threading

# Import atlas device parent class
from device.peripherals.classes.atlas import Atlas

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class AtlasEC(Atlas):
    """ Atlas EC sensor. """

    # Initialize sensor parameters
    _ec = None
    _accuracy_percent = 2


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
            

    def setup(self):
        """ Sets up sensor. Programs device operation parameters into 
            sensor driver circuit. Transitions to NORMAL on completion 
            and ERROR on error. """
        self.logger.debug("Setting up sensor")

        try:
            # Verify correct driver stamp
            info = self.info
            if self.info["device"] != "EC":
                self.logger.critical("Incorrect driver circuit. Expecting EC, received {}".format(info["device"]))
                raise exception("Incorrect hardware configuration")

            # Lock i2c protocol and set output parameters on supported firmware
            if float(info["firmware_version"]) >= 1.95:
                self.protocol_lock = True 
                self.output_parameter_ec = True # Enable electrical conductivity output
                self.output_parameter_tds = False # Disable total dissolved solids output
                self.output_parameter_s = False # Disable salinity output
                self.output_parameter_sg = False # Disable specific gravity output
            else:
                self.logger.warning("Using old circuit stamp, consider upgrading")
            
            # Enable status led
            self.led = True 

            # Set probe type
            self.probe_type = "1.0"
       
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.ec = 3.33
            self.health = 100
        else:
            self.update_ec()
            self.update_health()


    def shutdown(self):
        """ Shuts down sensor. Clears reported values, resets sensor health,
            then sets device into sleep mode. """
        self.clear_reported_values()
        self.health = 100
        self.sleep = True
        

    def update_ec(self):
        """ Updates sensor ec. """
        self.logger.debug("Updating EC")
        try:
            # Get EC from device
            # Assumes EC is only device output
            response_string = self.process_command("R", processing_seconds=0.6)
            raw_ec = float(response_string) / 1000 # Convert uS/cm to mS/cm

            # Set significant figures based off error magnitude
            error_value = raw_ec * self._accuracy_percent / 100
            error_magnitude = self.magnitude(error_value)
            significant_figures = error_magnitude * -1
            self.ec = round(raw_ec, significant_figures)

        except:
            self.logger.exception("Bad reading")
            self._missed_readings += 1
    

    def clear_reported_values(self):
        """ Clears reported values. """
        self.ec = None


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
        response_message = self.process_command("O,?", processing_seconds=0.3)
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
            self.process_command("O,EC,1", processing_seconds=0.3)
        else:
            self.process_command("O,EC,0", processing_seconds=0.3)

    @property
    def output_parameter_tds(self):
        """ Gets output parameter total dissolved solids state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
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
            self.process_command("O,TDS,1", processing_seconds=0.3)
        else:
            self.process_command("O,TDS,0", processing_seconds=0.3)

    @property
    def output_parameter_s(self):
        """ Gets output parameter salinity state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
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
            self.process_command("O,S,1", processing_seconds=0.3)
        else:
            self.process_command("O,S,0", processing_seconds=0.3)


    @property
    def output_parameter_sg(self):
        """ Gets output parameter specific gravity state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
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
            self.process_command("O,SG,1", processing_seconds=0.3)
        else:
            self.process_command("O,SG,0", processing_seconds=0.3)


    @property
    def probe_type(self):
        """ Gets probe type from device. """
        response_message = self.process_command("K,?", processing_seconds=0.6)
        if response_message != None:
            command, value = response_message.split(",")
            return value
        else:
            return None


    @probe_type.setter
    def probe_type(self, value):
        """ Sets device probe type. """ 
        if value:  
            self.process_command("K,{}".format(value), processing_seconds=0.3)
        else:
            self.process_command("K,{}".format(value), processing_seconds=0.3)




