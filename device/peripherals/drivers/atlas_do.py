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
    """ Atlas dissolved oxygen sensor. """

    # Initialize reported sensor parameters
    _dissolved_oxygen_mg_l = None
    _dissolved_oxygen_accuracy_mg_l = 0.05

    # Initialize compensation sensor parameters
    _electrical_conductivity_threshold_ms_cm = 0.1
    _temperature_threshold_celcius = 0.1
    _pressure_threshold_kpa = 0.1

    # Initialize sampling interval parameters
    _min_sampling_interval_seconds = 2
    _default_sampling_interval_seconds = 5


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """
        
        # Instantiate parent class
        super().__init__(*args, **kwargs)
        
        # Initialize reported sensor variable names
        self.dissolved_oxygen_name = self.parameters["variables"]["sensor"]["dissolved_oxygen_mg_l"]

        # Initialize compensation sensor variable names
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

        try:
            # Set firmware dependent settings
            if self._firmware_version >= 1.95:
                self.enable_protocol_lock()
                self.enable_mg_l_output()
                self.disable_percent_saturation_output()
            else:
                self.logger.warning("Using old circuit stamp, consider upgrading")
            
            # Set firmware independent settings
            self.enable_led()
            self.logger.debug("Successfully setup sensor")
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates sensor. """
        self.update_sensor_compensation_variables()
        self.update_dissolved_oxygen()
        self.update_health()


    def reset(self):
        """ Resets sensor. """
        self.logger.info("Resetting sensor")

        # Clear reported values
        self.clear_reported_values()
        self.logger.debug("Successfully reset sensor")


    def shutdown(self):
        """ Shuts down sensor. """
        self.logger.info("Shutting down sensor")

        # Clear reported values
        self.clear_reported_values()

        # Send enable sleep command to sensor hardware
        try:
            self.enable_sleep_mode()
            self.logger.debug("Successfully shutdown sensor")
        except:
            self.logger.exception("Sensor shutdown failed")
            self.mode = Modes.ERROR


############################# Main Helper Functions ###########################


    def perform_initial_health_check(self, retry=False):
        """ Performs initial health check by reading device status. """
        try:
            sensor_type, self._firmware_version = self.read_info()
            if sensor_type != "DO":
                self.logger.critical("Incorrect circuit stamp. Expecting `DO`, received `{}`".format(sensor_type))
                raise Exception("Incorrect circuit stamp type")
            else:
                self.logger.debug("Passed initial health check")
        except:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR


    def update_sensor_compensation_variables(self):
        """ Update sensor compensation variables. """
        self.update_compensation_electrical_conductivity()
        self.update_compensation_temperature()
        self.update_compensation_pressure()

            
    def update_compensation_electrical_conductivity(self):
        """ Update compensation for electrical conductivity. """

        # Don't update compensation electrical conductivity from calibrate mode
        if self.mode == Modes.CALIBRATE:
            self.logger.debug("No need to update compensation electrical conductivity when in CALIBRATE mode")
            return

        # Check if there is an electrical conductivity value in shared state to compensate with
        electrical_conductivity_ms_cm = self.electrical_conductivity_ms_cm
        if electrical_conductivity_ms_cm == None:
            self.logger.debug("No electrical conductivity value in shared state to compensate with")
            return

        # Check if electrical conductivity value on sensor requires an update
        electrical_conductivity_delta_ms_cm = abs(self._prev_electrical_conductivity_ms_cm - electrical_conductivity_ms_cm)
        if electrical_conductivity_delta_ms_cm < self._electrical_conductivity_threshold_ms_cm:
            self.logger.debug("Device electrical conductivity compensation does not require update, value within threshold")
            return

        # Update sensor conductivity compensation value
        self._electrical_conductivity_ms_cm = electrical_conductivity_ms_cm
        try:
            self.set_compensation_electrical_conductivity(electrical_conductivity_ms_cm)
        except:
            self.logger.warning("Unable to set sensor compensation electrical conductivity")


    def update_compensation_temperature(self):
        """ Update compensation for temperature. """

        # Don't update compensation temperature from calibrate mode
        if self.mode == Modes.CALIBRATE:
            self.logger.debug("No need to update compensation temperature when in CALIBRATE mode")
            return

        # Check if there is a temperature value in shared state to compensate with
        temperature_celcius = self.temperature_celcius
        if temperature_celcius == None:
            self.logger.debug("No temperature value in shared state to compensate with")
            return

        # Check if temperature value on sensor requires an update
        temperature_delta_temp = abs(self._prev_temperature_celcius - temperature_celcius)
        if temperature_delta_celcius < self._temperature_threshold_celcius:
            self.logger.debug("Device temperature compensation does not require update, value within threshold")
            return

        # Update sensor temperature compensation value
        self._prev_temperature_celcius = temperature_celcius
        try:
            self.set_compensation_temperature(temperature_celcius)
        except:
            self.logger.warning("Unable to set sensor compensation temperature")


    def update_compensation_pressure(self):
        """ Update compensation for pressure. """

        # Don't update compensation pressure from calibrate mode
        if self.mode == Modes.CALIBRATE:
            self.logger.debug("No need to update compensation pressure when in CALIBRATE mode")
            return

        # Check if there is a pressure value in shared state to compensate with
        pressure_kpa = self.pressure_kpa
        if pressure_kpa == None:
            self.logger.debug("No pressure value in shared state to compensate with")
            return

        # Check if pressure value on sensor requires an update
        pressure_delta_kpa = abs(self._prev_pressure_kpa - pressure_kpa)
        if pressure_delta_kpa < self._pressure_threshold_kpa:
            self.logger.debug("Device pressure compensation does not require update, value within threshold")
            return

        # Update sensor pressure compensation value
        self._prev_pressure_kpa = pressure_kpa
        try:
            self.set_compensation_pressure(pressure_kpa)
        except:
            self.logger.warning("Unable to set sensor compensation pressure")


    def update_dissolved_oxygen(self):
        """ Updates sensor dissolved oxygen. """
        self.logger.debug("Getting dissolved oxygen")
        try:
            self.dissolved_oxygen_mg_l = self.read_dissolved_oxygen_mg_l()
        except:
            self.logger.exception("Unable to update dissolved oxygen, bad reading")
            self._missed_readings += 1
    

    def clear_reported_values(self):
        """ Clears reported values. """
        self.dissolved_oxygen_mg_l = None


################# Peripheral Specific Event Functions #########################


    def process_peripheral_specific_event(self, request_type, value):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        # Execute request
        if request_type == "Enable Calibration Mode":
            self.response = self.process_enable_calibration_mode_event()
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


    def process_enable_calibration_mode_event(self):
        """ Processes calibrate event. """
        self.logger.debug("Processing enable calibration mode event")

        if self.mode == Modes.CALIBRATE:
            response = {"status": 200, "message": "Already in calibration mode!"}
        else:
            self.mode = Modes.CALIBRATE
            response = {"status": 200, "message": "Enabling calibration mode!"}
        return response



############################# Hardware Interactions ###########################


    def read_info(self):
        """ Gets info about sensor type and firmware version. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading info from hardware")
            sensor_type = "DO"
            firmware_version = 2.0
            return sensor_type, firmware_version

        # Sensor is not simulated
        self.logger.debug("Reading info from hardware")

        # Send read info command to device
        response_message = self.process_command("i", processing_seconds=0.3)
        command, sensor_type, firmware_version = response_message.split(",")
        return sensor_type, float(firmware_version)


    def read_dissolved_oxygen_mg_l(self):
        """ Reads dissolved oxygen from sensor, sets significant 
            figures based off error magnitude, returns value in mg/L. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading dissolved oxygen value from hardware")
            dissolved_oxygen_mg_l = 10.3
            self.logger.debug("dissolved_oxygen_mg_l = {}".format(dissolved_oxygen_mg_l))
            return dissolved_oxygen_mg_l
        
        # Sensor is not simulated
        self.logger.debug("Reading dissolved oxygen value from hardware")

        # Get dissolved oxygen reading from hardware
        # Assumed dissolved oxygen is only enabled output
        response_string = self.process_command("R", processing_seconds=0.6)
        dissolved_oxygen_raw_value = float(response_string)

        # Set significant figures based off error magnitude
        error_magnitude = self.magnitude(self._dissolved_oxygen_accuracy_mg_l)
        significant_figures = error_magnitude * -1
        dissolved_oxygen_mg_l = round(dissolved_oxygen_raw_value, significant_figures)

        # Return dissolved oxygen value
        self.logger.debug("dissolved_oxygen_mg_l = {}".format(dissolved_oxygen_mg_l))
        return dissolved_oxygen_mg_l


    def set_compensation_temperature_celcius(self, temperature_celcius):
        """ Commands sensor to set compensation temperature. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating setting compensation temperature in hardware")
            return 

        # Sensor not simulated
        self.logger.debug("Setting compensation temperature")
        
        # Send update compensation temperature command
        command = "T,{}".format(temperature_celcius)
        self.process_command(command, processing_seconds=0.3)


    def set_compensation_electrical_conductivity_ms_cm(self, electrical_conductivity_ms_cm):
        """ Commands sensor to set compensation electrical conductivity. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating setting compensation electrical conductivity in hardware")
            return 

        # Sensor not simulated
        self.logger.debug("Setting compensation electrical conductivity")
        
        # Send update compensation electrical conductivity command
        self._sensor_electrical_conductivity_ms_cm = value  
        value = float(value) * 1000 # convert mS/cm to uS/cm
        self.process_command("S,{}".format(value), processing_seconds=0.3)


    def set_compensation_pressure_kpa(self, pressure_kpa):
        """ Commands sensor to set compensation pressure. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating setting compensation pressure in hardware")
            return 

        # Sensor not simulated
        self.logger.debug("Setting compensation pressure")
        
        # Send update compensation temperature command
        command = "P,{}".format(pressure_kpa)
        self.process_command(command, processing_seconds=0.3)


    def enable_mg_l_output(self):
        """ Commands sensor to enable mg/L output when reporting 
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating enabling mg/L output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Enabling mg/L output in hardware")

        # Send enable mg/L command to hardware
        self.process_command("O,mg,1", processing_seconds=0.3)


    def disable_mg_l_output(self):
        """ Commands sensor to disable mg/L output when reporting 
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating disabling mg/L output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Disabling mg/L output in hardware")

        # Send enable mg/L command to hardware
        self.process_command("O,mg,0", processing_seconds=0.3)


    def enable_percent_saturation_output(self):
        """ Commands sensor to enable percent saturation output when reporting 
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating enabling percent saturation output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Enabling percent saturation output in hardware")

        # Send enable percent saturation command to hardware
        self.process_command("O,%,1", processing_seconds=0.3)


    def disable_percent_saturation_output(self):
        """ Commands sensor to disable percent saturation output when reporting 
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating disabling percent saturation output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Disabling percent saturation output in hardware")

        # Send enable percent saturation command to hardware
        self.process_command("O,%,0", processing_seconds=0.3)



########################## Setter & Getter Functions ##########################


    @property
    def dissolved_oxygen_mg_l(self):
        """ Gets dissolved oxygen value. """
        return self._dissolved_oxygen_mg_l


    @dissolved_oxygen_mg_l.setter
    def dissolved_oxygen_mg_l(self, value):
        """ Safely updates dissolved oxygen value in environment state each 
            time it is changed. """   
        self._dissolved_oxygen_mg_l = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.dissolved_oxygen_name, value)


    @property
    def pressure_kpa(self):
        """ Gets pressure stored in shared state. """
        if self.pressure_name in self.state.environment["sensor"]["reported"]:
            pressure_kpa = self.state.environment["sensor"]["reported"][self.pressure_name]
            if pressure_kpa != None:
                return float(pressure_kpa)


    @property
    def temperature_celcius(self):
        """ Gets temperature stored in shared state. """
        if self.temperature_name in self.state.environment["sensor"]["reported"]:
            temperature_celcius = self.state.environment["sensor"]["reported"][self.temperature_name]
            if temperature_celcius != None:
                return float(temperature_celcius)


    @property
    def electrical_conductivity_ms_cm(self):
        """ Gets electrical conductivity stored in shared state. """
        if self.electrical_conductivity_name in self.state.environment["sensor"]["reported"]:
            electrical_conductivity_ms_cm = self.state.environment["sensor"]["reported"][self.electrical_conductivity_name]
            if electrical_conductivity_ms_cm != None:
                return float(electrical_conductivity_ms_cm)