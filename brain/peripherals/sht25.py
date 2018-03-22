import logging, time, threading

# TODO: Inherit from a Peripherals class, perhaps even a Sensor class or ...
# TODO: Peripheral -> TempHumidSensor ?

class SHT25(object):
	""" A temperature and humidity sensor.
	
	Attributes:
		temperature: Temperature measurement.
		humidity: Humidity measurement.
	"""

	# Initialize logger
	logger = logging.getLogger(__name__)

	# Initialize sensor parameters
	sampling_rate_seconds = 3
	sampling_duration_seconds = None

	# Initialize sensor values
	temperature = None
	humidity = None
	initialized = False

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
		self.temperature_unit = config["variables"]["temperature"]["unit"]
		self.humidity_name = config["variables"]["humidity"]["name"]
		self.humidity_unit = config["variables"]["humidity"]["unit"]

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

			# Initialization State
			# System Transitions: INIT --> NOS or INIT --> CONFIG
			# Class Transitions: INIT --> ERROR
			if self.state == self.sys.INIT:
				if not self.initialized:
					self.initialize()
				else:
					# Check system state for transition
					if (self.sys.state == self.sys.NOS) or (self.sys.state == self.sys.CONFIG):
						self.state = self.sys.state
					else:
						self.state = self.sys.INVALID_TRANSITION
					time.sleep(0.2) # 200 ms

			# Normal Operation State
			# System Transitions: NOS --> CONFIG
			# Class Transitions: NOS --> ERROR
			if self.state == self.sys.NOS:
				# Initialize start time for sampling rate management
				start_time_ms = time.time()
				
				# Get sensor values
				self.get_temperature()
				self.get_humidity()

				# Update shared environment object
				with threading.Lock():
					self.env.set_sensor(self.name, self.temperature_name, self.temperature)
					self.env.set_sensor(self.name, self.humidity_name, self.humidity)

				# Try to enforce sampling rate
				self.sampling_duration_seconds = (time.time() - start_time_ms) * 1000
				if self.sampling_duration_seconds > self.sampling_rate_seconds:
					self.logger.warning("Sampling duration > sampling rate")
				else:
					time.sleep(self.sampling_rate_seconds - self.sampling_duration_seconds)


			# Configuration State


			# Error State



	def initialize(self):
		""" Initialize the physical sensor. """
		try:
			self.initialized = True
		except:
			self.logger.exception("Unable to initialize")
			self.initialized = False
			self.sys.state = self.sys.ERROR


	def get_temperature(self):
		""" Description. """
		try:
			self.temperature = 22.0
			self.logger.debug("Got temperature of: {}".format(self.temperature))
		except:
			self.logger.exception("Unable to get temperature")
			self.sys.state = self.sys.ERROR


	def get_humidity(self):
		""" Description. """
		try:
			self.humidity = 23
			self.logger.debug("Got humidity of: {}".format(self.humidity))
		except:
			self.logger.exception("Unable to get humidity")
			self.sys.state = self.sys.ERROR