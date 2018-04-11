# Import python modules
import logging, time, threading

# Import atlas device parent class
from device.peripherals.classes.atlas import Atlas

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class AtlasDissolvedOxygen(Atlas):
    """ Atlas dissolved oxygen sensor. """

    # Initialize reported sensor parameters
    _dissolved_oxygen_mg_l = None
    _dissolved_oxygen_accuracy_mg_l = 0.05

    # Initialize compensation sensor parameters
    _electrical_conductivity_threshold_ms_cm = 0.1
    _temperature_threshold_celcius = 0.1
    _pressure_threshold_kpa = 0.1


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """
        
        # Instantiate parent class
        super().__init__(*args, **kwargs)
        
        # Initialize reported sensor names
        self.dissolved_oxygen_name = self.parameters["variables"]["sensor"]["dissolved_oxygen_mg_l"]

        # Initialize compensation sensor names
        self.electrical_conductivity_name = self.parameters["variables"]["compensation"]["electrical_conductivity_ms_cm"]
        self.temperature_name = self.parameters["variables"]["compensation"]["temperature_celcius"]
        self.pressure_name = self.parameters["variables"]["compensation"]["pressure_kpa"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.dissolved_oxygen_mg_l = None
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
            if self.info["device"] != "DO":
                self.logger.critical("Incorrect driver circuit. Expecting `DO`, received `{}`".format(info["device"]))
                raise exception("Incorrect hardware configuration")

            # Lock i2c protocol and set output parameters on supported firmware
            if float(info["firmware_version"]) >= 1.95:
                self.protocol_lock = True 
                self.output_parameter_mg_l = True # Enable mg/L output
                self.output_parameter_percent_saturation = False # Disable percent saturation output
            else:
                self.logger.warning("Using old circuit stamp, consider upgrading")
            
            # Enable status led
            self.led = True 

            # Reset device compensation values
            self._sensor_electrical_conductivity_ms_cm = 0
            self._sensor_temperature_celcius = 0
            self._sensor_pressure_kpa = 0

        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates sensor. """
        if self.simulate:
            self.dissolved_oxygen_mg_l = 4.44
            self.health = 100
        else:
            self.update_sensor_compensation_variables()
            self.update_dissolved_oxygen()
            self.update_health()


    def shutdown(self):
        """ Shuts down sensor. Clears reported values, resets sensor health,
            then sets device into sleep mode. """
        self.clear_reported_values()
        self.health = 100
        self.sleep = True


    def update_sensor_compensation_variables(self):
        """ Update sensor compensation variables. """
        self.update_compensation_electrical_conductivity()
        self.update_compensation_temperature()
        self.update_compensation_pressure()

            
    def update_compensation_electrical_conductivity(self):
        """ Update compensation for electrical conductivity. """
        self.logger.debug("Updating compensation for electrical conductivity")

        # Check if there is an electrical conductivity value in shared state to compensate with
        state_ec = self.state_electrical_conductivity_ms_cm
        if state_ec == None:
            self.logger.debug("No electrical conductivity value in shared state to compensate with")
            return

        # Check if electrical conductivity value on sensor requires an update
        delta_ec = self._sensor_electrical_conductivity_ms_cm - state_ec
        if abs(delta_ec) < self._electrical_conductivity_threshold_ms_cm:
            self.logger.debug("Device electrical conductivity compensation does not require update, value within threshold")
            return

        # Update sensor electrical conductivity compensation value
        self.logger.debug("Updating sensor electrical conductivity compensation value")
        self.sensor_electrical_conductivity_ms_cm = state_ec


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


    def update_compensation_pressure(self):
        """ Update compensation for pressure. """
        self.logger.debug("Updating compensation for pressure")

        # Check if there is a pressure value in shared state to compensate with
        _state_pressure_kpa = self.state_pressure_kpa
        if _state_pressure_kpa == None:
            self.logger.debug("No pressure value in shared state to compensate with")
            return

        # Check if pressure value on sensor requires an update
        delta_pressure_kpa = self._sensor_pressure_kpa - _state_pressure_kpa
        if abs(delta_pressure_kpa) < self._pressure_threshold_kpa:
            self.logger.debug("Device pressure compensation does not require update, value within threshold")
            return

        # Update sensor pressure compensation value
        self.logger.debug("Updating sensor pressure compensation value")
        self.sensor_pressure_kpa = _state_pressure_kpa


    def update_dissolved_oxygen(self):
        """ Updates sensor dissolved oxygen. """
        self.logger.debug("Updating dissolved oxygen")
        try:
            # Get dissolved oxygen from device
            response_string = self.process_command("R", processing_seconds=0.6)
            dissolved_oxygen_raw_value = float(response_string)

            # Set significant figures based off error magnitude
            error_magnitude = self.magnitude(self._dissolved_oxygen_accuracy_mg_l)
            significant_figures = error_magnitude * -1
            self.dissolved_oxygen_mg_l = round(dissolved_oxygen_raw_value, significant_figures)

        except:
            self.logger.exception("Bad reading")
            self._missed_readings += 1
    

    def clear_reported_values(self):
        """ Clears reported values. """
        self.dissolved_oxygen_mg_l = None


    @property
    def dissolved_oxygen_mg_l(self):
        """ Gets dissolved oxygen value. """
        return self._dissolved_oxygen_mg_l


    @dissolved_oxygen_mg_l.setter
    def dissolved_oxygen_mg_l(self, value):
        """ Safely updates dissolved oxygen value in environment state each 
            time it is changed. """   
        self.logger.debug("Dissolved oxygen: {} mg/L".format(value))    
        self._dissolved_oxygen_mg_l = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.dissolved_oxygen_name, value)


    @property
    def state_electrical_conductivity_ms_cm(self):
        """ Gets electrical conductivity stored in shared state. """
        if self.electrical_conductivity_name in self.state.environment["sensor"]["reported"]:
            electrical_conductivity_ms_cm = self.state.environment["sensor"]["reported"][self.electrical_conductivity_name]
            if electrical_conductivity_ms_cm != None:
                return float(electrical_conductivity_ms_cm)


    @property
    def sensor_electrical_conductivity_ms_cm(self):
        """ Gets device compensation electrical conductivity value. """
        return self._sensor_electrical_conductivity_ms_cm


    @sensor_electrical_conductivity_ms_cm.setter
    def sensor_electrical_conductivity_ms_cm(self, value):
        """ Sets device electrical conductivity compensation value. """   
        self.logger.debug("Setting device compensation electrical conductivity: {} mS/cm".format(value))
        self._sensor_electrical_conductivity_ms_cm = value  
        value = float(value) * 1000 # convert mS/cm to uS/cm
        self.process_command("S,{}".format(value), processing_seconds=0.3)


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
    def state_pressure_kpa(self):
        """ Gets pressure stored in shared state. """
        if self.pressure_name in self.state.environment["sensor"]["reported"]:
            pressure_kpa = self.state.environment["sensor"]["reported"][self.pressure_name]
            if pressure_kpa != None:
                return float(pressure_kpa)


    @property
    def sensor_pressure_kpa(self):
        """ Gets sensor compensation pressure value. """
        return self._sensor_pressure_kpa


    @sensor_pressure_kpa.setter
    def sensor_pressure_kpa(self, value):
        """ Sets sensor pressure compensation value. """   
        self.logger.debug("Setting device compensation pressure: {} kPa".format(value))
        self._sensor_pressure_kpa = value  
        self.process_command("P,{}".format(value), processing_seconds=0.3)


    @property
    def output_parameter_mg_l(self):
        """ Gets output parameter mg/L state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
        if response_message != None:
            if "mg" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_mg_l.setter
    def output_parameter_mg_l(self, value):
        """ Sets output parameter mg/L state. """ 
        if value:  
            self.process_command("O,mg,1", processing_seconds=0.3)
        else:
            self.process_command("O,mg,0", processing_seconds=0.3)


    @property
    def output_parameter_percent_saturation(self):
        """ Gets output parameter percent saturation state. """
        response_message = self.process_command("O,?", processing_seconds=0.3)
        if response_message != None:
            if "%" in response_message:
                return True
            else:
                return False
        else:
            return None


    @output_parameter_percent_saturation.setter
    def output_parameter_percent_saturation(self, value):
        """ Sets output parameter percent saturations state. """ 
        if value:  
            self.process_command("O,%,1", processing_seconds=0.3)
        else:
            self.process_command("O,%,0", processing_seconds=0.3)