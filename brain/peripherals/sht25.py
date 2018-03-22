import logging, time, threading

# TODO: Inherit from a Peripherals class, perhaps even a Sensor class or ...
# TODO: Peripheral -> TempHumidSensor ?

class SHT25(object):
	""" A temperature and humidity sensor.
	
	Attributes:
		temperature: Temperature measurement in degrees Celcuis.
		humidity: Humidity measurement in %RH
	"""

	# Initialize logger
	logger = logging.getLogger(__name__)

	# Initialize sensor parameters
	sampling_rate_seconds = 2.5
	sampling_duration_seconds = None

	# Initialize sensor variable names
	temperature_name = "air_temperature"
	humidity_name = "air_humidity"

	# Initialize sensor values
	temperature = None
	humidity = None


	def __init__(self, config, name):
		""" This is an example function description. """
		self.bus = config["bus"]
		self.mux = config["mux"]
		self.channel = config["channel"]
		self.address = config["address"]
		self.name = name


	def run(self, env):
		t = threading.Thread(target=self.start_thread, args=(env,))
		t.start()


	def start_thread(self, env):
		""" Description. """
		while True:
			start_time_ms = time.time()
			
			# Get sensor values
			self.get_temperature()
			self.get_humidity()

			# Update shared environment safely
			with threading.Lock():
				env.set(self.name, self.temperature_name, self.temperature)
				env.set(self.name, self.humidity_name, self.humidity)

			# Try to enforce sampling rate
			self.sampling_duration_seconds = (time.time() - start_time_ms) * 1000
			if self.sampling_duration_seconds > self.sampling_rate_seconds:
				self.logger.warning("Sampling duration > sampling rate")
			else:
				time.sleep(self.sampling_rate_seconds - self.sampling_duration_seconds)


	def get_temperature(self):
		""" Description. """
		self.temperature = 22.0
		self.logger.debug("Got temperature of: {}".format(self.temperature))


	def get_humidity(self):
		""" Description. """
		self.humidity = 23
		self.logger.debug("Got humidity of: {}".format(self.humidity))