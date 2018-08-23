# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import peripheral driver
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver


def test_init() -> None:
    driver = AtlasPHDriver(name="Test", bus=2, address=0x77, simulate=True)


def test_read_ph() -> None:
    driver = AtlasPHDriver("Test", 2, 0x77, simulate=True)
    ph = driver.read_ph()
    assert ph == 4.001
