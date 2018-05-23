# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error

# Import led panel
from device.peripherals.led_dac5578.panel import Panel


class Array:

    def __init__(self, name, panels, simulate=False):
        """ Instantiate array. """

        # Instantiate logger
        self.logger = Logger(
            name = "LEDArray({})".format(name),
            dunder_name = __name__,
        )

        # Instantiate all panels in array
        self.panels = []
        for panel in panels:
            self.panels.append(Panel(
                name = panel["name"], 
                bus = panel["bus"], 
                address = panel["address"], 
                mux = panel["mux"], 
                channel = panel["channel"],
                simulate = simulate,
            ))


    def initialize(self):
        """ Initializes array. Initializes all panels in array. """
        for panel in self.panels:
            panel.initialize()



    def set_spectral_power_distribution


#   def probe(self):
#       ...


#   def set_output(self, channel, percent, panel=None):
#       ...


#   def set_outputs(self, percent, panel=None):
#       ...


#   def turn_on(self, panel=None):
#       self.set_outputs(100, panel=panel)


#   def turn_off(self, panel=None):
#       self.set_outputs(0, panel=panel)


#   def fade(self):
#       ...





#     def probe(self, retry=False):
#         """ Probes health. """
#         self.logger.info("Probing health")

#         # Check driver health
#         for dac5578 in self.dac5578s:
#             error = dac5578.probe()

#             # Check for errors
#             if error.exists(retry):
#                 ...
#             else:
#                 ...


#     def update_channel_outputs(self):
#         """ Updates channel outputs. """

#         # Check desired light parameters are not None. If any desired parameter 
#         # is None, turn off all outputs and clear reported values
#         if self.desired_intensity == None:
#             self.logger.warning("Unable to update channel outputs, no desired intensity")
#             self.turn_off_output()
#             self.clear_reported_values()
#             return
#         if self.desired_spectrum == None:
#             self.logger.warning("Unable to update channel outputs, no desired spectrum")
#             self.turn_off_output()
#             self.clear_reported_values()
#             return
#         if self.desired_distance == None:
#             self.logger.warning("Unable to update channel outputs, no desired illumination distance")
#             self.turn_off_output()
#             self.clear_reported_values()
#             return

#         # Calculate max intensity for given spectrum
#         spectrum_max_intensity = self.get_spectrum_max_intensity()

#         # Check desired intensity is realiazable for desired spectrum
#         if spectrum_max_intensity < self.desired_intensity:
#             self.logger.warning("Desired intensity is not realizable for given spectrum, setting max intensity spectrum can realize")
#             self.logger.debug("desired_intensity={}Watts, spectrum_max_intensity={}Watts".format(self.desired_intensity, spectrum_max_intensity))
#             self.intensity = spectrum_max_intensity
#         else:
#             self.intensity = self.desired_intensity
        
#         # Set spectrum and illumination to desired values       
#         self.spectrum = self.desired_spectrum
#         self.distance = self.desired_distance

#         # Calculate channel output percents
#         self.logger.info("Calculating channel output percents")
#         channel_outputs = {}
#         for channel_config in self.channel_configs:
#             channel_name = channel_config["name"]["brief"]
#             channel_outputs[channel_name] = self.get_channel_output_percent(channel_name)
#         self.logger.debug("channel_outputs = {}".format(channel_outputs))

#         # Set channel output on actuator hardwarechannel_output
#         self.set_channel_outputs(channel_outputs)


#     def get_channel_output_percent(self, channel_name):
#         """ Gets channel output percent. """
    
#         channel_spectrum_percent = self.desired_spectrum[channel_name]
#         desired_channel_intensity = self.desired_intensity * channel_spectrum_percent / 100
#         channel_intensity_at_illumination_distance = self.get_channel_intensity_at_distance(channel_name, self.distance)
#         channel_output_coefficient = desired_channel_intensity / channel_intensity_at_illumination_distance
#         channel_output_percent = self.get_channel_output_percent_from_output_coefficient(channel_name, channel_output_coefficient)

#         return channel_output_percent


#     def get_channel_output_percent_from_output_coefficient(self, channel_name, channel_output_coefficient):
#         """ Gets channel output percent from provided channel output
#             coefficient for provided channel name. Calculates output percent
#             from linear interpolation of output percent map. Rounds output 
#             percent to 2 decimal points. Assumes config dict keys are already
#             verifided. """

#         # Get output percent map, assume config dict already verified
#         output_percent_map = self.channel_config_dict[channel_name]["output_percent_map"]
       
#         # Get output percent map parameters, assume map alread verified
#         output_percent_list = []
#         output_coefficient_list = []
#         for entry in output_percent_map:
#             output_percent_list.append(entry["output_percent"])
#             output_coefficient_list.append(entry["intensity_normalized"])

#         # Calculate output percent from linear interpolation of output percent map
#         output_percent = self.interpolate(output_coefficient_list, output_percent_list, channel_output_coefficient)

#         # Set significant figures
#         output_percent = round(output_percent, 2)

#         # Return interpolated output percent
#         return output_percent


#     def get_channel_intensity_at_distance(self, channel_name, distance):
#         """ Gets channel intensity at desired illumination distance for 
#             given channel name. Checks for valid illumination distance then 
#             calculates intensity from linear interpolation of planar distance
#             map. Warns if desired illumination distance is out of range but 
#             still interpolates. Assumes config dict keys are already verifided. """

#         # Get planar distance map, assume channel config dict already verified
#         planar_distance_map = self.channel_config_dict[channel_name]["planar_distance_map"]

#         # Get valid illumination distance range, assume planar distance map already verified
#         distance_list = []
#         intensity_list = []
#         for entry in planar_distance_map:
#             distance_list.append(entry["z_cm"])
#             intensity_list.append(entry["intensity_watts"])

#         # Check illumination distance within valid range, warn if not.
#         # TODO: Should this prevent light from turning on?
#         if distance < min(distance_list):
#             self.logger.warning("Desired illumination distance less than min calibrated distance, interpolating anyway")
#             self.logger.debug("Desired illumination distance: {}cm, min calibrated distance: {}cm".format(distance, min(distance_list)))
#         if distance > max(distance_list):
#             self.logger.warning("Desired illumination distance greater than max calibrated distance, interpolating anyway")
#             self.logger.debug("Desired illumination distance: {}cm, max calibrated distance: {}cm".format(distance, max(distance_list)))

#         # Calculate intensity from linear interpolation of planar distance map then return value
#         channel_intensity = self.interpolate(distance_list, intensity_list, distance)
#         return channel_intensity


#     def get_spectrum_max_intensity(self):
#         """ Gets max intensity for given spectrum based on channel configs and
#             desired illumination distance. """

#         # Initialize max planar intensities list
#         max_channel_intensities_watts = []

#         # Get max planar intensity for each channel and append to max planar 
#         # intensities list. Calculate max planar intensity for each channel by
#         # assuming all channel intensities superimpose to generate the desired
#         # overall light intensity. For example, if a Far Red channel on a light 
#         # panel is set to comprise 20% of the light output, and can output 50 
#         # Watts at a distance of 10cm. The max overall intensity this channel
#         # could realize while preserving the integrity of the spectrum is:
#         #   50 / 0.2 = 250 Watts.
#         for channel_config in self.channel_configs:
#             channel_name = channel_config["name"]["brief"]
#             channel_intensity_at_illumination_distance = self.get_channel_intensity_at_distance(channel_name, self.desired_distance)
#             channel_spectrum_percent = self.desired_spectrum[channel_name]
#             channel_max_intensity = channel_intensity_at_illumination_distance / (channel_spectrum_percent / 100)
#             max_channel_intensities_watts.append(channel_max_intensity)

#         # Return lowest actuatable intensity
#         return min(max_channel_intensities_watts)


#     def build_channel_outputs(self, output_percent, enable_channel_name=None):
#         """ Builds channel output percent dict and sets each channel output to 
#             passed in output percent. """
#         channel_outputs = {}
#         for channel_config in self.channel_configs:
#             channel_name = channel_config["name"]["brief"]

#             # If enable channel name parameter is passed in, only set channel 
#             # that channel to output percent and set the other channals off,
#             # otherwise set all channels to output percent
#             if enable_channel_name == None:
#                 channel_outputs[channel_name] = output_percent
#             elif channel_name == enable_channel_name:
#                 channel_outputs[channel_name] = output_percent
#             else:
#                 channel_outputs[channel_name] = 0

#         return channel_outputs


#     def calculate_output_intensity_and_spectrum(self, output_percent_dict, distance):
#         """ Calculates resultant spectrum from output percent dict at distance. """

#         channel_intensities = {}
#         output_intensity = 0

#         # Calculate intensity at distance from output percent from each channel
#         for channel_config in self.channel_configs:
#             channel_name = channel_config["name"]["brief"]
#             raw_intensity = self.get_channel_intensity_at_distance(channel_name, distance)
#             scaled_intensity = raw_intensity * output_percent_dict[channel_name] / 100
#             channel_intensities[channel_name] = scaled_intensity
#             output_intensity += scaled_intensity

#         # Check if light completely off
#         if output_intensity == 0:
#             return 0, None

#         # Calculate spectrum
#         output_spectrum = {}
#         for channel_name, intensity in channel_intensities.items():
#             channel_percentage = intensity / output_intensity * 100
#             output_spectrum[channel_name] = round(channel_percentage, 1)

#         # Return output intensity and spectrum spectrum
#         self.logger.debug("output_intensity={}, output_spectrum={}".format(output_intensity, output_spectrum))
#         return output_intensity, output_spectrum




# ########################################  Hardware   #########################


# def set_outputs(self, sw_outputs):
#     """ Sets channel outputs. """

#     # Convert software channels to hardware channels
#     # e.g. {"WW": 80, "FR": 40} -> {3: 80, 6: 40}
#     hw_outputs = self.get_hw_outputs(sw_outputs)

#     # Set outpus on panel drivers
#     for dac5578 in self.dac5578s:
#         error = dac5578.set_outputs(hw_outputs)
    


# def turn_on_output(self):
#     """ Turns on output. Sets all channel output percents to 100%. """

#     # Build channel output percent dict
#     channel_outputs = self.build_channel_outputs(output_percent=100)

#     # Use previously used distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]   

#     # Calculate resultant intensity and spectrum
#     self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

#     # Set channel outputs on hardware
#     self.set_channel_outputs(channel_outputs)


# def turn_off_output(self):
#     """ Turns off output. Sets all channel output percents to 0%. """
#     self.logger.debug("Turning off channel outputs")
    
#     # Build channel output percent dict
#     channel_outputs = self.build_channel_outputs(output_percent=0)

#     # Update reported intensity, spectrum and distance
#     self.intensity = 0
#     self.spectrum = None
#     self.distance = None

#     # Set channel outputs on hardware
#     self.set_channel_outputs(channel_outputs)


# def fade_concurrently(self):
#     """ Fades output concurrently forever. Exits on new event. """
#     self.logger.debug("Fading concurrently")

#     # Use previously used illumination distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  


#     # Run fade loop until new event
#     while True:

#         # Fade up
#         for output_percent in range(0, 100, 10):
#             self.intensity = output_percent
#             channel_outputs = self.build_channel_outputs(output_percent)
#             self.set_channel_outputs(channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)

#         # Fade down
#         for output_percent in range(100, 0, -10):
#             self.intensity = output_percent
#             channel_outputs = self.build_channel_outputs(output_percent)
#             self.set_channel_outputs(channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)


#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)


# def fade_sequentially(self):
#     """ Fades output sequentially, forever. Exits on new event. """
#     self.logger.debug("Fading sequentially")

#     # Use previously used illumination distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  

#     # Run fade loop until new event
#     while True:

#         for channel_config in self.channel_configs:
#             channel_name = channel_config["name"]["brief"]
#             # Fade up
#             for output_percent in range(0, 100, 10):
#                 self.intensity = output_percent
#                 channel_outputs = self.build_channel_outputs(output_percent, enable_channel_name=channel_name)
#                 self.set_channel_outputs(channel_outputs)
#                 self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

#                 # Check for events
#                 if self.request != None:
#                     request = self.request
#                     self.request = None
#                     self.process_event(request)
#                     return

#                 # Update every 100ms
#                 time.sleep(0.1)

#             # Fade down
#             for output_percent in range(100, 0, -10):
#                 self.intensity = output_percent
#                 channel_outputs = self.build_channel_outputs(output_percent, enable_channel_name=channel_name)
#                 self.set_channel_outputs(channel_outputs)
#                 self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)


#                 # Check for events
#                 if self.request != None:
#                     request = self.request
#                     self.request = None
#                     self.process_event(request)
#                     return

#                 # Update every 100ms
#                 time.sleep(0.1)


# def turn_on_channel_output(self, channel_name):
#     """ Turns on channel output. Sets specific channel output percent to
#         100% and the rest of the channel to 0% """

#     # Set channel output to 0%
#     self.channel_outputs[channel_name] = 100

#     # Build channel output percent dict
#     # channel_outputs = self.build_channel_outputs(output_percent=100, enable_channel_name=channel_name)

#     # Use previously used distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]   

#     # Calculate resultant intensity and spectrum
#     self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

#     # Set channel outputs on hardware
#     self.set_channel_outputs(self.channel_outputs)


# def turn_off_channel_output(self, channel_name):
#     """ Turns off channel output. Sets specific channel output percent to
#         100% and the rest of the channel to 0% """

#     # Set channel output to 0%
#     self.channel_outputs[channel_name] = 0

#     # Use previously used distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]   

#     # Calculate resultant intensity and spectrum
#     self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

#     # Set channel outputs on hardware
#     self.set_channel_outputs(self.channel_outputs)


# def fade_channel_output(self, channel_name):
#     """ Fades output channel forever. Exits on new event. """
#     self.logger.debug("Fading channel")

#     # Turn off all channels
#     self.turn_off_output()

#     # Use previously used illumination distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  

#     # Run fade loop until new event
#     while True:

#         # Fade up
#         for output_percent in range(0, 100, 10):
#             self.intensity = output_percent
#             self.channel_outputs[channel_name] = output_percent # TODO: copy the dict and pass in, dont need to set twice (here + in set function)
#             self.set_channel_outputs(self.channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)

#         # Fade down
#         for output_percent in range(100, 0, -10):
#             self.intensity = output_percent
#             self.channel_outputs[channel_name] = output_percent # TODO: copy the dict and pass in, dont need to set twice (here + in set function)
#             self.set_channel_outputs(self.channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)