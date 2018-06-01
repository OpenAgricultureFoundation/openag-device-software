# Import standard python libraries
import sys

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.classes.atlas_driver import AtlasDriver
except:
    # ... if running tests from same dir as AtlasDriver_ec.py
    sys.path.append("../../../")
    from device.peripherals.classes.atlas_driver import AtlasDriver
    

def test_init():
    driver = AtlasDriver(
        name = "Test", 
        bus = 2, 
        address = 0x77, 
        logger_name = "AtlasDriver", 
        i2c_name = "AtlasDriver", 
        dunder_name = __name__, 
        simulate = True,
    )


def test_read_info():
    driver = AtlasDriver("Test", 2, 0x77, "AtlasDriver", "AtlasDriver", __name__, simulate=True)
    driver_type, firmware_version, error = driver.read_info()
    assert error.exists() == True


def test_read_status():
    driver = AtlasDriver("Test", 2, 0x77, "AtlasDriver", "AtlasDriver", __name__, simulate=True)
    prev_restart_reason, voltage, error = driver.read_status()
    assert error.exists() == True
    assert prev_restart_reason == None
    assert voltage == None


def test_enable_protocol_lock():
    driver = AtlasDriver("Test", 2, 0x77, "AtlasDriver", "AtlasDriver", __name__, simulate=True)
    error = driver.enable_protocol_lock()
    assert error.exists() == True


def test_disable_protocol_lock():
    driver = AtlasDriver("Test", 2, 0x77, "AtlasDriver", "AtlasDriver", __name__, simulate=True)
    error = driver.disable_protocol_lock()
    assert error.exists() == True


def test_enable_led():
    driver = AtlasDriver("Test", 2, 0x77, "AtlasDriver", "AtlasDriver", __name__, simulate=True)
    error = driver.enable_led()
    assert error.exists() == True


def test_disable_led():
    driver = AtlasDriver("Test", 2, 0x77, "AtlasDriver", "AtlasDriver", __name__, simulate=True)
    error = driver.disable_led()
    assert error.exists() == True


def test_enable_sleep_mode():
    driver = AtlasDriver("Test", 2, 0x77, "AtlasDriver", "AtlasDriver", __name__, simulate=True)
    error = driver.enable_sleep_mode()
    assert error.exists() == False
