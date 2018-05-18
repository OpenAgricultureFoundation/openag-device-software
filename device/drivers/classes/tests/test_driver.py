# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.classes.driver import Driver
except:
	# ... if running tests from same dir as driver.py
	sys.path.append("../../../")
	from device.drivers.classes.driver import Driver


def test_init():
	driver = Driver()
