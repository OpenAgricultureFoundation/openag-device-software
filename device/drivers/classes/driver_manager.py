# Import standard python modules
import time

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.health import Health


class DriverManager:
	""" Driver manager for I2C device. """


	def __init__(self, logger_name: str, dunder_name: str, 
		health_minimum: int = 80, health_updates: int = 20) -> None:
		""" Initializes I2C driver. """

		# Initialize logger
		self.logger = Logger(
		    name = logger_name,
		    dunder_name = dunder_name,
		)

		# Initialize health
		self.health = Health(
		    updates = health_updates, 
		    minimum = health_minimum,
		)


	def probe(self) -> None:
		raise NotImplementedError


	def reset(self) -> None:
		raise NotImplementedError


	def shutdown(self) -> None:
		raise NotImplementedError

