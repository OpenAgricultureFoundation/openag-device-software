# Import standard python modules
from typing import Optional

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error

# Import led array
from device.peripherals.led_dac5578.array import LEDArray


class LEDManager:
	""" Manages an LED array controlled by the dac5578. """

	def __init__(self, *args, **kwargs):
	    """ Instantiates light array. Instantiates parent class, and initializes 
	        sensor variable name. """

	    # Instantiate parent class
	    super().__init__(*args, **kwargs)

	    # Initialize panel and channel configs
	    self.panel_configs = self.parameters["communication"]["panel"]
	    self.channel_configs = self.setup_dict["channel_configs"]

	    # Initialize variable names
	    self.intensity_name = self.parameters["variables"]["sensor"]["intensity_watts"]
	    self.spectrum_name = self.parameters["variables"]["sensor"]["spectrum_nm_percent"]
	    self.illumination_distance_name = self.parameters["variables"]["sensor"]["illumination_distance_cm"]
	    self.channel_output_name = self.parameters["variables"]["actuator"]["channel_output_percents"]

	    # Initialize LED array
	    self.array = LEDArray(self.name, self.panel_configs, self.channel_configs, self.simulate)

	    # Initialize health and probe functions
	    self.health = self.array.health
	    self.probe = self.array.probe


	def initialize(self):
		""" Initializes peripheral. """
		self.logger.debug("Initializing")

		# Set initial parameters
		self.intensity = None
		self.spectrum = None
		self.distance = None

		# Probe health
		error = self.probe(retry=True) 
		# TODO: What do we want to do with errors?


	def setup(self):
	    """ Sets up peripheral. """
	    self.logger.debug("Setting up")

	    # Turn off all array
	    error = self.array.turn_off()

	    # Check for errors
	    if error.exists():
	    	error.report("Unable to setup")
	    	self.logger.warning(error.trace)
	    	self.mode = Modes.ERROR

	    # Successful setup!
	    self.logger.debug("Setup successfully")


	


	@property
	def spectrum(self):
	    """ Gets spectrum value. """
	    return self.state.get_peripheral_reported_sensor_value(self.name, self.spectrum_name)


	@spectrum.setter
	def spectrum(self, value):
	    """ Sets spectrum value in shared state. """
	    self.state.set_environment_reported_sensor_value(self.name, self.spectrum_name, value, simple=True)
	    self.state.set_peripheral_reported_sensor_value(self.name, self.spectrum_name, value)


	@property
	def desired_spectrum(self):
	    """ Gets desired spectrum value from shared environment state if not 
	        in manual mode, otherwise gets it from peripheral state. """
	    if self.mode != Modes.MANUAL:
	    	return self.state.get_environment_desired_sensor_value(self.name, self.spectrum_name)
	    else:
	    	return self.state.get_peripheral_desired_sensor_value(self.name, self.spectrum_name)


	@property
	def intensity(self):
	    """ Gets intensity value. """
	    return self.state.get_peripheral_reported_sensor_value(self.name, self.intensity_name)


	@intensity.setter
	def intensity(self, value):
	    """ Sets intensity value in shared state. """
	    self.state.set_environment_reported_sensor_value(self.name, self.intensity_name, value, simple=True)
	    self.state.set_peripheral_reported_sensor_value(self.name, self.intensity_name, value)


	@property
	def desired_intensity(self):
	    """ Gets desired intensity value from shared environment state if not 
	        in manual mode, otherwise gets it from peripheral state. """
	    if self.mode != Modes.MANUAL:
	    	return self.state.get_environment_desired_sensor_value(self.name, self.intensity_name)
	    else:
	    	return self.state.get_peripheral_desired_sensor_value(self.name, self.intensity_name)


	@property
	def distance(self):
	    """ Gets distance value. """
	    return self.state.get_peripheral_reported_sensor_value(self.name, self.distance_name)


	@distance.setter
	def distance(self, value):
	    """ Sets distance value in shared state. """
	    self.state.set_environment_reported_sensor_value(self.name, self.distance_name, value, simple=True)
	    self.state.set_peripheral_reported_sensor_value(self.name, self.distance_name, value)


	@property
	def desired_distance(self):
	    """ Gets desired distance value from shared environment state if not 
	        in manual mode, otherwise gets it from peripheral state. """
	    if self.mode != Modes.MANUAL:
	    	return self.state.get_environment_desired_sensor_value(self.name, self.distance_name)
	    else:
	    	return self.state.get_peripheral_desired_sensor_value(self.name, self.distance_name)


	@property
	def channel_outputs(self):
	    """ Gets distance value. """
	    return self.state.get_peripheral_reported_actuator_value(self.name, self.channel_output_name)


	@channel_outputs.setter
	def channel_outputs(self, value):
	    """ Sets channel outputs value in shared state. """
	    self.state.set_environment_reported_actuator_value(self.name, self.channel_outputs_name, value)
	    self.state.set_peripheral_reported_actuator_value(self.name, self.channel_outputs_name, value)


	@property
	def desired_channel_outputs(self):
	    """ Gets desired distance value from shared environment state if not 
	        in manual mode, otherwise gets it from peripheral state. """
	    if self.mode != Modes.MANUAL:
	    	return self.state.get_environment_desired_actuator_value(self.name, self.channel_output_name)
	    else:
	    	return self.state.get_peripheral_desired_actuator_value(self.name, self.channel_output_name)




















































#     def update_channel_outputs(self):
#         """ Updates channel outputs. """
intensity
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