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
    """ Atlas electrical conductivity sensor. """

    # Initialize reported sensor parameters 
    _electrical_conductivity_ms_cm = None
    _electrical_conductivity_accuracy_percent = 2

    # Initialize compensation sensor parameters
    _temperature_threshold_celcius = 0.1
    _prev_temperature_celcius = 0

    # Initialize sampling interval parameters
    _min_sampling_interval_seconds = 2
    _default_sampling_interval_seconds = 5


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor names. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize sensor variable names
        self.electrical_conductivity_name = self.parameters["variables"]["sensor"]["electrical_conductivity_ms_cm"]
        self.compensation_temperature_name = self.parameters["variables"]["compensation"]["temperature_celcius"]


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
            self.logger.Resetexception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates sensor when in normal mode. """
        self.update_compensation_temperature()
        self.update_electrical_conductivity()
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
            if sensor_type != "EC":
                self.logger.critical("Incorrect circuit stamp. Expecting `EC`, received `{}`".format(sensor_type))
                raise Exception("Incorrect circuit stamp type")
            else:
                self.logger.debug("Passed initial health check")
        except:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR


    def update_electrical_conductivity(self):
        """ Updates sensor electrical conductivity. """
        self.logger.debug("Getting electrical conductivity")
        try:
            self.electrical_conductivity_ms_cm = self.read_electrical_conductivity_ms_cm()
        except:
            self.logger.exception("Unable to update electrical conductivity, bad reading")
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
            self.set_compensation_temperature_celcius(temperature_celcius)
        except:
            self.logger.warning("Unable to set sensor compensation temperature")


    def clear_reported_values(self):
        """ Clears reported values. """
        self.electrical_conductivity_ms_cm = None


################# Peripheral Specific Event Functions #########################


    def process_peripheral_specific_event(self, request):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        # Execute request
        if request["type"] == "Enable Calibration Mode":
            self.response = self.process_enable_calibration_mode_event()
        elif request["type"] == "Dry Calibration":
            self.response = self.process_dry_calibration_event()
        elif request["type"] == "Single Point Calibration":
            self.response = self.process_single_point_calibration_event(request)
        elif request["type"] == "Low Point Calibration":
            self.response = self.process_low_point_calibration_event(request)
        elif request["type"] == "High Point Calibration":
            self.response = self.process_high_point_calibration_event(request)
        elif request["type"] == "Clear Calibration":
            self.response = self.process_clear_calibration_event()
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


    def process_dry_calibration_event(self):
        """ Processes dry calibration event. Verifies sensor in calibrate mode,
            then takes dry calibration reading. """
        self.logger.debug("Processing dry calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take dry calibration!"}
            return response

        # Execute request
        try:
            self.take_dry_calibration_reading()
            response = {"status": 200, "message": "Successfully took dry calibration reading!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take dry calibration reading!")
            response = {"status": 500, "message": "Unable to take dry calibration reading: {}".format(e)}
            return response


    def process_single_point_calibration_event(self, request):
        """ Processes single point calibration event. Gets request parameters,
            executes request, returns response. """
        self.logger.debug("Processing single point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!."}
            return response

        # Execute request
        try:
            self.take_single_point_calibration_reading(value)
            response = {"status": 200, "message": "Set single point calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take single point calibration reading")
            response = {"status": 500, "message": "Unable to take single point calibration reading: {}!".format(e)}
            return response


    def process_low_point_calibration_event(self, request):
        """ Processes low point calibration event. Gets request parameters,
            executes request, returns response. """
        self.logger.debug("Processing low point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take low point calibration!."}
            return response

        # Execute request
        try:
            self.take_low_point_calibration_reading(value)
            response = {"status": 200, "message": "Set low point calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take low point calibration reading")
            response = {"status": 500, "message": "Unable to take low point calibration reading: {}!".format(e)}
            return response


    def process_high_point_calibration_event(self, request):
        """ Processes high point calibration event. Gets request parameters,
            executes request, returns response. """
        self.logger.debug("Processing high point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take high point calibration!."}
            return response

        # Execute request
        try:
            self.take_high_point_calibration_reading(value)
            response = {"status": 200, "message": "Set high point calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take high point calibration reading")
            response = {"status": 500, "message": "Unable to take high point calibration reading: {}!".format(e)}
            return response


    def process_clear_calibration_event(self):
        """ Processes clear calibration event. """
        self.logger.debug("Processing clear calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to clear calibration!."}
            return response

        # Execute request
        try:
            self.clear_calibration_data()
            response = {"status": 200, "message": "Cleared calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to clear calibration reading")
            response = {"status": 500, "message": "Unable to clear calibration reading: {}!".format(e)}
            return response


############################# Hardware Interactions ###########################

    def read_info(self):
        """ Gets info about sensor type and firmware version. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading info from hardware")
            sensor_type = "EC"
            firmware_version = 2.0
            return sensor_type, firmware_version

        # Sensor is not simulated
        self.logger.debug("Reading info from hardware")

        # Send read info command to device
        response_message = self.process_command("i", processing_seconds=0.3)
        command, sensor_type, firmware_version = response_message.split(",")
        return sensor_type, float(firmware_version)


    def read_electrical_conductivity_ms_cm(self):
        """ Reads electrical conductivity from sensor, sets significant 
            figures based off error magnitude, returns value in mS/cm. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading electrical conductivity value from hardware")
            electrical_conductivity_ms_cm = 3.14
            self.logger.debug("electrical_conductivity_ms_cm = {}".format(electrical_conductivity_ms_cm))
            return electrical_conductivity_ms_cm
        
        # Sensor is not simulated
        self.logger.debug("Reading electrical conductivity value from hardware")

        # Get electrical conductivity reading from hardware
        # Assumes electrical conductivity is only enabled output
        response_string = self.process_command("R", processing_seconds=0.6)
        electrical_conductivity_us_cm = float(response_string)
        electrical_conductivity_ms_cm = electrical_conductivity_us_cm / 1000

        # Set significant figures based off error magnitude
        error_value = electrical_conductivity_ms_cm * self._electrical_conductivity_accuracy_percent / 100
        error_magnitude = self.magnitude(error_value)
        significant_figures = error_magnitude * -1
        electrical_conductivity_ms_cm = round(electrical_conductivity_ms_cm, significant_figures)

        # Return electical conductivity value
        self.logger.debug("electrical_conductivity_ms_cm = {}".format(electrical_conductivity_ms_cm))
        return electrical_conductivity_ms_cm


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


    def enable_electrical_conductivity_output(self):
        """ Commands sensor to enable electrical conductivity output when 
            reporting readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating enabling electrical conductivity output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Enabling electrical conductivity output in hardware")

        # Send enable ec command to hardware
        self.process_command("O,EC,1", processing_seconds=0.3)


    def disable_electrical_conductivity_output(self):
        """ Commands sensor to disable electrical conductivity output when 
            reporting readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating disabling electrical conductivity output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Disabling electrical conductivity output in hardware")

        # Send disable ec command to hardware
        self.process_command("O,EC,0", processing_seconds=0.3)


    def enable_total_dissolved_solids_output(self):
        """ Commands sensor to enable total dissolved solids output when 
            reporting readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating enabling total dissolbed solids output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Enabling total dissolved solids output in hardware")

        # Send enable tds command to hardware
        self.process_command("O,TDS,1", processing_seconds=0.3)


    def disable_total_dissolved_solids_output(self):
        """ Commands sensor to disable total dissolved solids output when 
            reporting readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating disabling total dissolbed solids output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Disabling total dissolved solids output in hardware")

        # Send disable tds output command to hardware
        self.process_command("O,TDS,0", processing_seconds=0.3)


    def enable_salinity_output(self):
        """ Commands sensor to enable salinity output when reporting 
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating enabling salinity output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Enabling salinity output in hardware")

        # Send enable salinity command to hardware
        self.process_command("O,S,1", processing_seconds=0.3)


    def disable_salinity_output(self):
        """ Commands sensor to disable salinity output when reporting 
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating disabling salinity output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Disabling salinity output in hardware")

        # Send disable salinity command to hardware
        self.process_command("O,S,0", processing_seconds=0.3)


    def enable_specific_gravity_output(self):
        """ Commands sensor to enable specific gravity output when reporting
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating enabling specific gravity output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Enabling specific gravity output in hardware")

        # Send enable specific gravity output to hardware
        self.process_command("O,SG,1", processing_seconds=0.3)


    def disable_specific_gravity_output(self):
        """ Commands sensor to disable specific gravity output when reporting
            readings. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating disabling specific gravity output in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Disabling specific gravity output in hardware")

        # Send disable specific gravity output to hardware
        self.process_command("O,SG,0", processing_seconds=0.3)


    def set_probe_type(self, value):
        """ Commands sensor to set probe type to value. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating setting probe type in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Setting probe type in hardware")

        # Send set probe type command to hardware
        self.process_command("K,{}".format(value), processing_seconds=0.3)


    def take_dry_calibration_reading(self):
        """ Commands sensor to take a dry calibration reading. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking dry calibration reading in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Taking dry calibration reading in hardware")

        # Send take dry calibration command to hardware
        self.process_command("Cal,dry", processing_seconds=0.6)


    def take_single_point_calibration_reading(self, electrical_conductivity_ms_cm):
        """ Commands sensor to take a single point calibration reading. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking single point calibration reading in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Taking single point calibration reading in hardware.")

        # Send take single point calibration command to hardware
        electrical_conductivity_us_cm = electrical_conductivity_ms_cm * 1000
        command = "Cal,{}".format(electrical_conductivity_us_cm)
        self.process_command(command, processing_seconds=0.6)


    def take_low_point_calibration_reading(self, electrical_conductivity_ms_cm):
        """ Commands sensor to take a low point calibration reading. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking low point calibration reading in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Taking low point calibration reading in hardware.")

        # Send take low point calibration command to hardware
        electrical_conductivity_us_cm = electrical_conductivity_ms_cm * 1000
        command = "Cal,low,{}".format(electrical_conductivity_us_cm)
        self.process_command(command, processing_seconds=0.6)


    def take_high_point_calibration_reading(self, electrical_conductivity_ms_cm):
        """ Commands sensor to take a high point calibration reading. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking high point calibration reading in hardware")
            return 

        # Sensor is not simulated
        self.logger.info("Taking high point calibration reading in hardware.")
        
        # Send take high point calibration command to hardware
        electrical_conductivity_us_cm = electrical_conductivity_ms_cm * 1000
        command = "Cal,high,{}".format(electrical_conductivity_us_cm)
        self.process_command(command, processing_seconds=0.6)


    def clear_calibration_data(self):
        """ Commands sensor to clear calibration data. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking high point calibration reading in hardware")
            return

        # Sensor is not simulated
        self.logger.info("Taking high point calibration reading in hardware.")

        # Send take high point calibration command to hardware
        self.process_command("Cal,clear", processing_seconds=0.3)



########################## Setter & Getter Functions ##########################


    @property
    def electrical_conductivity_ms_cm(self):
        """ Gets electrical conductivity value. """
        return self._electrical_conductivity_ms_cm


    @electrical_conductivity_ms_cm.setter
    def electrical_conductivity_ms_cm(self, value):
        """ Safely updates electrical conductivity in shared state. If sensor 
            is in calibrate mode only update peripheral shared state, else
            updates peripheral and environment shared state. """   
        self._electrical_conductivity_ms_cm = value
        self.report_peripheral_sensor_value(self.electrical_conductivity_name, value)

        # Update environment if not in calibrate mode
        if self.mode != Modes.CALIBRATE:
            self.report_environment_sensor_value(self.name, self.electrical_conductivity_name, value)


    @property
    def temperature_celcius(self):
        """ Gets temperature stored in shared state. """
        if self.compensation_temperature_name in self.state.environment["sensor"]["reported"]:
            temperature_celcius = self.state.environment["sensor"]["reported"][self.compensation_temperature_name]
            if temperature_celcius != None:
                return float(temperature_celcius)
