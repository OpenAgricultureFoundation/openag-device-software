# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import type checks
from typing import Any

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver


def test_init():
    driver = AtlasPHDriver(name="Test", bus=2, address=0x77, simulate=True)


def test_read_ph():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    ph = driver.read_ph()
    assert ph == 4.001


def test_set_compensation_temperature():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    driver.set_compensation_temperature(26.0)


def test_take_low_point_calibration_reading():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    driver.take_low_point_calibration_reading(4.0)


def test_take_mid_point_calibration_reading():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    driver.take_mid_point_calibration_reading(7.0)


def test_take_high_point_calibration_reading():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    driver.take_high_point_calibration_reading(10.0)


def test_clear_calibration_readings():
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    driver.clear_calibration_readings()
