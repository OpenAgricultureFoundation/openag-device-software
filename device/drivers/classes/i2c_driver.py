# Import standard python modules
import logging, time

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.health import Health


class I2CDriver:
	""" Driver for I2C device. """

	def __init__(self, name, bus, address, mux=None, channel=None, 
			simulate=False, health_minimum=80, health_updates=20):
		""" Instantiates I2C driver. """

		# Initialize passed in parameters
		self.name = name
		self.bus = bus
		self.address = address
		self.mux = mux
		self.channel = channel
		self.simulate = simulate
		self.minimum_health = health_minimum
		self.health_updates = health_updates

		# Initialize health and I2C objects
		self.health = Health(updates=health_updates, minimum=health_minimum)
		self.i2c = I2C(name, bus, address, mux=mux, channel=channel, simulate=simulate)

		# Initialize logger
		extra = {'console_name':self.name, 'file_name': self.name}
		logger = logging.getLogger(__name__)
		self.logger = logging.LoggerAdapter(logger, extra)


	def check_health():
		raise NotImplementedError
