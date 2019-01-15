# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.ccs811.driver import CCS811Driver


def test_init() -> None:
    driver = CCS811Driver(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x77,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


# def test_read_algorithm_data() -> None:
#     driver = CCS811Driver("Test", 2, 0x77, simulate=True, mux_simulator=MuxSimulator())
#     co2, tvoc = driver.read_algorithm_data()
#     assert co2 == 404
