# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.cores.dac5578 import DAC5578Core
except:
	# ... if running tests from same dir as dac5578.py
	sys.path.append("../../../")
	from device.drivers.cores.dac5578 import DAC5578Core
	


def test_init():
	dac5578_core = DAC5578Core("TEST", 2, 0x77, simulate=True)


def test_set_output():
	dac5578_core = DAC5578Core("TEST", 2, 0x77, simulate=True)
	error = dac5578_core.set_output(0, 50)
	assert error == None
