import logging, time, threading

# TODO: Inherit from a Peripherals class, perhaps even a Light Panel class

class LightPanelTaurus(object):
	""" A light panel with six independently controlled channels that can 
	create the Taurus light spectrum.
	
	Attributes:
		example_attr: An example attribute. 
	"""

	# Initialize logger
	logger = logging.getLogger(__name__)

	# Initialize actuator parameters
	sampling_rate_seconds = 5.0
	sampling_duration_seconds = None

	# Initialize actuator values
	spectrum = None
	intensity = None

	def __init__(self, config):
		""" This is an example function description. """
		self.bus = config["bus"]
		self.mux = config["mux"]
		self.channel = config["channel"]
		self.address = config["address"]


	def run(self):
		t = threading.Thread(target=self.start_thread)
		t.start()


	def start_thread(self):
		""" Description. """
		
		while True:
			start_time_ms = time.time()

			# TODO: Get desired actuator values
			
			# Set actuator values
			self.set_spectrum("Blue")
			self.set_intensity(300)

			# Try to enforce sampling rate
			self.sampling_duration_seconds = (time.time() - start_time_ms) * 100

			if self.sampling_duration_seconds > self.sampling_rate_seconds:
				self.logger.warning("Sampling duration > sampling rate")
			else:
				time.sleep(self.sampling_rate_seconds - self.sampling_duration_seconds)


	def set_spectrum(self, spectrum):
		""" Description. """
		self.spectrum = spectrum
		self.logger.info("Set spectrum to: {}".format(self.spectrum))


	def set_intensity(self, intensity):
		""" Description. """
		self.intensity = intensity
		self.logger.info("Set intensity to: {}".format(self.intensity))
