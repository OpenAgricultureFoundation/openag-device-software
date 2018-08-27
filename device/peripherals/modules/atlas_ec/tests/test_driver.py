# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import peripheral driver
from device.peripherals.modules.atlas_ph.driver import AtlasECDriver


def test_init() -> None:
    driver = AtlasECDriver(name="Test", bus=2, address=0x77, simulate=True)


def test_read_ec() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    ec = driver.read_ec()
    assert ec == 10.2


# def test_enable_electrical_conductivity_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.enable_electrical_conductivity_output()
#     assert error.exists() == True


# def test_disable_electrical_conductivity_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.enable_electrical_conductivity_output()
#     assert error.exists() == True


# def test_enable_total_dissolved_solids_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.enable_total_dissolved_solids_output()
#     assert error.exists() == True


# def test_disable_total_dissolved_solids_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.disable_total_dissolved_solids_output()
#     assert error.exists() == True


# def test_enable_salinity_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.enable_salinity_output()
#     assert error.exists() == True


# def test_disable_salinity_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.disable_salinity_output()
#     assert error.exists() == True


# def test_enable_specific_gravity_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.enable_specific_gravity_output()
#     assert error.exists() == True


# def test_disable_specific_gravity_output():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.disable_specific_gravity_output()
#     assert error.exists() == True


# def test_set_probe_type():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.set_probe_type(1.0)
#     assert error.exists() == True


# def test_take_dry_calibration_reading():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.take_dry_calibration_reading()
#     assert error.exists() == True


# def test_take_single_point_calibration_reading():
#     driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
#     error = driver.take_single_point_calibration_reading(7.0)
#     assert error.exists() == True
