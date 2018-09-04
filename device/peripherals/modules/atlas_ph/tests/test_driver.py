# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import mux simulator
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver


def test_init() -> None:
    driver = AtlasPHDriver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=True,
    )


def test_read_ph() -> None:
    driver = AtlasPHDriver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=True,
    )
    ph = driver.read_ph()
    assert ph == 4.001
