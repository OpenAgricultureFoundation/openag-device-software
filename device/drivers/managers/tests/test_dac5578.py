# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.managers.dac5578 import DAC5578Manager
except:
	# ... if running tests from same dir as dac5578.py
	sys.path.append("../../../")
	from device.drivers.managers.dac5578 import DAC5578Manager


def test_init():
	dac5578_manager = DAC5578Manager("TEST", 2, 0x77, simulate=True)


def test_set_output():
	dac5578_manager = DAC5578Manager("TEST", 2, 0x77, simulate=True)
	error = dac5578_manager.set_output(0, 50)
	assert error == None
	assert False