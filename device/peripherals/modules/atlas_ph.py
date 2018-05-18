# Import python modules
import logging, time, threading

# Import atlas device parent class
from device.peripherals.classes.atlas import Atlas

# Import device comms
from device.comms.i2c import I2C

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class AtlasPH(Atlas):
    """ Atlas pH sensor. """

    # Initialize sensor parameters
    _potential_hydrogen = None
    _potential_hydrogen_accuracy = 0.002

    # Initialize compensation sensor parameters
    _temperature_threshold_celcius = 0.1

    # Initialize sampling interval parameters
    _min_sampling_interval_seconds = 2
    _default_sampling_interval_seconds = 5


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize reported sensor variable names
        self.potential_hydrogen_name = self.parameters["variables"]["sensor"]["potential_hydrogen"]

        # Initialize compensation sensor variable names
        self.temperature_name = self.parameters["variables"]["compensation"]["temperature_celcius"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.potential_hydrogen = None
        self.health = 100

        # Perform initial health check
        self.check_health(retry=True)


    def setup(self):
        """ Sets up sensor. Programs device operation parameters into 
            sensor driver circuit. Transitions to NORMAL on completion 
            and ERROR on error. """
        self.logger.debug("Setting up sensor")

        try:
            # Set firmware dependent settings
            if self._firmware_version >= 1.95:
                self.enable_protocol_lock()
                # TODO: enable / disable outputs
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
        self.update_compensation_temperature()  # update compensation before pH
        self.update_potential_hydrogen()
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


    ############################# Main Helper Functions #######################


    def check_health(self, retry=False):
        """ Checks health by reading sensor info and verifying correct circuit stamp type. """
        try:
            sensor_type, self._firmware_version = self.read_info()
            if sensor_type != "pH":
                self.logger.critical("Incorrect circuit stamp. Expecting `pH`, received `{}`".format(sensor_type) )
                raise Exception("Incorrect circuit stamp type")
            else:
                self.logger.debug("Passed initial health check")
        except:
            if retry:
                self.logger.info("Retrying health check")
                self.check_health()
            else:
                self.logger.exception("Failed initial health check")
                self.error = Errors.FAILED_HEALTH_CHECK
                self.mode = Modes.ERROR
            return

        # Sensor is healthy
        self.logger.debug("Passed health check")


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
        if self._prev_temperature_celcius != None:
            temperature_delta_celcius = abs(self._prev_temperature_celcius - temperature_celcius)
            if temperature_delta_celcius < self._temperature_threshold_celcius:
                self.logger.debug("Device temperature compensation does not require update, value within threshold")
                return

        # Update sensor temperature compensation value
        self._prev_temperature_celcius = temperature_celcius
        try:
            self.set_compensation_temperature(temperature_celcius)
        except:
            self.logger.warning("Unable to set sensor compensation temperature")


    def update_potential_hydrogen(self):
        """ Updates sensor potential hydrogen. """
        self.logger.debug("Getting potential hydrogen")
        try:
            self.potential_hydrogen = self.read_potential_hydrogen()
        except:
            self.logger.exception("Unable to update potential_hydrogen, bad reading")
            self._missed_readings += 1


    def clear_reported_values(self):
        """ Clears reported values. """
        self.potential_hydrogen = None


    ################# Peripheral Specific Event Functions #####################


    def process_peripheral_specific_event(self, request):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        # Execute request
        if request["type"] == "Low Point Calibration":
            self.response = self.process_low_point_calibration_event(request)
        elif request["type"] == "Mid Point Calibration":
            self.response = self.process_mid_point_calibration_event(request)
        elif request["type"] == "High Point Calibration":
            self.response = self.process_high_point_calibration_event(request)
        elif request["type"] == "Clear Calibration":
            self.response = self.process_clear_calibration_event()
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


    def process_low_point_calibration_event(self, request):
        """ Processes low point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be within range 0-4. """
        self.logger.debug("Processing low point calibration event")

        # Verify value in request
        try:
            value = int(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {
                "status": 400, "message": "Invalid request parameters: {}".format(e)
            }
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Verify value within valid range
        if value not in range(4, 10):
            error_message = "Invalid request value, not in range 4-10"
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!.",}
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


    def process_mid_point_calibration_event(self, request):
        """ Processes mid point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be in range 4-10. """
        self.logger.debug("Processing mid point calibration event")

        # Verify value in request
        try:
            value = int(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Verify value within valid range
        if value not in range(4, 10):
            error_message = "Invalid request value, not in range 4-10"
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!."}
            return response

        # Execute request
        try:
            self.take_mid_point_calibration_reading(value)
            response = {"status": 200, "message": "Set mid point calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take mid point calibration reading")
            response = {"status": 500, "message": "Unable to take mid point calibration reading: {}!".format(e)}
            return response


    def process_high_point_calibration_event(self, request):
        """ Processes high point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be within range 10-14. """
        self.logger.debug("Processing high point calibration event")

        # Verify value in request
        try:
            value = int(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Verify value within valid range
        if value not in range(10, 14):
            error_message = "Invalid request value, not in range 10-14"
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!."}
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


    ############################# Hardware Interactions #######################


    def read_info(self):
        """ Gets info about sensor type and firmware version. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading info from hardware")
            sensor_type = "pH"
            firmware_version = 2.0
            return sensor_type, firmware_version

        # Sensor is not simulated
        self.logger.debug("Reading info from hardware")

        # Send read info command to device
        response_message = self.process_command("i", processing_seconds=0.6) # was 0.3
        command, sensor_type, firmware_version = response_message.split(",")
        return sensor_type, float(firmware_version)


    def read_potential_hydrogen(self):
        """ Reads potential hydrogen from sensor, sets significant 
            figures based off error magnitude. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading potential hydrogen value from hardware")
            potential_hydrogen = 6.83
            self.logger.debug("potential_hydrogen = {}".format(potential_hydrogen))
            return potential_hydrogen

        # Sensor is not simulated
        self.logger.debug("Reading potential hydrogen value from hardware")

        # Get potential hydrogen reading from hardware
        # Assumed potential hydrogen is only enabled output
        response_string = self.process_command("R", processing_seconds=1.2) # was 0.6
        potential_hydrogen_raw_value = float(response_string)

        # Set significant figures based off error magnitude
        error_magnitude = self.magnitude(self._potential_hydrogen_accuracy)
        significant_figures = error_magnitude * -1
        potential_hydrogen = round(potential_hydrogen_raw_value, significant_figures)

        # Return potential hydrogen value
        self.logger.debug("potential_hydrogen = {}".format(potential_hydrogen))
        return potential_hydrogen


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

    def take_low_point_calibration_reading(self, value):
        """ Commands sensor to take a low point calibration reading. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking low point calibration reading in hardware")
            return

        # Sensor is not simulated
        self.logger.info("Taking low point calibration reading in hardware.")

        # Send take low point calibration command to hardware
        command = "Cal,low,{}".format(value)
        self.process_command(command, processing_seconds=0.9)

    def take_mid_point_calibration_reading(self, value):
        """ Commands sensor to take a mid point calibration reading. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking mid point calibration reading in hardware, value={}".format(value))
            return

        # Sensor is not simulated
        self.logger.info( "Taking mid point calibration reading in hardware, value={}".format(value))

        # Send take mid point calibration command to hardware
        command = "Cal,mid,{}".format(value)
        self.process_command(command, processing_seconds=0.9)


    def take_high_point_calibration_reading(self, value):
        """ Commands sensor to take a high point calibration reading. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating taking high point calibration reading in hardware")
            return

        # Sensor is not simulated
        self.logger.info("Taking high point calibration reading in hardware.")

        # Send take high point calibration command to hardware
        command = "Cal,high,{}".format(value)
        self.process_command(command, processing_seconds=0.9)


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
    def potential_hydrogen(self):
        """ Gets pH value. """
        return self._potential_hydrogen

    @potential_hydrogen.setter
    def potential_hydrogen(self, value):
        """ Safely updates ph in environment state each time
            it is changed. """
        self._potential_hydrogen = value
        self.report_peripheral_sensor_value(self.potential_hydrogen_name, value)
        
        # Update environment if not in calibrate mode
        if self.mode != Modes.CALIBRATE:
            self.report_environment_sensor_value(self.name, self.potential_hydrogen_name, value)


    @property
    def temperature_celcius(self):
        """ Gets temperature stored in shared state. """
        if self.temperature_name in self.state.environment["sensor"]["reported"]:
            temperature_celcius = self.state.environment["sensor"]["reported"][self.temperature_name]
            if temperature_celcius != None:
                return float(temperature_celcius)