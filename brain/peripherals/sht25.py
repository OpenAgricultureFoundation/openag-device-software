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
	sampling_rate_seconds = 3
	sampling_duration_seconds = None

	# Initialize sensor values
	temperature = None
	humidity = None

	# Initialize class
	def __init__(self, config, name, env, sys):
		""" This is an example function description. """
		self.name = name
		self.env = env
		self.sys = sys
		self.bus = config["comms"]["bus"]
		self.mux = config["comms"]["mux"]
		self.channel = config["comms"]["channel"]
		self.address = config["comms"]["address"]
		self.temperature_name = config["variables"]["temperature"]["name"]
		self.humidity_name = config["variables"]["humidity"]["name"]

		# Initialize state variables in class object
		self._prev_state = self.sys.BOOT
		self._state = self.sys.INIT

		# Initialize peripheral state in system object
		with threading.Lock():
			self.sys.peripheral[self.name] = {"prev_state": self._prev_state, "state": self._state}


	def run(self):
		t = threading.Thread(target=self.start_thread, )
		t.daemon = True
		t.start()


	@property
	def state(self):
		return self._state

	@state.setter
	def state(self, value):
		if value != self._state:
			self.logger.info("Transition state from {} to {}".format(self.state, value))
			
			self._prev_state = self._state
			self._state = value

			with threading.Lock():
				self.sys.peripheral[self.name]["state"] = self._state
				self.sys.peripheral[self.name]["prev_state"] = self._prev_state


	def start_thread(self):
		""" Description. """
		self.logger.debug("Starting thread")

		# Run forever
		while True:

			self.state = self.sys.NOS

			# Normal Operation State
			if self.state == self.sys.NOS:

				# Initialize start time for sampling rate management
				start_time_ms = time.time()
				
				# Get sensor values
				self.get_temperature()
				self.get_humidity()

				# Update shared environment object
				with threading.Lock():
					self.env.set(self.name, self.temperature_name, self.temperature)
					self.env.set(self.name, self.humidity_name, self.humidity)

				# Try to enforce sampling rate
				self.sampling_duration_seconds = (time.time() - start_time_ms) * 1000
				if self.sampling_duration_seconds > self.sampling_rate_seconds:
					self.logger.warning("Sampling duration > sampling rate")
				else:
					time.sleep(self.sampling_rate_seconds - self.sampling_duration_seconds)


	def get_temperature(self):
		""" Description. """
		try:
			self.temperature = 22.0
			self.logger.debug("Got temperature of: {}".format(self.temperature))
		except:
			self.logger.exception("Unable to get temperature")
			# self.set_state(self.sys.ERROR)



	def get_humidity(self):
		""" Description. """
		try:
			self.humidity = 23
			self.logger.debug("Got humidity of: {}".format(self.humidity))
		except:
			self.logger.exception("Unable to get humidity")