# Import standard python libraries
import sys, os

# Get current working directory
cwd = os.getcwd()
print("Running test from: {}".format(cwd))

# Set correct import path
if cwd.endswith("atlas_ph"):
    print("Running test locally")
    os.chdir("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running test globally")
else:
    print("Running test from invalid location")
    sys.exit(0)

# Import sensor
from device.peripherals.modules.atlas_ph.sensor import AtlasPHSensor
    

def test_init():
    sensor = AtlasPHSensor(
        name = "Test", 
        bus = 2, 
        address = 0x64, 
        simulate=True,
    )
    

def test_read_potential_hydrogen():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    ph, error = sensor.read_potential_hydrogen()
    assert error.exists() == False
    assert ph == 7.4


def test_set_compensation_temperature():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.set_compensation_temperature(23.6)
    assert error.exists() == True


def test_take_low_point_calibration_reading():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.take_low_point_calibration_reading(4.0)
    assert error.exists() == True


def test_take_mid_point_calibration_reading():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.take_mid_point_calibration_reading(4.0)
    assert error.exists() == True


def test_take_high_point_calibration_reading():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.take_high_point_calibration_reading(10.0)
    assert error.exists() == True


def test_clear_calibration_readings():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.clear_calibration_readings()
    assert error.exists() == True


def test_probe():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.probe()
    assert error.exists() == False


def test_initialize():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.initialize()
    assert error.exists() == False


def test_setup():
    sensor = AtlasPHSensor("Test", 2, 0x64, simulate=True)
    error = sensor.setup()
    assert error.exists() == False
