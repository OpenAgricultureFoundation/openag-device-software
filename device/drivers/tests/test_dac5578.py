# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.dac5578 import DAC5578
except:
	# ... if running tests from same dir as dac5578.py
	sys.path.append("../../")
	from device.drivers.dac5578 import DAC5578


def test_init():
	dac5578 = DAC5578("test", 2, 0x77, simulate=True)


def test_set_output():
	dac5578 = DAC5578("test", 2, 0x77, simulate=True)
	error = dac5578.set_output(0, 50)
	assert error == None


def test_get_status():
	dac5578 = DAC5578("test", 2, 0x77, simulate=True)
	status, error = dac5578.get_status()
	assert error == None
	assert status.powered[0] == True
