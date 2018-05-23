
# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.math import interpolate

# Import device drivers
from device.drivers.dac5578.manager import DAC5578Manager as DAC5578


class Panel:
	""" An led panel controlled by a dac5578. """

	def __init__(self, name, bus, address, mux=None, channel=None, simulate=False):
		""" Instantiates panel. """

		# Instantiate logger
		self.logger = Logger(
			name = "LEDPanel({})".format(name),
			dunder_name = __name__,
		)
		
		# Instantiate name
		self.name = name

		# Instantiate driver
		self.dac5578 = DAC5578(
			name = name,
			bus = bus,
			address = address,
			mux = mux,
			channel = channel,
			simulate = simulate,
		)

		# Instantiate health & probe
		self.health = self.dac5578.health
		self.probe = self.dac5578.probe

 
	def initialize(self) -> Error:
		""" Initializes panel by probing driver with retry enabled. """
		error = self.dac5578.probe(retry=True)
		if error.exists():
			error.append("Panel initialization failed")
			self.logger.warning(error)
			return error
		else:
			return Error(None)


	def set_output(self, channel: int, percent: int) -> Error:
		""" Sets output on dac and checks for errors. """
		error = self.dac5578.set_output(channel, percent)
		if error.exists():
			error.append("Panel failed to set output")
			return error
		else:
			return Error(None)


	def set_outputs(self, outputs: dict) -> Error:
        """ Sets output channels to output percents. Only sets mux once. """
        error = self.core.set_outputs(outputs)
        if error.exists():
        	error.append("Panel failed to set outputs")
        	return error
        else:
        	return Error(None)


    def approximate_spectral_power(self, channels: dict, desired: dict) -> dict:
    	""" Approximates spectral power, returns outputs. """

    	# Get desired vector
    	desired_vector = []
    	for entry in desired:
    		desired_vector.append(entry["power_watts"])
    	desired_vector = np.array(desired_vector)

    	# Get channel matrix
    	channel_matrix = []
    	for channel in channels:
    		channel_vector = []
    		for entry in channel["distribution"]:
    			channel_vector.append(entry["power_watts"])
    		channel_matrix.append(channel_vector)
    	channel_matrix = np.array(channel_matrix)
    	channel_matrix = np.transpose(channel_matrix)

    	# Calculate outputs
    	weighted_outputs = np.linalg.lstsq(channel_matrix, desired_vector, rcond=None)[0]
    	normalized_outputs = weighted_outputs / max(weighted_outputs)
    	output_list = []
    	for element in normalized_outputs:
    		output_list.append(round(element, 2))

    	# Build output dict
    	outputs = {}
    	for channel in channels:
    		output

    	
    	# Return outputs
    	return outputs


