# Import standard python libraries
import os, sys, pytest, logging, time

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device utilities
from device.utilities.state.main import State

# Import manager elements
from device.upgrade import manager, events, modes


def test_init() -> None:
    state = State()
    upgrade = manager.UpgradeManager(State())
