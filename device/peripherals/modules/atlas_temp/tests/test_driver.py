# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.atlas_temp.driver import AtlasTempDriver


def test_init() -> None:
    driver = AtlasTempDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=True,
    )


def test_read_temperature() -> None:
    driver = AtlasTempDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=True,
    )
    temperature = driver.read_temperature()
    assert temperature == 22.97
