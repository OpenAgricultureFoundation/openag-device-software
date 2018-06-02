# Import standard python libraries
import sys

# Import sensor module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ec.sensor import AtlasECSensor
except:
    # ... if running tests from same dir as sensor.py
    sys.path.append("../../../../")
    from device.peripherals.modules.atlas_ec.sensor import AtlasECSensor
    

def test_init():
    sensor = AtlasECSensor(
        name = "Test", 
        bus = 2, 
        address = 0x64, 
        simulate=True,
    )
    

def test_read_electrical_conductivity():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    ec, error = sensor.read_electrical_conductivity()
    assert error.exists() == False
    assert ec == 2.1


def test_set_compensation_temperature():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.set_compensation_temperature(23.6)
    assert error.exists() == True


def test_set_probe_type():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.set_probe_type("1.0")
    assert error.exists() == True


def test_enable_electrical_conductivity_output():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.enable_electrical_conductivity_output()
    assert error.exists() == True


def test_disable_total_dissolved_solids_output():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.disable_total_dissolved_solids_output()
    assert error.exists() == True


def test_disable_salinity_output():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.disable_salinity_output()
    assert error.exists() == True


def test_disable_specific_gravity_output():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.disable_specific_gravity_output()
    assert error.exists() == True


def test_initialize():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.initialize()
    assert error.exists() == False


def test_setup():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.setup()
    assert error.exists() == False


def test_take_dry_calibration_reading():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.take_dry_calibration_reading()
    assert error.exists() == True


def test_single_point_calibration_reading():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.take_single_point_calibration_reading(7.0)
    assert error.exists() == True


def test_take_low_point_calibration_reading():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.take_low_point_calibration_reading(4.0)
    assert error.exists() == True


def test_take_high_point_calibration_reading():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.take_high_point_calibration_reading(10.0)
    assert error.exists() == True


def test_clear_calibration_readings():
    sensor = AtlasECSensor("Test", 2, 0x64, simulate=True)
    error = sensor.clear_calibration_readings()
    assert error.exists() == True
