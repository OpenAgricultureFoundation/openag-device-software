# Import standard python libraries
import sys

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.drivers.classes.i2c_driver_core import I2CDriverCore
except:
    # ... if running tests from same dir as i2c_driver.py
    sys.path.append("../../../")
    from device.drivers.classes.i2c_driver_core import I2CDriverCore


def test_init():
    driver_core = I2CDriverCore(
        name = "Test", 
        bus = 2, 
        address = 0x40, 
        mux = None, 
        channel = None, 
        simulate = True,
        i2c_name = "Driver-Test",
        logger_name = "DriverCore(Test)",
        dunder_name = __name__,
    )