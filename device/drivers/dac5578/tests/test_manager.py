# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.dac5578.manager import DAC5578Manager
except:
	# ... if running tests from same dir as dac5578.py
	sys.path.append("../../../")
	from device.drivers.dac5578.manager import DAC5578Manager


# TODO: Need a way to test failure cases better


def test_init():
	dac5578_manager = DAC5578Manager("Test", 2, 0x77, simulate=True)


def test_set_output():
	dac5578_manager = DAC5578Manager("Test", 2, 0x77, simulate=True)

	# Standard case
	error = dac5578_manager.set_output(0, 50)
	assert error.exists() == False


def test_set_output():
	dac5578_manager = DAC5578Manager("Test", 2, 0x77, simulate=True)

	# Standard case
	outputs = {0: 90.0, 1: 100, 2: 50, 3: 25, 4: 12.5, 5: 88, 6:74.4, 7:77.7}
	error = dac5578_manager.set_outputs(outputs)
	assert error.exists() == False

