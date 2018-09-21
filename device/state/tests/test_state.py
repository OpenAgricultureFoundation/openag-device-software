# Import standard python libraries
import os, sys, pytest, threading

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device state
from device.state.main import State


def test_state():
    """State is pretty simple, so just make sure it has empty dicts."""
    s = State()
    assert list(s.device.keys()) == []
    assert list(s.environment.keys()) == []
    assert list(s.recipe.keys()) == []
    assert list(s.peripherals.keys()) == []
    assert list(s.controllers.keys()) == []
