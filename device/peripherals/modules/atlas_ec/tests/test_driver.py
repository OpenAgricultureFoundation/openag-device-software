# Import standard python libraries
import sys, os

# Get current working directory
cwd = os.getcwd()
print("Running test from: {}".format(cwd))

# Set correct import path
if cwd.endswith("atlas_ec"):
    print("Running test locally")
    os.chdir("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running test globally")
else:
    print("Running tests from invalid location")
    sys.exit(0)

# Import driver
from device.peripherals.modules.atlas_ec.driver import AtlasECDriver


def test_init():
    driver = AtlasECDriver(name="Test", bus=2, address=0x77, simulate=True)


def test_read_electrical_conductivity():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    electrical_conductivity, error = driver.read_electrical_conductivity()
    assert electrical_conductivity == None
    assert error.exists() == True


def test_set_compensation_temperature():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.set_compensation_temperature(temperature=23.6)
    assert error.exists() == True


def test_enable_electrical_conductivity_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.enable_electrical_conductivity_output()
    assert error.exists() == True


def test_disable_electrical_conductivity_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.enable_electrical_conductivity_output()
    assert error.exists() == True


def test_enable_total_dissolved_solids_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.enable_total_dissolved_solids_output()
    assert error.exists() == True


def test_disable_total_dissolved_solids_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.disable_total_dissolved_solids_output()
    assert error.exists() == True


def test_enable_salinity_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.enable_salinity_output()
    assert error.exists() == True


def test_disable_salinity_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.disable_salinity_output()
    assert error.exists() == True


def test_enable_specific_gravity_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.enable_specific_gravity_output()
    assert error.exists() == True


def test_disable_specific_gravity_output():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.disable_specific_gravity_output()
    assert error.exists() == True


def test_set_probe_type():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.set_probe_type(1.0)
    assert error.exists() == True


def test_take_dry_calibration_reading():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.take_dry_calibration_reading()
    assert error.exists() == True


def test_take_single_point_calibration_reading():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.take_single_point_calibration_reading(7.0)
    assert error.exists() == True


def test_take_low_point_calibration_reading():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.take_low_point_calibration_reading(4.0)
    assert error.exists() == True


def test_take_high_point_calibration_reading():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.take_high_point_calibration_reading(10.0)
    assert error.exists() == True


def test_clear_calibration_readings():
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    error = driver.clear_calibration_readings()
    assert error.exists() == True
