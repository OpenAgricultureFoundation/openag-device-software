# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.classes.driver_manager import DriverManager
except:
	# ... if running tests from same dir as i2c_driver.py
	sys.path.append("../../../")
	from device.drivers.classes.driver_manager import DriverManager


def test_init():
	driver_manager = DriverManager(
		logger_name = "TEST",
		dunder_name = __name__,
		health_minimum = 80,
		health_updates = 20,
	)