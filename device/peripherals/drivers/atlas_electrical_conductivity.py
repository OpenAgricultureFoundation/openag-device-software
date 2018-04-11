# Import python modules
import logging, time, threading

# Import atlas device parent class
from device.peripherals.classes.atlas import Atlas

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class AtlasElectricalConductivity(Atlas):
    """ Atlas electrical conductivity sensor. """

    # Initialize reported sensor parameters 
    _electrical_conductivity_ms_cm = None
    _electrical_conductivity_accuracy_percent = 2

    # Initialize compensation sensor parameters
    _temperature_threshold_celcius = 0.1


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize reported sensor names
        self.electrical_conductivity_name = self.parameters["variables"]["sensor"]["electrical_conductivity_ms_cm"]

        # Initialize compensation sensor names
        self.temperature_name = self.parameters["variables"]["compensation"]["temperature_celcius"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.electrical_conductivity_ms_cm = None
        self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()
            

    def setup(self):
        """ Sets up sensor. Programs device operation parameters into 
            sensor driver circuit. Transitions to NORMAL on completion 
            and ERROR on error. """
        self.logger.debug("Setting up sensor")

        if self.simulate:
            self.logger.info("Simulating sensor setup")
            return

        try:
            # Verify correct driver stamp
            info = self.info
            if self.info["device"] != "EC":
                self.logger.critical("Incorrect driver circuit. Expecting `EC`, received `{}`".format(info["device"]))
                raise exception("Incorrect hardware configuration")

            # Lock i2c protocol and set output parameters on supported firmware
            if float(info["firmware_version"]) >= 1.95:
                self.protocol_lock = True 
                self.output_parameter_electrical_conductivity = True
                self.output_parameter_total_dissolved_solids = False
                self.output_parameter_salinity = False 
                self.output_parameter_specific_gravity = False
            else:
                self.logger.warning("Using old circuit stamp, consider upgrading")
            
            # Enable status led
            self.led = True 

            # Set probe type
            self.probe_type = "1.0"

            # Reset device compensation values
            self._sensor_temperature_celcius = 0
       
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.electrical_conductivity_ms_cm = 3.33
            self.health = 100
        else:
            self.update_sensor_compensation_variables()
            self.update_electrical_conductivity()
            self.update_health()


    def shutdown(self):
        """ Shuts down sensor. Clears reported values, resets sensor health,
            then sets device into sleep mode. """
        self.clear_reported_values()
        self.health = 100
        self.sleep = True


    def update_sensor_compensation_variables(self):
        """ Update sensor compensation variables. """
        self.update_compensation_temperature()
        
            
    def update_compensation_temperature(self):
        """ Update compensation for electrical conductivity. """
        self.logger.debug("Updating compensation for temperature")

        # Check if there is a temperature value in shared state to compensate with
        state_temp = self.state_temperature_celcius
        if state_temp == None:
            self.logger.debug("No temperature value in shared state to compensate with")
            return

        # Check if temperature value on sensor requires an update
        delta_temp = self._sensor_temperature_celcius - state_temp
        if abs(delta_temp) < self._temperature_threshold_celcius:
            self.logger.debug("Device temperature compensation does not require update, value within threshold")
            return

        # Update sensor temperature compensation value
        self.logger.debug("Updating sensor temperature compensation value")
        self.sensor_temperature_celcuis = state_temp
        

    def update_electrical_conductivity(self):
        """ Updates sensor electrical conductivity. """
        self.logger.debug("Updating electrical conductivity")
        try:
            # Get electrical conductivity from device
            # Assumes electrical conductivity is only device output
            response_string = self.process_command("R", processing_seconds=0.6)
            electrical_conductivity_raw_value = float(response_string) / 1000 # Convert uS/cm to mS/cm

            # Set significant figures based off error magnitude
            error_value = electrical_conductivity_raw_value * self._electrical_conductivity_accuracy_percent / 100
            error_magnitude = self.magnitude(error_value)
            significant_figures = error_magnitude * -1
            self.electrical_conductivity_ms_cm = round(electrical_conductivity_raw_value, significant_figures)

        except:
            self.logger.exception("Bad reading")
            self._missed_readings += 1
    

    def clear_reported_values(self):
        """ Clears reported values. """
        self.electrical_conductivity_ms_cm = None


    @property
    def electrical_conductivity_ms_cm(self):
        """ Gets electrical conductivity value. """
        return self._electrical_conductivity_ms_cm


    @electrical_conductivity_ms_cm.setter
    def electrical_conductivity_ms_cm(self, value):
        """ Safely updates electrical conductivity in environment state each 
            time it is changed. """   
        self.logger.debug("Electrical conductivity: {} mS/cm".format(value))    
        self._electrical_conductivity_ms_cm = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.electrical_conductivity_name, value)



    @property
    def state_temperature_celcius(self):
        """ Gets temperature stored in shared state. """
        if self.temperature_name in self.state.environment["sensor"]["reported"]:
            temperature_celcius = self.state.environment["sensor"]["reported"][self.temperature_name]
            if temperature_celcius != None:
                return float(temperature_celcius)


    @property
    def sensor_temperature_celcius(self):
        """ Gets device compensation temperature value. """
        return self._sensor_temperature_celcius


    @sensor_temperature_celcius.setter
    def sensor_temperature_celcius(self, value):
        """ Sets device temperature compensation value. """   
        self.logger.debug("Setting device compensation temperature: {} C".format(value))
        self._sensor_temperature_celcius = value  
        self.process_command("T,{}".format(value), processing_seconds=0.3)


    @property
    def output_parameter_electrical_conductivity(self):
        """ Gets output parameter electrical conductivity state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
        if response_message != None:
            if "EC" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_electrical_conductivity.setter
    def output_parameter_electrical_conductivity(self, value):
        """ Sets output parameter electrical conductivity state. """ 
        if value:  
            self.process_command("O,EC,1", processing_seconds=0.3)
        else:
            self.process_command("O,EC,0", processing_seconds=0.3)


    @property
    def output_parameter_total_dissolved_solids(self):
        """ Gets output parameter total dissolved solids state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
        if response_message != None:
            if "TDS" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_total_dissolved_solids.setter
    def output_parameter_total_dissolved_solids(self, value):
        """ Sets output parameter total dissolved solids state. """ 
        if value:  
            self.process_command("O,TDS,1", processing_seconds=0.3)
        else:
            self.process_command("O,TDS,0", processing_seconds=0.3)

    @property
    def output_parameter_salinity(self):
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


    @output_parameter_salinity.setter
    def output_parameter_salinity(self, value):
        """ Sets output parameter salinity state. """ 
        if value:  
            self.process_command("O,S,1", processing_seconds=0.3)
        else:
            self.process_command("O,S,0", processing_seconds=0.3)


    @property
    def output_parameter_specific_gravity(self):
        """ Gets output parameter specific gravity state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
        if response_message != None:
            if "SG" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_specific_gravity.setter
    def output_parameter_specific_gravity(self, value):
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




