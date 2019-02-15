# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.atlas_ec.driver import AtlasECDriver
from device.peripherals.modules.atlas_ec.exceptions import (
    TakeSinglePointCalibrationError,
)


def test_init() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_read_ec() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    ec = driver.read_ec()
    assert ec == 0.0


def test_enable_ec_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.enable_ec_output()


def test_disable_ec_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.enable_ec_output()


def test_enable_tds_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.enable_tds_output()


def test_disable_tds_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.disable_tds_output()


def test_enable_salinity_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.enable_salinity_output()


def test_disable_salinity_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.disable_salinity_output()


def test_enable_specific_gravity_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.enable_specific_gravity_output()


def test_disable_specific_gravity_output() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.disable_specific_gravity_output()


def test_set_probe_type() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.set_probe_type(1.0)


def test_calibrate_dry() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.calibrate_dry()


def test_calibrate_single() -> None:
    driver = AtlasECDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    with pytest.raises(TakeSinglePointCalibrationError):
        driver.calibrate_single(1.413)
