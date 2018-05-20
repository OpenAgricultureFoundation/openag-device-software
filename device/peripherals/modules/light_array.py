# Import standard python modules
import logging, time, threading, json

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import drivers
from device.drivers.dac5578 import DAC5578

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors
from device.utilities.health import Health


class LightArray(Peripheral):
    """ A light array of panels with DAC5578s controlling light output. """


    def __init__(self, *args, **kwargs):
        """ Instantiates light array. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Get device parameters
        self.panels = self.parameters["communication"]["panels"]

        # Initialize panel drivers
        self.dac5578s = []
        for panel in self.panels:
            dac5578 = DAC5578(
                name = panel["name"],
                bus = panel["bus"],
                address = int(panel["address"], 16), 
                mux = int(panel["mux"], 16), 
                channel = panel["channel"],
            )
            self.dac5578s.append(dac5578)

        # Initialize variable names
        self.intensity_name = self.parameters["variables"]["sensor"]["intensity_watts"]
        self.spectrum_name = self.parameters["variables"]["sensor"]["spectrum_channel_percents"]
        self.illumination_distance_name = self.parameters["variables"]["sensor"]["illumination_distance_cm"]
        self.channel_output_name = self.parameters["variables"]["actuator"]["channel_output_percents"]

        # Initialize channel configs
        self.load_channel_configs()
        self.parse_channel_configs()

        # Initialize health parameter
        self.health = Health(health_minimum=80, health_updates=10)


    def initialize(self):
        """ Initializes light array. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing")

        # Set initial parameters
        self.intensity = None
        self.spectrum = None
        self.distance = None

        # Probe health
        self.probe() 


    def setup(self):
        """ Sets up actuator. Useful for actuators with warm up times >200ms """
        self.logger.debug("Setting up sensor")

        # Setup sensor
        try:    
           # Start with light panel off
            self.turn_off_output()
            self.logger.debug("Successfully setup sensor")
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates actuator. """

        # Initialize channel update flag
        update_channels = False

        # Check for new desired intensity
        if self.desired_intensity != self.intensity and self.desired_intensity != None:
            self.logger.info("Received new desired intensity")
            self.logger.debug("desired_intensity = {} Watts".format(self.desired_intensity))
            update_channels = True

        # Check for new desired spectrum
        if self.desired_spectrum != self.spectrum:
            self.logger.info("Received new desired spectrum")
            self.logger.debug("desired_spectrum_dict = {}".format(self.desired_spectrum))
            update_channels = True

        # Check for new illumination distance
        if self.desired_distance != self.distance:
            self.logger.info("Received new desired illumination distance")
            self.logger.debug("desired_illumination_distance = {} cm".format(self.desired_distance))
            update_channels = True

        # Update output channels if new value
        if update_channels:
            self.update_channel_outputs()


    def reset(self):
        """ Resets sensor. """
        self.logger.info("Resetting sensor")

        # Reset peripheral health & clear error
        self.health.reset()
        self.error = None

        # Reset driver health
        for dac5578 in self.dac5578s:
            dac5578.health.reset()

        # Clear reported values
        self.clear_reported_values()

        # Reset complete!
        self.logger.debug("Successfully reset sensor")


    def shutdown(self):
        """ Shuts down actuator. """

        # Reset driver health
        for dac5578 in self.dac5578s:
            dac5578.health.reset()

        # Clear reported values
        self.clear_reported_values()

        # Send enable sleep command to actuator hardware
        try:
            self.turn_off_output()
            self.logger.debug("Successfully shutdown actuator")
        except:
            self.logger.exception("Actuator shutdown failed")
            self.mode = Modes.ERROR


############################# Main Helper Functions ###########################


    def load_channel_configs(self): 
        """ Loads channel configs from setup file. """
        self.logger.debug("Loading channel configs")
        self.channel_configs = self.setup_dict["channel_configs"]


    def parse_channel_configs(self):
        """ Parses channel configs. """
        self.logger.debug("Parsing channel configs")

        self.channel_config_dict = {}
        for channel_config in self.channel_configs:
            channel_key = channel_config["name"]["brief"]
            self.channel_config_dict[channel_key] = channel_config


    def probe(self):
        """ Probes health. """
        self.logger.info("Probing health")

        # Check driver health
        for dac5578 in self.dac5578s:
            error = dac5578.probe()


    def update_channel_outputs(self):
        """ Updates channel outputs. """

        # Check desired light parameters are not None. If any desired parameter 
        # is None, turn off all outputs and clear reported values
        if self.desired_intensity == None:
            self.logger.warning("Unable to update channel outputs, no desired intensity")
            self.turn_off_output()
            self.clear_reported_values()
            return
        if self.desired_spectrum == None:
            self.logger.warning("Unable to update channel outputs, no desired spectrum")
            self.turn_off_output()
            self.clear_reported_values()
            return
        if self.desired_distance == None:
            self.logger.warning("Unable to update channel outputs, no desired illumination distance")
            self.turn_off_output()
            self.clear_reported_values()
            return

        # Calculate max intensity for given spectrum
        spectrum_max_intensity = self.get_spectrum_max_intensity()

        # Check desired intensity is realiazable for desired spectrum
        if spectrum_max_intensity < self.desired_intensity:
            self.logger.warning("Desired intensity is not realizable for given spectrum, setting max intensity spectrum can realize")
            self.logger.debug("desired_intensity={}Watts, spectrum_max_intensity={}Watts".format(self.desired_intensity, spectrum_max_intensity))
            self.intensity = spectrum_max_intensity
        else:
            self.intensity = self.desired_intensity
        
        # Set spectrum and illumination to desired values       
        self.spectrum = self.desired_spectrum
        self.distance = self.desired_distance

        # Calculate channel output percents
        self.logger.info("Calculating channel output percents")
        channel_outputs = {}
        for channel_config in self.channel_configs:
            channel_name = channel_config["name"]["brief"]
            channel_outputs[channel_name] = self.get_channel_output_percent(channel_name)
        self.logger.debug("channel_outputs = {}".format(channel_outputs))

        # Set channel output on actuator hardwarechannel_output
        self.set_channel_outputs(channel_outputs)


    def get_channel_output_percent(self, channel_name):
        """ Gets channel output percent. """
    
        channel_spectrum_percent = self.desired_spectrum[channel_name]
        desired_channel_intensity = self.desired_intensity * channel_spectrum_percent / 100
        channel_intensity_at_illumination_distance = self.get_channel_intensity_at_distance(channel_name, self.distance)
        channel_output_coefficient = desired_channel_intensity / channel_intensity_at_illumination_distance
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
        output_percent = self.interpolate(output_coefficient_list, output_percent_list, channel_output_coefficient)

        # Set significant figures
        output_percent = round(output_percent, 2)

        # Return interpolated output percent
        return output_percent


    def get_channel_intensity_at_distance(self, channel_name, distance):
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
        if distance < min(distance_list):
            self.logger.warning("Desired illumination distance less than min calibrated distance, interpolating anyway")
            self.logger.debug("Desired illumination distance: {}cm, min calibrated distance: {}cm".format(distance, min(distance_list)))
        if distance > max(distance_list):
            self.logger.warning("Desired illumination distance greater than max calibrated distance, interpolating anyway")
            self.logger.debug("Desired illumination distance: {}cm, max calibrated distance: {}cm".format(distance, max(distance_list)))

        # Calculate intensity from linear interpolation of planar distance map then return value
        channel_intensity = self.interpolate(distance_list, intensity_list, distance)
        return channel_intensity


    def get_spectrum_max_intensity(self):
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
            channel_intensity_at_illumination_distance = self.get_channel_intensity_at_distance(channel_name, self.desired_distance)
            channel_spectrum_percent = self.desired_spectrum[channel_name]
            channel_max_intensity = channel_intensity_at_illumination_distance / (channel_spectrum_percent / 100)
            max_channel_intensities_watts.append(channel_max_intensity)

        # Return lowest actuatable intensity
        return min(max_channel_intensities_watts)


    def build_channel_outputs(self, output_percent, enable_channel_name=None):
        """ Builds channel output percent dict and sets each channel output to 
            passed in output percent. """
        channel_outputs = {}
        for channel_config in self.channel_configs:
            channel_name = channel_config["name"]["brief"]

            # If enable channel name parameter is passed in, only set channel 
            # that channel to output percent and set the other channals off,
            # otherwise set all channels to output percent
            if enable_channel_name == None:
                channel_outputs[channel_name] = output_percent
            elif channel_name == enable_channel_name:
                channel_outputs[channel_name] = output_percent
            else:
                channel_outputs[channel_name] = 0

        return channel_outputs


    def calculate_output_intensity_and_spectrum(self, output_percent_dict, distance):
        """ Calculates resultant spectrum from output percent dict at distance. """

        channel_intensities = {}
        output_intensity = 0

        # Calculate intensity at distance from output percent from each channel
        for channel_config in self.channel_configs:
            channel_name = channel_config["name"]["brief"]
            raw_intensity = self.get_channel_intensity_at_distance(channel_name, distance)
            scaled_intensity = raw_intensity * output_percent_dict[channel_name] / 100
            channel_intensities[channel_name] = scaled_intensity
            output_intensity += scaled_intensity

        # Check if light completely off
        if output_intensity == 0:
            return 0, None

        # Calculate spectrum
        output_spectrum = {}
        for channel_name, intensity in channel_intensities.items():
            channel_percentage = intensity / output_intensity * 100
            output_spectrum[channel_name] = round(channel_percentage, 1)

        # Return output intensity and spectrum spectrum
        self.logger.debug("output_intensity={}, output_spectrum={}".format(output_intensity, output_spectrum))
        return output_intensity, output_spectrum


    def clear_reported_values(self):
        """ Clears values reported to shared state. """
        self.intensity = None
        self.spectrum = None
        self.distance = None







################# Peripheral Specific Event Functions #########################


    def process_peripheral_specific_event(self, request):
        """ Processes peripheral specific event event. Gets request parameters, 
            executes request, returns response. """

        # Execute request
        if request["type"] == "Turn On":
            self.response = self.process_turn_on_event()
        elif request["type"] == "Turn Off":
            self.response = self.process_turn_off_event()
        elif request["type"] == "Fade Concurrently":
            self.process_fade_concurrently_event()
        elif request["type"] == "Fade Sequentially":
            self.process_fade_sequentially_event()
        elif request["type"] == "Turn On Channel":
            self.response = self.process_turn_on_channel_event(request)
        elif request["type"] == "Turn Off Channel":
            self.response = self.process_turn_off_channel_event(request)
        elif request["type"] == "Fade Channel":
            self.process_fade_channel_event(request)
        elif request["type"] == "Set Channel Output":
            self.response = self.process_set_channel_output_event(request)
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


    def process_turn_on_event(self):
        """ Processes turn on event. """
        self.logger.debug("Processing turn on event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Execute request
        try:
            self.turn_on_output()
            response = {"status": 200, "message": "Turned light on!"}
            return response
        except Exception as e:
            self.error = "Unable to turn light on"
            self.logger.exception(self.error)
            response = {"status": 500, "message": self.error}
            self.mode = Modes.ERROR
            return response


    def process_turn_off_event(self):
        """ Processes turn off event. """
        self.logger.debug("Processing turn off event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Execute request
        try:
            self.turn_off_output()
            response = {"status": 200, "message": "Turned light off!"}
            return response
        except Exception as e:
            self.error = "Unable to turn light off"
            self.logger.exception(self.error)
            response = {"status": 500, "message": self.error}
            self.mode = Modes.ERROR
            return response


    def process_fade_concurrently_event(self):
        """ Processes fade concurrently event. """
        self.logger.debug("Processing fade concurrently event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.response = {"status": 400, "message": "Must be in manual mode."}
            return

        # Return response to event request
        self.response = {"status": 200, "message": "Fading concurrently!"}

        # Start fade concurrently loop, exits on new event
        try:
            self.fade_concurrently()
        except:
            self.error = "Fade concurrently failed"
            self.logger.exception(self.error)
            self.mode = Modes.ERROR


    def process_fade_sequentially_event(self):
        """ Processes fade sequentially event. """
        self.logger.debug("Processing fade sequentially event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.response = {"status": 400, "message": "Must be in manual mode."}
            return

        # Return response to event request
        self.response = {"status": 200, "message": "Fading sequentially!"}

        # Start fade concurrently loop, exits on new event
        try:
            self.fade_sequentially()
        except:
            self.error = "Fade sequentially failed"
            self.logger.exception(self.error)
            self.mode = Modes.ERROR
            return


    def process_turn_on_channel_event(self, request):
        """ Processes turn off event. """
        self.logger.debug("Processing turn on channel event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Verify value in request
        try:
            channel_name = request["value"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response

        # Check channel name in channel outputs
        if channel_name not in self.channel_outputs.keys():
            response = {"status": 400, "message": "Invalid channel name."}
            return response

        # Execute request
        try:
            self.turn_on_channel_output(channel_name)
            response = {"status": 200, "message": "Turned light channel `{}` on!".format(channel_name)}
            return response
        except Exception as e:
            self.error = "Unable to turn light channel `{}` on".format(channel_name)
            self.logger.exception(self.error)
            self.mode = Modes.ERROR
            response = {"status": 500, "message": self.error}
            return response


    def process_turn_off_channel_event(self, request):
        """ Processes turn off channel event. """
        self.logger.debug("Processing turn off channel event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Verify value in request
        try:
            channel_name = request["value"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response

        # Check channel name in channel outputs
        if channel_name not in self.channel_outputs.keys():
            response = {"status": 400, "message": "Invalid channel name."}
            return response

        # Execute request
        try:
            self.turn_off_channel_output(channel_name)
            response = {"status": 200, "message": "Turned light channel `{}` off!".format(channel_name)}
            return response
        except Exception as e:
            self.error = "Unable to turn light channel `{}` off".format(channel_name)
            self.logger.exception(self.error)
            self.mode = Modes.ERROR
            response = {"status": 500, "message": self.error}
            return response


    def process_fade_channel_event(self, request):
        """ Processes fadef channel event. """
        self.logger.debug("Processing fade channel event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.response = {"status": 400, "message": "Must be in manual mode."}
            return

        # Verify value in request
        try:
            channel_name = request["value"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            self.response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return

        # Check channel name in channel outputs
        if channel_name not in self.channel_outputs.keys():
            self.response = {"status": 400, "message": "Invalid channel name."}
            return

        # Return response to event request
        self.response = {"status": 200, "message": "Fading channel!"}

        # Execute request
        try:
            self.fade_channel_output(channel_name)
            self.response = {"status": 200, "message": "Fading channel `{}`!".format(channel_name)}
            return
        except Exception as e:
            self.error = "Unable to fade channel `{}`".format(channel_name)
            self.logger.exception(self.error)
            self.mode = Modes.ERROR
            self.response = {"status": 500, "message": self.error}
            return


    def process_set_channel_output_event(self, request):
        """ Processes turn off event. """
        self.logger.debug("Processing set channel output event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Verify value in request
        try:
            channel_name, output_percent = request["value"].split(",")
            self.logger.debug("channel_name = {}".format(channel_name))
            output_percent = float(output_percent)
            self.logger.debug("output_percent = {}".format(output_percent))
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response

        # Check channel name in channel outputs
        if channel_name not in self.channel_outputs.keys():
            response = {"status": 400, "message": "Invalid channel name."}
            return response

        # Check valid channel output percent
        if output_percent < 0 or output_percent > 100:
            response = {"status": 400, "message": "Invalid channel name."}
            return response

        # Execute request
        try:
            self.set_channel_output(channel_name, output_percent)
            response = {"status": 200, "message": "Set light channel `{}` to {}%!".format(channel_name, output_percent)}
            return response
        except Exception as e:
            self.error = "Unable to turn light channel `{}` to {}%".format(channel_name, output_percent)
            self.logger.exception(self.error)
            self.mode = Modes.ERROR
            response = {"status": 500, "message": self.error}
            return response


############################# Hardware Interactions ###########################



    def set_outputs(self, sw_outputs):
        """ Sets channel outputs. """

        # Convert software channels to hardware channels
        # e.g. {"WW": 80, "FR": 40} -> {3: 80, 6: 40}
        hw_outputs = self.get_hw_outputs(sw_outputs)

        # Set outpus on panel drivers
        for dac5578 in self.dac5578s:
            error = dac5578.set_outputs(hw_outputs)
        


################# Hardware Interaction Helper Functions #######################


    def turn_on_output(self):
        """ Turns on output. Sets all channel output percents to 100%. """

        # Build channel output percent dict
        channel_outputs = self.build_channel_outputs(output_percent=100)

        # Use previously used distance or first distance in entry if prev is none
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]   

        # Calculate resultant intensity and spectrum
        self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

        # Set channel outputs on hardware
        self.set_channel_outputs(channel_outputs)


    def turn_off_output(self):
        """ Turns off output. Sets all channel output percents to 0%. """
        self.logger.debug("Turning off channel outputs")
        
        # Build channel output percent dict
        channel_outputs = self.build_channel_outputs(output_percent=0)

        # Update reported intensity, spectrum and distance
        self.intensity = 0
        self.spectrum = None
        self.distance = None

        # Set channel outputs on hardware
        self.set_channel_outputs(channel_outputs)


    def fade_concurrently(self):
        """ Fades output concurrently forever. Exits on new event. """
        self.logger.debug("Fading concurrently")

        # Use previously used illumination distance or first distance in entry if prev is none
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  


        # Run fade loop until new event
        while True:

            # Fade up
            for output_percent in range(0, 100, 10):
                self.intensity = output_percent
                channel_outputs = self.build_channel_outputs(output_percent)
                self.set_channel_outputs(channel_outputs)
                self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

                # Check for events
                if self.request != None:
                    request = self.request
                    self.request = None
                    self.process_event(request)
                    return

                # Update every 100ms
                time.sleep(0.1)

            # Fade down
            for output_percent in range(100, 0, -10):
                self.intensity = output_percent
                channel_outputs = self.build_channel_outputs(output_percent)
                self.set_channel_outputs(channel_outputs)
                self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)


                # Check for events
                if self.request != None:
                    request = self.request
                    self.request = None
                    self.process_event(request)
                    return

                # Update every 100ms
                time.sleep(0.1)


    def fade_sequentially(self):
        """ Fades output sequentially, forever. Exits on new event. """
        self.logger.debug("Fading sequentially")

        # Use previously used illumination distance or first distance in entry if prev is none
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  

        # Run fade loop until new event
        while True:

            for channel_config in self.channel_configs:
                channel_name = channel_config["name"]["brief"]
                # Fade up
                for output_percent in range(0, 100, 10):
                    self.intensity = output_percent
                    channel_outputs = self.build_channel_outputs(output_percent, enable_channel_name=channel_name)
                    self.set_channel_outputs(channel_outputs)
                    self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

                    # Check for events
                    if self.request != None:
                        request = self.request
                        self.request = None
                        self.process_event(request)
                        return

                    # Update every 100ms
                    time.sleep(0.1)

                # Fade down
                for output_percent in range(100, 0, -10):
                    self.intensity = output_percent
                    channel_outputs = self.build_channel_outputs(output_percent, enable_channel_name=channel_name)
                    self.set_channel_outputs(channel_outputs)
                    self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)


                    # Check for events
                    if self.request != None:
                        request = self.request
                        self.request = None
                        self.process_event(request)
                        return

                    # Update every 100ms
                    time.sleep(0.1)


    def turn_on_channel_output(self, channel_name):
        """ Turns on channel output. Sets specific channel output percent to
            100% and the rest of the channel to 0% """

        # Set channel output to 0%
        self.channel_outputs[channel_name] = 100

        # Build channel output percent dict
        # channel_outputs = self.build_channel_outputs(output_percent=100, enable_channel_name=channel_name)

        # Use previously used distance or first distance in entry if prev is none
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]   

        # Calculate resultant intensity and spectrum
        self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

        # Set channel outputs on hardware
        self.set_channel_outputs(self.channel_outputs)


    def turn_off_channel_output(self, channel_name):
        """ Turns off channel output. Sets specific channel output percent to
            100% and the rest of the channel to 0% """

        # Set channel output to 0%
        self.channel_outputs[channel_name] = 0

        # Use previously used distance or first distance in entry if prev is none
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]   

        # Calculate resultant intensity and spectrum
        self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

        # Set channel outputs on hardware
        self.set_channel_outputs(self.channel_outputs)


    def fade_channel_output(self, channel_name):
        """ Fades output channel forever. Exits on new event. """
        self.logger.debug("Fading channel")

        # Turn off all channels
        self.turn_off_output()

        # Use previously used illumination distance or first distance in entry if prev is none
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  

        # Run fade loop until new event
        while True:

            # Fade up
            for output_percent in range(0, 100, 10):
                self.intensity = output_percent
                self.channel_outputs[channel_name] = output_percent # TODO: copy the dict and pass in, dont need to set twice (here + in set function)
                self.set_channel_outputs(self.channel_outputs)
                self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

                # Check for events
                if self.request != None:
                    request = self.request
                    self.request = None
                    self.process_event(request)
                    return

                # Update every 100ms
                time.sleep(0.1)

            # Fade down
            for output_percent in range(100, 0, -10):
                self.intensity = output_percent
                self.channel_outputs[channel_name] = output_percent # TODO: copy the dict and pass in, dont need to set twice (here + in set function)
                self.set_channel_outputs(self.channel_outputs)
                self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

                # Check for events
                if self.request != None:
                    request = self.request
                    self.request = None
                    self.process_event(request)
                    return

                # Update every 100ms
                time.sleep(0.1)


########################## Setter & Getter Functions ##########################


    @property
    def spectrum(self):
        """ Gets spectrum value. """
        try:
            return self._spectrum
        except NameError:
            self._spectrum = None
            return self._spectrum


    @spectrum.setter
    def spectrum(self, value):
        """ Safely updates spectrum in environment object each time
            it is changed. """
        self._spectrum = value
        self.report_sensor_value(self.name, self.spectrum_name, value, simple=True)
        self.report_peripheral_sensor_value(self.spectrum_name, value)


    @property
    def desired_spectrum(self):
        """ Gets desired spectrum value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """

        if self.mode != Modes.MANUAL:
            if "sensor" not in self.state.environment:
                return
            if "desired" not in self.state.environment["sensor"]:
                return
            if self.spectrum_name in self.state.environment["sensor"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.spectrum_name]
                return value
        else:
            if "stored" not in self.state.peripherals:
                return
            if "desired" not in self.state.peripherals["stored"]:
                return
            if self.spectrum_name in self.state.peripherals[self.name]["stored"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.spectrum_name]
                return value


    @desired_spectrum.setter
    def desired_spectrum(self, value):
        """ Safely updates desired spectrum in shared peripheral state. Only 
            updates from manual mode. """

        # Verify only setting from manual mode
        if self.mode != Modes.MANUAL:
            self.logger.error("desired_intensity setter should only be set from manual mode")
            return

        # Safely write desired intensity to shared peripheral state
        with threading.Lock():
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            if "desired" not in self.state.peripherals[self.name]["stored"]:
                self.state.peripherals[self.name]["stored"]["desired"] = {}
            self.state.peripherals[self.name]["stored"]["desired"][self.spectrum_name] = value


    @property
    def intensity(self):
        """ Gets intensity value. """
        try:
            return self._intensity
        except NameError:
            self._intensity = None
            return self._intensity


    @intensity.setter
    def intensity(self, value):
        """ Safely updates intensity in environment object each time 
            it is changed. """
        self._intensity = value
        self.report_sensor_value(self.name, self.intensity_name, value, simple=True)
        self.report_peripheral_sensor_value(self.intensity_name, value)

    @property
    def desired_intensity(self):
        """ Gets desired intensity value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """

        if self.mode != Modes.MANUAL:
            if "sensor" not in self.state.environment:
                return
            if "desired" not in self.state.environment["sensor"]:
                return
            if self.intensity_name in self.state.environment["sensor"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.intensity_name]
                return value
        else:
            if "stored" not in self.state.peripherals:
                return
            if "desired" not in self.state.peripherals["stored"]:
                return
            if self.intensity_name in self.state.peripherals[self.name]["stored"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.intensity_name]
                return value


    @desired_intensity.setter
    def desired_intensity(self, value):
        """ Safely updates desired intensity in shared peripheral state. Only 
            updates from manual mode. """

        # Verify only setting from manual mode
        if self.mode != Modes.MANUAL:
            self.logger.error("desired_intensity setter should only be set from manual mode")
            return

        # Safely write desired intensity to shared peripheral state
        with threading.Lock():
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            if "desired" not in self.state.peripherals[self.name]["stored"]:
                self.state.peripherals[self.name]["stored"]["desired"] = {}
            self.state.peripherals[self.name]["stored"]["desired"][self.intensity_name] = value


    @property
    def distance(self):
        """ Gets intensity value. """
        try:
            return self._distance
        except NameError:
            self._distance = None
            return self._distance


    @distance.setter
    def distance(self, value):
        """ Safely updates illumination distance in environment object each time 
            it is changed. """
        self._distance = value
        self.report_sensor_value(self.name, self.illumination_distance_name, value, simple=True)
        self.report_peripheral_sensor_value(self.illumination_distance_name, value)


    @property
    def desired_distance(self):
        """ Gets desired illumination distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """

        if self.mode != Modes.MANUAL:
            if "sensor" not in self.state.environment:
                return
            if "desired" not in self.state.environment["sensor"]:
                return
            if self.illumination_distance_name in self.state.environment["sensor"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.illumination_distance_name]
                return value
        else:
            if "stored" not in self.state.peripherals:
                return
            if "desired" not in self.state.peripherals["stored"]:
                return
            if self.illumination_distance_name in self.state.peripherals[self.name]["stored"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.illumination_distance_name]
                return value


    @desired_distance.setter
    def desired_distance(self, value):
        """ Safely updates desired intensity in shared peripheral state. Only 
            updates from manual mode. """

        # Verify only setting from manual mode
        if self.mode != Modes.MANUAL:
            self.logger.error("desired_intensity setter should only be set from manual mode")
            return

        # Safely write desired intensity to shared peripheral state
        with threading.Lock():
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            if "desired" not in self.state.peripherals[self.name]["stored"]:
                self.state.peripherals[self.name]["stored"]["desired"] = {}
            self.state.peripherals[self.name]["stored"]["desired"][self.illumination_distance_name] = value


    @property
    def channel_outputs(self):
        """ Gets channel outputs percent value. """
        try:
            return self._channel_outputs
        except NameError:
            self._channel_outputs = None
            return self._channel_outputs


    @channel_outputs.setter
    def channel_outputs(self, value):
        """ Safely updates channel outputs percent in environment object each time 
            it is changed. """
        self._channel_outputs = value
        self.report_actuator_value(self.name, self.channel_output_name, value)
        self.set_desired_actuator_value(self.name, self.channel_output_name, value)

        self.report_peripheral_actuator_value(self.channel_output_name, value)
