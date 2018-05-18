
# Import standard python modules
import time

# Import driver parent class
from device.drivers.classes.i2c_driver import I2CDriver



class DAC5578(I2CDriver):
	""" Driver for DAC5578 digital to analog converter. """

	def __init___(self, *args, **kwargs):
		""" Instantiates DAC5578 driver. """

		super().__init__(*args, **kwargs)





	def check_health(self):
		...


	def set_output(self, channel, percent):
	    """ Sets output value to channel. """

	    # Check valid channel range
	    if channel < 0 or channel > 7:
	    	return "Channel out of range, must be within 0-7"

	   	# Check valid value range
	   	if percent < 0 or percent > 100:
	   		return "Output percent out of range, must be within 0-100"

	   	# Convert output percent to byte
	   	byte = 255 - int(percent * 2.55) # 255 is off, 0 is on

	   	# Check if driver is simulated
	   	if self.simulate:
	   		self.logger.debug("Simulating writing to dac5578({}): ch={}, byte={}".format(self.name, channel, byte))
	   		return None

	   	# Sensor is not simulated!
		self.logger.debug("Writing to dac5578({}): ch={}, byte={}".format(self.name, channel, byte))
		error = self.i2c.write([0x30+software_channel, output_byte, 0x00])

		# Check for errors
		if error != None:
			self.logger.error("Unable to set output on dac5578({})".format(self.name))








	# def read_power_down_register(self):
	#     """ Reads power down register and return byte. """

	#     # Check if sensor is simulated
	#     if self.simulate:
	#         self.logger.debug("Simulating reading power down register")
	#         return 0x00

	#     # Sensor is not simulated!
	#     self.logger.debug("Reading power down register")
	#     return self.i2c.read_register(0x40)