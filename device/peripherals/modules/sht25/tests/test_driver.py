# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.sht25.driver import SHT25Driver


def test_init() -> None:
    driver = SHT25Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_read_temperature() -> None:
    driver = SHT25Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )

    temperature = driver.read_temperature()
    assert temperature == 24.0


def test_read_humidity() -> None:
    driver = SHT25Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    humidity = driver.read_humidity()
    assert humidity == 70.0


def test_read_user_register() -> None:
    driver = SHT25Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    user_register = driver.read_user_register()
    assert user_register.end_of_battery == False
    assert user_register.heater_enabled == False
    assert user_register.reload_disabled == False


def test_reset() -> None:
    driver = SHT25Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.reset()
