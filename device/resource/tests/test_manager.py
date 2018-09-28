# Import standard python libraries
import os, sys, pytest, logging, time

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device utilities
from device.state.main import State
from device.utilities.statemachine import modes, events

# Import device managers
from device.iot.manager import IoTManager
from device.recipe.manager import RecipeManager

# Import manager elements
from device.resource.manager import ResourceManager


def test_init() -> None:
    state = State()
    manager = ResourceManager(state, IoTManager(state, RecipeManager(state)))
