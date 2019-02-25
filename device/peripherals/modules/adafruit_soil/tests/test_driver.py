# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.adafruit_soil.driver import AdafruitSoilDriver


def test_init() -> None:
    driver = AdafruitSoilDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_read_temperature() -> None:
    driver = AdafruitSoilDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )

    temperature = driver.read_temperature()
    assert temperature == 24.0


def test_read_moisture() -> None:
    driver = AdafruitSoilDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    humidity = driver.read_moisture()
    assert humidity == 1000


def test_read_hardware_id() -> None:
    driver = AdafruitSoilDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    hardware_id = driver.read_hardware_id()
    assert hardware_id == 4026


def test_reset() -> None:
    driver = AdafruitSoilDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.reset()
