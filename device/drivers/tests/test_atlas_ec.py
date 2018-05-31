# Import standard python libraries
import sys

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.atlas_ec import AtlasEC
except:
	# ... if running tests from same dir as dac5578.py
	sys.path.append("../../")
	from device.drivers.atlas_ec import AtlasEC
	

def test_init():
	sensor = AtlasEC("Test", 2, 0x77, simulate=True)


def test_read_info():
	sensor = AtlasEC("Test", 2, 0x77, simulate=True)
	sensor_type, firmware_version, error = sensor.read_info()
	assert error.exists() == True