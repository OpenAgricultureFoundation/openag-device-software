# Import standard python libraries
import sys, os, pytest, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import driver elements
from device.peripherals.classes.atlas.driver import AtlasDriver
from device.peripherals.classes.atlas.simulator import AtlasSimulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator


def test_init() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )


def test_read_info() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    info = driver.read_info()
    assert info.sensor_type == "ec"
    assert info.firmware_version == 1.96


def test_read_status() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    status = driver.read_status()
    assert status.prev_restart_reason == "Powered off"
    assert status.voltage == 3.655


def test_enable_protocol_lock() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.enable_protocol_lock()


def test_disable_protocol_lock() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.disable_protocol_lock()


def test_enable_led() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.enable_led()


def test_disable_led() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.disable_led()


def test_enable_sleep_mode() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.enable_sleep_mode()


def test_set_compensation_temperature() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.set_compensation_temperature(26.0)


def test_calibrate_low() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.calibrate_low(4.0)


def test_calibrate_mid() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.calibrate_mid(7.0)


def test_calibrate_high() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.calibrate_high(10.0)


def test_clear_calibrations() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.clear_calibrations()


def test_factory_reset() -> None:
    driver = AtlasDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x64,
        simulate=True,
        mux_simulator=MuxSimulator(),
        Simulator=AtlasSimulator,
    )
    driver.factory_reset()
