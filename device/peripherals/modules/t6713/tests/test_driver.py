# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.t6713.driver import T6713Driver


def test_init() -> None:
    driver = T6713Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_read_co2() -> None:
    driver = T6713Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    co2 = driver.read_co2()
    assert co2 == 546.0


def test_read_status() -> None:
    driver = T6713Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    status = driver.read_status()
    assert status.error_condition == False
    assert status.flash_error == False
    assert status.calibration_error == False
    assert status.rs232 == False
    assert status.rs485 == False
    assert status.i2c == False
    assert status.warm_up_mode == False
    assert status.single_point_calibration == False


def test_enable_abc_logic() -> None:
    driver = T6713Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.enable_abc_logic()


def test_disable_abc_logic() -> None:
    driver = T6713Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.disable_abc_logic()
