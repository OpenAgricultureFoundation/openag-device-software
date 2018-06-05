# Import standard python libraries
import sys

# Import sensor module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_do.sensor import AtlasDOSensor
except:
    # ... if running tests from same dir as sensor.py
    sys.path.append("../../../../")
    from device.peripherals.modules.atlas_do.sensor import AtlasDOSensor
    

def test_init():
    sensor = AtlasDOSensor(
        name = "Test", 
        bus = 2, 
        address = 0x64, 
        simulate=True,
    )
    

def test_read_dissolved_oxygen():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    do, error = sensor.read_dissolved_oxygen()
    assert error.exists() == False
    assert do == 10.2


def test_set_compensation_temperature():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.set_compensation_temperature(23.6)
    assert error.exists() == True


def test_set_compensation_pressure():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.set_compensation_pressure(50.0)
    assert error.exists() == True


def test_set_compensation_electrical_conductivity():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.set_compensation_electrical_conductivity(3.4)
    assert error.exists() == True


def test_enable_mg_l_output():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.enable_mg_l_output()
    assert error.exists() == True


def test_disable_percent_saturation_output():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.disable_percent_saturation_output()
    assert error.exists() == True


def test_probe():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.probe()
    assert error.exists() == False


def test_initialize():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.initialize()
    assert error.exists() == False


def test_setup():
    sensor = AtlasDOSensor("Test", 2, 0x64, simulate=True)
    error = sensor.setup()
    assert error.exists() == False
