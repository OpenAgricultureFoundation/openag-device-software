# Import standard python libraries
import sys

# Import sensor module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.t6713.sensor import T6713Sensor
except:
    # ... if running tests from same dir as sensor.py
    sys.path.append("../../../../")
    from device.peripherals.modules.t6713.sensor import T6713Sensor
    

def test_init():
    sensor = T6713Sensor(
        name = "Test", 
        bus = 2, 
        address = 0x64, 
        simulate=True,
    )
    

def test_read_carbon_dioxide():
    sensor = T6713Sensor("Test", 2, 0x64, simulate=True)
    carbon_dioxide, error = sensor.read_carbon_dioxide()
    assert error.exists() == False
    assert carbon_dioxide == 430


def test_probe():
    sensor = T6713Sensor("Test", 2, 0x64, simulate=True)
    error = sensor.probe()
    assert error.exists() == False


def test_initialize():
    sensor = T6713Sensor("Test", 2, 0x64, simulate=True)
    error = sensor.initialize()
    assert error.exists() == False


def test_setup():
    sensor = T6713Sensor("Test", 2, 0x64, simulate=True)
    error = sensor.setup()
    assert error.exists() == False
