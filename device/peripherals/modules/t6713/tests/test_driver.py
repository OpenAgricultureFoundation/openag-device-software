# Import standard python libraries
import sys, os

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("t6713"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import sensor
from device.peripherals.modules.t6713.driver import T6713Driver
    

def test_init():
    driver = T6713Driver(
        name = "Test", 
        bus = 2, 
        address = 0x77, 
        simulate=True,
    )
    

def test_read_carbon_dioxide():
    driver = T6713Driver("Test", 2, 0x77, simulate=True)
    carbon_dioxide, error = driver.read_carbon_dioxide()
    assert error.exists() == False
    assert carbon_dioxide == 0.0


def test_read_status():
    driver = T6713Driver("Test", 2, 0x77, simulate=True)
    status, error = driver.read_status()
    assert error.exists() == False
    assert status.error_condition == False
    assert status.flash_error == False
    assert status.calibration_error == False
    assert status.rs232 == False
    assert status.rs485 == False
    assert status.i2c == False
    assert status.warm_up_mode == False
    assert status.single_point_calibration == False


def test_enable_abc_logic():
    driver = T6713Driver("Test", 2, 0x77, simulate=True)
    error = driver.enable_abc_logic()
    assert error.exists() == False


def test_disable_abc_logic():
    driver = T6713Driver("Test", 2, 0x77, simulate=True)
    error = driver.disable_abc_logic()
    assert error.exists() == False
