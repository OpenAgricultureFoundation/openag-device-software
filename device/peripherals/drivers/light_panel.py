# Import standard python modules
import logging, time, threading, json

# Import scipy
import scipy.interpolate

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device comms
from device.comms.i2c import I2C

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class LightPanel(Peripheral):
    """ A multichannel light panel. """

    # Initialize sensor variables
    _intensity_watts = None
    _desired_intensity_watts = None
    _spectrum_normalized_percentage_dict = None
    _desired_spectrum_normalized_percentage_dict = None
    _illumination_distance_cm = None
    _desired_illumination_distance_cm = None
    _channel_output_percent_dict = None


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize i2c mux parameters
        self.parameters = self.config["parameters"]
        self.bus = int(self.parameters["communication"]["bus"])
        self.mux = int(self.parameters["communication"]["mux"], 16) # Convert from hex string
        self.channel = int(self.parameters["communication"]["channel"])
        self.address = int(self.parameters["communication"]["address"], 16) # Convert from hex string
        
        # Initialize I2C communication if sensor not simulated
        if not self.simulate:
            self.logger.info("Initializing i2c bus={}, mux=0x{:02X}, channel={}, address=0x{:02X}".format(
                self.bus, self.mux, self.channel, self.address))
            self.i2c = I2C(bus=self.bus, mux=self.mux, channel=self.channel, address=self.address)

        # Initialize variable names
        self.intensity_name = self.parameters["variables"]["sensor"]["intensity_watts"]
        self.spectrum_name = self.parameters["variables"]["sensor"]["spectrum_normalized_percentage_dict"]
        self.illumination_distance_name = self.parameters["variables"]["sensor"]["illumination_distance_cm"]
        self.channel_output_name = self.parameters["variables"]["actuator"]["channel_output_percent_dict"]

        # Initialize setup file
        self.load_setup_file()

        # Initialize channel configs
        self.load_channel_configs()
        self.parse_channel_configs()


    @property
    def spectrum_normalized_percentage_dict(self):
        """ Gets spectrum value. """
        return self._spectrum_normalized_percentage_dict


    @spectrum_normalized_percentage_dict.setter
    def spectrum_normalized_percentage_dict(self, value):
        """ Safely updates spectrum in environment object each time
            it is changed. """
        self._spectrum_normalized_percentage_dict = value
        with threading.Lock():
                self.report_sensor_value(self.name, self.spectrum_name, value, simple=True)


    @property
    def intensity_watts(self):
        """ Gets intensity value. """
        return self._intensity_watts


    @intensity_watts.setter
    def intensity_watts(self, value):
        """ Safely updates intensity in environment object each time 
            it is changed. """
        self._intensity_watts = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.intensity_name, value, simple=True)


    @property
    def illumination_distance_cm(self):
        """ Gets intensity value. """
        return self._illumination_distance_cm


    @illumination_distance_cm.setter
    def illumination_distance_cm(self, value):
        """ Safely updates illumination distance in environment object each time 
            it is changed. """
        self._illumination_distance_cm = value
        with threading.Lock():
            self.report_sensor_value(self.name, self.illumination_distance_name, value, simple=True)


    @property
    def channel_output_percent_dict(self):
        """ Gets channel outputs percent value. """
        return self._channel_output_percent_dict


    @channel_output_percent_dict.setter
    def channel_output_percent_dict(self, value):
        """ Safely updates channel outputs percent in environment object each time 
            it is changed. """
        self._channel_output_percent_dict = value
        with threading.Lock():
            self.report_actuator_value(self.name, self.channel_output_name, value)

            if self.mode != Modes.MANUAL:
                self.set_desired_actuator_value(self.name, self.channel_output_name, value)


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Set initial parameters
        self.intensity_watts = None
        self.spectrum_normalized_percentage_dict = None
        self.channel_output_percent_dict = None
        self.illumination_distance_cm = None
        self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()


    def perform_initial_health_check(self):
        """ Performs initial health check by TODO: this. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.info("Simulating initial health check")
            return
        else:
            self.logger.info("Performing initial health check")

        # Check sensor health
        try:
            # TODO: Do something
            self.logger.debug("Passed initial health check")
        except:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR


    def setup(self):
        """ Sets up actuator. Useful for actuators with warm up times >200ms """
        
        # Check for simulated sensor
        if self.simulate:
            self.logger.info("Simulating sensor setup")
            return
        else:
            self.logger.debug("Setting up sensor")

        # Setup sensor
        try:    
            # TODO: Do something
            self.logger.debug("Successfully setup sensor")
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates actuator. """

        # Initialize channel update flag
        update_channels = False

        # Check for new desired intensity
        if self.intensity_name in self.state.environment["sensor"]["desired"]:
            self._desired_intensity_watts = self.state.environment["sensor"]["desired"][self.intensity_name]
            if self._desired_intensity_watts != self.intensity_watts:
                self.logger.info("Received new desired intensity")
                self.logger.debug("desired_intensity = {} Watts".format(self._desired_intensity_watts))
                update_channels = True

        # Check for new desired spectrum
        if self.spectrum_name in self.state.environment["sensor"]["desired"]:
            self._desired_spectrum_normalized_percentage_dict = self.state.environment["sensor"]["desired"][self.spectrum_name]
            if self._desired_spectrum_normalized_percentage_dict != self.spectrum_normalized_percentage_dict:
                self.logger.info("Received new desired spectrum")
                self.logger.debug("desired_spectrum_dict = {}".format(self._desired_spectrum_normalized_percentage_dict))
                update_channels = True

        # Check for new illumination distance
        if self.illumination_distance_name in self.state.environment["sensor"]["desired"]:
            self._desired_illumination_distance_cm = self.state.environment["sensor"]["desired"][self.illumination_distance_name]
            if self._desired_illumination_distance_cm != self.illumination_distance_cm:
                self.logger.info("Received new desired illumination distance")
                self.logger.debug("desired_illumination_distance = {} cm".format(self._desired_illumination_distance_cm))
                update_channels = True

        # Update output channels if new value
        if update_channels:
            self.update_channel_outputs()


    def load_setup_file(self): 
        """ Loads setup file from filename. """
        self.logger.debug("Loading setup file")

        # TODO: load this from database
        file_name = self.parameters["setup"]["file_name"]
        self.setup_file = json.load(open("device/peripherals/setups/" + file_name + ".json"))


    def load_channel_configs(self): 
        """ Loads channel configs from setup file. """
        self.logger.debug("Loading channel configs")
        self.channel_configs = self.setup_file["channel_configs"]


    def parse_channel_configs(self):
        """ Parses channel configs. """
        self.logger.debug("Parsing channel configs")

        self.channel_config_dict = {}
        for channel_config in self.channel_configs:
            channel_key = channel_config["name"]["brief"]
            self.channel_config_dict[channel_key] = channel_config


    def update_channel_outputs(self):
        """ Updates channel outputs. """

        # Check desired light parameters are not None. If any desired parameter 
        # is None, turn off all outputs and clear reported values
        if self._desired_intensity_watts == None:
            self.logger.warning("Unable to update channel outputs, no desired intensity")
            self.turn_off_output()
            self.clear_reported_values()
            return
        if self._desired_spectrum_normalized_percentage_dict == None:
            self.logger.warning("Unable to update channel outputs, no desired spectrum")
            self.turn_off_output()
            self.clear_reported_values()
            return
        if self._desired_illumination_distance_cm == None:
            self.logger.warning("Unable to update channel outputs, no desired illumination distance")
            self.turn_off_output()
            self.clear_reported_values()
            return

        # Calculate max intensity for given spectrum
        spectrum_max_intensity_watts = self.get_spectrum_max_intensity_watts()

        # Check desired intensity is realiazable for desired spectrum
        if spectrum_max_intensity_watts < self._desired_intensity_watts:
            self.logger.warning("Desired intensity is not realizable for given spectrum, setting max intensity spectrum can realize")
            self.logger.debug("desired_intensity={}Watts, spectrum_max_intensity={}Watts".format(self._desired_intensity_watts, spectrum_max_intensity_watts))
            self.intensity_watts = spectrum_max_intensity_watts
        else:
            self.intensity_watts = self._desired_intensity_watts
        
        # Set spectrum and illumination to desired values       
        self.spectrum_normalized_percentage_dict = self._desired_spectrum_normalized_percentage_dict
        self.illumination_distance_cm = self._desired_illumination_distance_cm

        # Calculate channel output percents
        self.logger.info("Calculating channel output percents")
        channel_output_percent_dict = {}
        for channel_config in self.channel_configs:
            channel_name = channel_config["name"]["brief"]
            channel_output_percent_dict[channel_name] = self.get_channel_output_percent(channel_name)
        self.logger.debug("channel_output_percent_dict = {}".format(channel_output_percent_dict))

        # Set channel output on actuator hardwarechannel_output
        self.set_channel_outputs(channel_output_percent_dict)


    def get_channel_output_percent(self, channel_name):
        """ Gets channel output percent. """
    
        channel_spectrum_percent = self._desired_spectrum_normalized_percentage_dict[channel_name]
        desired_channel_intensity_watts = self._desired_intensity_watts * channel_spectrum_percent / 100
        channel_intensity_watts_at_illumination_distance = self.get_channel_intensity_watts_at_illumination_distance(channel_name)
        channel_output_coefficient = desired_channel_intensity_watts / channel_intensity_watts_at_illumination_distance
        channel_output_percent = self.get_channel_output_percent_from_output_coefficient(channel_name, channel_output_coefficient)

        return channel_output_percent


    def get_channel_output_percent_from_output_coefficient(self, channel_name, channel_output_coefficient):
        """ Gets channel output percent from provided channel output
            coefficient for provided channel name. Calculates output percent
            from linear interpolation of output percent map. Rounds output 
            percent to 2 decimal points. Assumes config dict keys are already
            verifided. """

        # Get output percent map, assume config dict already verified
        output_percent_map = self.channel_config_dict[channel_name]["output_percent_map"]
       
        # Get output percent map parameters, assume map alread verified
        output_percent_list = []
        output_coefficient_list = []
        for entry in output_percent_map:
            output_percent_list.append(entry["output_percent"])
            output_coefficient_list.append(entry["intensity_normalized"])

        # Calculate output percent from linear interpolation of output percent map
        interpolate_output_percent = scipy.interpolate.interp1d(output_coefficient_list, output_percent_list)
        output_percent = float(interpolate_output_percent(channel_output_coefficient))

        # Set significant figures
        output_percent = round(output_percent, 2)

        # Return interpolated output percent
        return output_percent


    def get_channel_intensity_watts_at_illumination_distance(self, channel_name):
        """ Gets channel intensity at desired illumination distance for 
            given channel name. Checks for valid illumination distance then 
            calculates intensity from linear interpolation of planar distance
            map. Warns if desired illumination distance is out of range but 
            still interpolates. Assumes config dict keys are already verifided. """

        # Get planar distance map, assume channel config dict already verified
        planar_distance_map = self.channel_config_dict[channel_name]["planar_distance_map"]

        # Get valid illumination distance range, assume planar distance map already verified
        distance_list = []
        intensity_list = []
        for entry in planar_distance_map:
            distance_list.append(entry["z_cm"])
            intensity_list.append(entry["intensity_watts"])

        # Check illumination distance within valid range, warn if not.
        # TODO: Should this prevent light from turning on?
        if self._desired_illumination_distance_cm < min(distance_list):
            self.logger.warning("Desired illumination distance less than min calibrated distance, interpolating anyway")
            self.logger.debug("Desired illumination distance: {}cm, min calibrated distance: {}cm".format(self._desired_illumination_distance_cm, min(distance_list)))
        if self._desired_illumination_distance_cm > max(distance_list):
            self.logger.warning("Desired illumination distance greater than max calibrated distance, interpolating anyway")
            self.logger.debug("Desired illumination distance: {}cm, max calibrated distance: {}cm".format(self._desired_illumination_distance_cm, max(distance_list)))

        # Calculate intensity from linear interpolation of planar distance map then return value
        interpolate_intensity = scipy.interpolate.interp1d(distance_list, intensity_list)
        channel_intensity_watts_at_illumination_distance = float(interpolate_intensity(self._desired_illumination_distance_cm))
        return channel_intensity_watts_at_illumination_distance


    def get_spectrum_max_intensity_watts(self):
        """ Gets max intensity for given spectrum based on channel configs and
            desired illumination distance. """

        # Initialize max planar intensities list
        max_channel_intensities_watts = []

        # Get max planar intensity for each channel and append to max planar 
        # intensities list. Calculate max planar intensity for each channel by
        # assuming all channel intensities superimpose to generate the desired
        # overall light intensity. For example, if a Far Red channel on a light 
        # panel is set to comprise 20% of the light output, and can output 50 
        # Watts at a distance of 10cm. The max overall intensity this channel
        # could realize while preserving the integrity of the spectrum is:
        #   50 / 0.2 = 250 Watts.
        for channel_config in self.channel_configs:
            channel_name = channel_config["name"]["brief"]
            channel_intensity_watts_at_illumination_distance = self.get_channel_intensity_watts_at_illumination_distance(channel_name)
            channel_spectrum_percent = self._desired_spectrum_normalized_percentage_dict[channel_name]
            channel_max_intensity = channel_intensity_watts_at_illumination_distance / (channel_spectrum_percent / 100)
            max_channel_intensities_watts.append(channel_max_intensity)

        # Return lowest actuatable intensity
        return min(max_channel_intensities_watts)


    def shutdown(self):
        """ Shuts down sensor. """
        self.turn_off_output()
        self.clear_reported_values()


    def turn_off_output(self):
        """ Turns off output. Sets all channel output percents to 0%. """
        
        # Build channel output percent dict
        channel_output_percent_dict = {}
        for channel_config in self.channel_configs:
            channel_name = channel_config["name"]["brief"]
            channel_output_percent_dict[channel_name] = 0

        # Set channel outputs on hardware
        self.set_channel_outputs(channel_output_percent_dict)


    def clear_reported_values(self):
        """ Clears values reported to shared state. """
        self.intensity_watts = None
        self.spectrum_normalized_percentage_dict = None
        self.illumination_distance_cm = None


############################# Hardware Interactions ###########################

    def set_channel_outputs(self, channel_output_percent_dict):
        """ Sets channel outputs on hardware. Converts each channel output 
            percent to output byte then sends update command to hardware. 
            Assumes channel config dict keys are verified. """
        try:
            for channel_name, output_percent in channel_output_percent_dict.items():
                output_byte = 255 - int(output_percent*2.55) # 255 is off, 0 is on
                software_channel = self.channel_config_dict[channel_name]["channel"]["software"]
                if not self.simulate:
                    self.i2c.write([0x30+software_channel, output_byte, 0x00])
                else:
                    self.logger.info("Simulating writing to dac: software_channel={} output_byte={}".format(software_channel, output_byte))
            self.channel_output_percent_dict = channel_output_percent_dict
        except:
            self.channel_output_percent_dict = None
            self.logger.exception("Unable to set channel outputs")
            self._missed_readings += 1
        self.update_health()


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


    # TODO: add process_sampling_interval event with checks for min update interval
