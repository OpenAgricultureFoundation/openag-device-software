# Import standard python modules
from typing import Optional

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger


class I2CDriverCore:
	""" Driver core for I2C device. """

	def __init__(self, name: str, logger_name: str, dunder_name: str, i2c_name: str, 
			bus: int, address: int, mux: Optional[int] = None, channel: Optional[int] = None, 
			simulate: bool = False) -> None:
		""" Instantiates I2C driver core. """

		# Initialize parameters
		self.simulate = simulate

		# Initialize logger
		self.logger = Logger(
		    name = logger_name,
		    dunder_name = dunder_name,
		)

		# Initialize I2C
		self.i2c = I2C(
			name = i2c_name,
			bus = bus,
			address = address,
			mux = mux,
			channel = channel,
			simulate = simulate,
		)
