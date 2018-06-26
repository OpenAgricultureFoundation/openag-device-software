# Import standard python libraries
import sys

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_do.driver import AtlasDODriver
except:
    # ... if running tests from same dir as driver.py
    sys.path.append("../../../../")
    from device.peripherals.modules.atlas_do.driver import AtlasDODriver


def test_init():
    driver = AtlasDODriver(name="Test", bus=2, address=0x77, simulate=True)


def test_read_dissolved_oxygen():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    dissolved_oxygen, error = driver.read_dissolved_oxygen()
    assert error.exists() == True


def test_set_compensation_temperature():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    error = driver.set_compensation_temperature(23.6)
    assert error.exists() == True


def test_set_compensation_pressure():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    error = driver.set_compensation_pressure(50.0)
    assert error.exists() == True


def test_set_compensation_electrical_conductivity():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    error = driver.set_compensation_electrical_conductivity(3.2)
    assert error.exists() == True


def test_enable_mg_l_output():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    error = driver.enable_mg_l_output()
    assert error.exists() == True


def test_disable_mg_l_output():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    error = driver.disable_mg_l_output()
    assert error.exists() == True


def test_enable_percent_saturation_output():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    error = driver.enable_percent_saturation_output()
    assert error.exists() == True


def test_disable_percent_saturation_output():
    driver = AtlasDODriver("Test", 2, 0x77, simulate=True)
    error = driver.disable_percent_saturation_output()
    assert error.exists() == True
