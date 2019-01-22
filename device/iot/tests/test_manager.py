# Import standard python libraries
import os, sys, pytest, time

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import device utilities
from device.utilities.state.main import State

# Import device managers
from device.recipe.manager import RecipeManager

# Import manager elements
from device.iot import manager, modes


def test_init() -> None:
    state = State()
    recipe = RecipeManager(state)
    iot = manager.IotManager(state, recipe)
