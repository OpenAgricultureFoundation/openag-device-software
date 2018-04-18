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
    _prev_temperature_celcius = 0


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor names. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize reported sensor names
        self.electrical_conductivity_name = self.parameters["variables"]["sensor"]["electrical_conductivity_ms_cm"]

        # Initialize compensation sensor names
        self.temperature_name = self.parameters["variables"]["compensation"]["temperature_celcius"]

        # TODO: Load this in from device config file
        self.setup_uuid = "349fba97-1f23-48c7-8fe7-1ea717915dd4"


    @property
    def electrical_conductivity_ms_cm(self):
        """ Gets electrical conductivity value. """
        return self._electrical_conductivity_ms_cm


    @electrical_conductivity_ms_cm.setter
    def electrical_conductivity_ms_cm(self, value):
        """ Safely updates electrical conductivity in shared state. If sensor 
            is in calibrate mode only update peripheral shared state, else
            updates peripheral and environment shared state. """   
        self.logger.debug("Electrical conductivity: {} mS/cm".format(value))    
        self._electrical_conductivity_ms_cm = value
        
        # Update peripheral and/or environment shared state
        if self.mode == Modes.CALIBRATE:
            self.report_peripheral_value(self.electrical_conductivity_name, value)
        else:
            self.report_peripheral_value(self.electrical_conductivity_name, value)
            self.report_sensor_value(self.name, self.electrical_conductivity_name, value)


    @property
    def temperature_celcius(self):
        """ Gets temperature stored in shared state. """
        if self.temperature_name in self.state.environment["sensor"]["reported"]:
            temperature_celcius = self.state.environment["sensor"]["reported"][self.temperature_name]
            if temperature_celcius != None:
                return float(temperature_celcius)


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


    def perform_initial_health_check(self, retry=False):
        """ Performs initial health check by reading device status. """
        
        # Check for simulated sensor
        if self.simulate:
            self.logger.info("Simulating initial health check")
            return
        else:
            self.logger.info("Performing initial health check")

        # Check sensor health
        try:
            sensor_type, self._firmware_version = self.get_info()
            if sensor_type != "EC":
                self.logger.critical("Incorrect circuit stamp. Expecting `EC`, received `{}`".format(sensor_type))
                raise Exception("Incorrect circuit stamp type")
            else:
                self.logger.debug("Passed initial health check")
        except:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR
     

    def setup(self):
        """ Sets up sensor. Programs device operation parameters into 
            sensor driver circuit. Transitions to NORMAL on completion 
            and ERROR on error. """
        
        # Check for simulated sensor
        if self.simulate:
            self.logger.info("Simulating sensor setup")
            return
        else:
            self.logger.debug("Setting up sensor")

        # Setup sensor
        try:
            # Set firmware dependent settings
            if self._firmware_version >= 1.95:
                self.enable_protocol_lock()
                self.enable_electrical_conductivity_output()
                self.disable_total_dissolved_solids_output()
                self.disable_salinity_output()
                self.disable_specific_gravity_output()
            else:
                self.logger.warning("Using old circuit stamp, consider upgrading")
            
            # Set firmware independent settings
            self.enable_led()
            self.set_probe_type("1.0")
            self.logger.debug("Successfully setup sensor")
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates sensor when in normal mode. """
        if self.simulate:
            self.electrical_conductivity_ms_cm = 3.33
            self.health = 100
        else:
            self.update_compensation_temperature()
            self.update_electrical_conductivity()
            self.update_health()


    def update_electrical_conductivity(self):
        """ Updates sensor electrical conductivity. """
        self.logger.debug("Getting electrical conductivity")
        try:
            self.electrical_conductivity_ms_cm = self.get_electrical_conductivity()
        except:
            self.logger.exception("Unable to get electrical conductivity")
            self._missed_readings += 1


    def update_compensation_temperature(self):
        """ Updates sensor compensation temperature on if temperature value exists
            in shared state. Only sets on new values greater than threshold. """

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
        temperature_delta_celcius = abs(self._prev_temperature_celcius - temperature_celcius)
        if temperature_delta_celcius < self._temperature_threshold_celcius:
            self.logger.debug("Device temperature compensation does not require update, value within threshold")
            return

        # Update sensor temperature compensation value
        self._prev_temperature_celcius = temperature_celcius
        try:
            self.set_compensation_temperature(temperature_celcius)
        except:
            self.logger.exception("Unable to set compensation temperature")


    def shutdown(self):
        """ Shuts down sensor. Clears reported values, then sets sensor into 
            sleep mode. """
        self.clear_reported_values()
        self.enable_sleep_mode()
    

    def clear_reported_values(self):
        """ Clears reported values. """
        self.electrical_conductivity_ms_cm = None



################################## Events #####################################

    def process_event(self, request):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        self.logger.debug("Processing event request: `{}`".format(request))

        # Get request parameters
        try:
            request_type = request["type"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            self.response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}

        # Execute request
        if request_type == "Reset":
            self.response = self.process_reset_event(request)
        elif request_type == "Enable Calibration Mode":
            self.response = self.process_enable_calibration_mode_event(request)
        elif request_type == "Dry Calibration":
            self.response = self.process_dry_calibration_event(request)
        elif request_type == "Single Point Calibration":
            self.response = self.process_single_point_calibration_event(request)
        else:
            message = "Unknown event request type"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


    def process_reset_event(self, request):
        """ Processes reset event. """
        self.logger.debug("Processing reset event")
        self.mode = Modes.RESET
        response = {"status": 200, "message": "Resetting peripheral"}
        return response


    def process_enable_calibration_mode_event(self, request):
        """ Processes calibrate event. """
        self.logger.debug("Processing enable calibration mode event")

        # return {"status": 400, "message": "This is a test"}

        if self.mode == Modes.CALIBRATE:
            response = {"status": 200, "message": "Already in calibration mode"}
        else:
            self.mode = Modes.CALIBRATE
            response = {"status": 200, "message": "Enabling calibration mode"}
        return response



    def process_dry_calibration_event(self, request):
        """ Processes dry calibration event. Verifies sensor in calibrate mode,
            then takes dry calibration reading. """
        self.logger.debug("Processing dry calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take dry calibration"}
            return response

        # Execute request
        try:
            self.take_dry_calibration_reading()
            response = {"status": 200, "message": "Successfully took dry calibration reading"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take dry calibration reading")
            response = {"status": 500, "message": "Unable to take dry calibration reading: {}".format(e)}
            return response


    def process_single_point_calibration_event(self, request):
        """ Processes single point calibration event. Gets request parameters,
            executes request, returns response. """
        self.logger.debug("Processing single point calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration."}
            return response

        # Get request parameters
        try:
            electrical_conductivity_ms_cm = request["value"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response

        # Execute request
        try:
            self.take_single_point_calibration_reading(electrical_conductivity_ms_cm)
            response = {"status": 200, "message": "Set single point calibration"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take single point calibration reading")
            response = {"status": 500, "message": "Unable to take single point calibration reading: {}".format(e)}
            return response


############################# Hardware Interactions ###########################


    def get_electrical_conductivity(self):
        """ Gets electrical conductivity reading from sensor, sets significant 
            figures based off error magnitude, returns value in mS/cm. """
        self.logger.debug("Getting electrical conductivity")

        # Get electrical conductivity reading from sensor
        # Assumes electrical conductivity is only device output
        response_string = self.process_command("R", processing_seconds=0.6)
        electrical_conductivity_us_cm = float(response_string)
        electrical_conductivity_ms_cm = electrical_conductivity_us_cm / 1000

        # Set significant figures based off error magnitude
        error_value = electrical_conductivity_ms_cm * self._electrical_conductivity_accuracy_percent / 100
        error_magnitude = self.magnitude(error_value)
        significant_figures = error_magnitude * -1

        # Return value in mS/cm
        return round(electrical_conductivity_ms_cm, significant_figures)


    def set_compensation_temperature(self, temperature_celcius):
        """ Commands sensor to set compensation temperature. """
        self.logger.debug("Setting compensation temperature")
        command = "T,{}".format(temperature_celcius)
        self.process_command(command, processing_seconds=0.3)


    def enable_electrical_conductivity_output(self):
        """ Commands sensor to enable electrical conductivity output when 
            reporting readings. """
        self.logger.info("Enabling electrical conductivity output")
        self.process_command("O,EC,1", processing_seconds=0.3)


    def disable_electrical_conductivity_output(self):
        """ Commands sensor to disable electrical conductivity output when 
            reporting readings. """
        self.logger.info("Disabling electrical conductivity output")
        self.process_command("O,EC,0", processing_seconds=0.3)


    def enable_total_dissolved_solids_output(self):
        """ Commands sensor to enable total dissolved solids output when 
            reporting readings. """
        self.logger.info("Enabling total dissolved solids output")
        self.process_command("O,TDS,1", processing_seconds=0.3)


    def disable_total_dissolved_solids_output(self):
        """ Commands sensor to disable total dissolved solids output when 
            reporting readings. """
        self.logger.info("Disabling total dissolved solids output")
        self.process_command("O,TDS,0", processing_seconds=0.3)


    def enable_salinity_output(self):
        """ Commands sensor to enable salinity output when reporting 
            readings. """
        self.logger.info("Enabling salinity output")
        self.process_command("O,S,1", processing_seconds=0.3)


    def disable_salinity_output(self):
        """ Commands sensor to disable salinity output when reporting 
            readings. """
        self.logger.info("Disabling salinity output")
        self.process_command("O,S,0", processing_seconds=0.3)


    def enable_specific_gravity_output(self):
        """ Commands sensor to enable specific gravity output when reporting
            readings. """
        self.logger.info("Enabling specific gravity output")
        self.process_command("O,SG,1", processing_seconds=0.3)


    def disable_specific_gravity_output(self):
        """ Commands sensor to disable specific gravity output when reporting
            readings. """
        self.logger.info("Disabling specific gravity output")
        self.process_command("O,SG,0", processing_seconds=0.3)


    def set_probe_type(self, value):
        """ Commands sensor to set probe type to value. """
        self.logger.info("Setting probe type")
        self.process_command("K,{}".format(value), processing_seconds=0.3)


    def take_dry_calibration_reading(self):
        """ Commands sensor to take a dry calibration reading. """
        self.logger.info("(FAKE) Taking dry calibration reading")
        #self.process_command("Cal,dry", processing_seconds=0.6)


    def take_single_point_calibration_reading(self, electrical_conductivity_ms_cm):
        """ Commands sensor to take a single point calibration reading. """
        self.logger.info("(FAKE) Taking single point calibration reading.")
        # electrical_conductivity_us_cm = electrical_conductivity_ms_cm * 1000
        # command = "Cal,{}".format(electrical_conductivity_us_cm)
        # self.process_command(command, processing_seconds=0.6)


    def take_low_point_calibration_reading(self, electrical_conductivity_ms_cm):
        """ Commands sensor to take a low point calibration reading. """
        self.logger.info("(FAKE) Taking low point calibration reading.")
        # electrical_conductivity_us_cm = electrical_conductivity_ms_cm * 1000
        # command = "Cal,low,{}".format(electrical_conductivity_us_cm)
        # self.process_command(command, processing_seconds=0.6)


    def take_high_point_calibration_reading(self, electrical_conductivity_ms_cm):
        """ Commands sensor to take a high point calibration reading. """
        self.logger.info("(FAKE) Taking high point calibration reading.")
        # electrical_conductivity_us_cm = electrical_conductivity_ms_cm * 1000
        # command = "Cal,high,{}".format(electrical_conductivity_us_cm)
        # self.process_command(command, processing_seconds=0.6)