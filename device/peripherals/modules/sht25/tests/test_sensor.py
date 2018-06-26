# Import standard python libraries
import sys, os

# Get current working directory
cwd = os.getcwd()
print("Running test from: {}".format(cwd))

# Set correct import path
if cwd.endswith("sht25"):
    print("Running test locally")
    os.chdir("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running test globally")
else:
    print("Running test from invalid location")
    sys.exit(0)

# Import manager
from device.peripherals.modules.sht25.sensor import SHT25Sensor


def test_init():
    sensor = SHT25Sensor(name="Test", bus=2, address=0x64, simulate=True)


def test_read_temperature():
    sensor = SHT25Sensor("Test", 2, 0x64, simulate=True)
    temperature, error = sensor.read_temperature()
    assert error.exists() == False
    assert temperature == 20.2


def test_read_humidity():
    sensor = SHT25Sensor("Test", 2, 0x64, simulate=True)
    humidity, error = sensor.read_humidity()
    assert error.exists() == False
    assert humidity == 40.4


def test_probe():
    sensor = SHT25Sensor("Test", 2, 0x64, simulate=True)
    error = sensor.probe()
    assert error.exists() == False


def test_initialize():
    sensor = SHT25Sensor("Test", 2, 0x64, simulate=True)
    error = sensor.initialize()
    assert error.exists() == False


def test_setup():
    sensor = SHT25Sensor("Test", 2, 0x64, simulate=True)
    error = sensor.setup()
    assert error.exists() == False
