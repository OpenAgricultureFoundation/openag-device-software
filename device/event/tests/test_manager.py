# Import standard python libraries
import os, sys, pytest

# Set system path
# sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Set system path and directory
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)
print(os.getcwd())

# Import device state
from device.state.main import State

# Import peripheral driver
from device.event.manager import EventManager


def test_init() -> None:
    manager = EventManager(State())
