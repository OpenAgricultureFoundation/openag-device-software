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
    print("Running tests from invalid location")
    sys.exit(0)

# Import driver
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver
    

def test_init():
    driver = AtlasPHDriver(
        name = "Test", 
        bus = 2, 
        address = 0x77, 
        simulate=True,
    )
    

def test_read_potential_hydroden():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    potential_hydrogen, error = driver.read_potential_hydrogen()
    assert error.exists() == True
    assert potential_hydrogen == None


def test_set_compensation_temperature():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    error = driver.set_compensation_temperature(temperature=23.6)
    assert error.exists() == True


def test_take_low_point_calibration_reading():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    error = driver.take_low_point_calibration_reading(4.0)
    assert error.exists() == True


def test_take_mid_point_calibration_reading():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    error = driver.take_mid_point_calibration_reading(4.0)
    assert error.exists() == True


def test_take_high_point_calibration_reading():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    error = driver.take_high_point_calibration_reading(10.0)
    assert error.exists() == True


def test_clear_calibration_readings():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    error = driver.clear_calibration_readings()
    assert error.exists() == True
