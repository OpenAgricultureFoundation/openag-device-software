# Import standard python libraries
import sys, os, pytest

# Import manager
from device.peripherals.modules.sht25.driver import SHT25Driver
from device.comms.i2c2.mux_simulator import MuxSimulator


def test_init() -> None:
    driver = SHT25Driver(
        name="Test", bus=2, address=0x77, simulate=True, mux_simulator=MuxSimulator()
    )


def test_read_temperature() -> None:
    driver = SHT25Driver("Test", 2, 0x77, simulate=True, mux_simulator=MuxSimulator())
    temperature = driver.read_temperature()
    assert temperature == 24.0


def test_read_humidity() -> None:
    driver = SHT25Driver("Test", 2, 0x77, simulate=True, mux_simulator=MuxSimulator())
    humidity = driver.read_humidity()
    assert humidity == 70.0


def test_read_user_register() -> None:
    driver = SHT25Driver("Test", 2, 0x77, simulate=True, mux_simulator=MuxSimulator())
    user_register = driver.read_user_register()
    assert user_register.end_of_battery == False
    assert user_register.heater_enabled == False
    assert user_register.reload_disabled == False


def test_reset() -> None:
    driver = SHT25Driver("Test", 2, 0x77, simulate=True)
    driver.reset()
