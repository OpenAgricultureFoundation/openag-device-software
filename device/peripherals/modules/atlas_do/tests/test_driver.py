# Import standard python libraries
import os, sys, pytest

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import mux simulator
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.atlas_do.driver import AtlasDODriver


def test_init() -> None:
    driver = AtlasDODriver(
        name="Test", bus=2, address=0x77, simulate=True, mux_simulator=True
    )
