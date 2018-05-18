# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.classes.i2c_driver import I2CDriver
except:
	# ... if running tests from same dir as i2c_driver.py
	sys.path.append("../../../")
	from device.drivers.classes.i2c_driver import I2CDriver


def test_init():
	driver = I2CDriver("test", 2, 0x77, simulate=True)