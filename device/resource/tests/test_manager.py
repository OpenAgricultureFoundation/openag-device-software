# Import standard python libraries
import os, sys, pytest, logging, time

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import device utilities
from device.utilities.state.main import State
from device.utilities.statemachine import modes, events

# Import device managers
from device.iot.manager import IotManager
from device.recipe.manager import RecipeManager

# Import manager elements
from device.resource.manager import ResourceManager


def test_init() -> None:
    state = State()
    manager = ResourceManager(state, IotManager(state, RecipeManager(state)))
