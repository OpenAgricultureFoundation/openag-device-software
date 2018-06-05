import pytest
from device.state import State

def test_state():
    # state is pretty simple, so just make sure it has empty dicts
    s = State()
    assert list( s.device.keys() ) == []
    assert list( s.environment.keys() ) == []
    assert list( s.recipe.keys() ) == []
    assert list( s.peripherals.keys() ) == []
    assert list( s.controllers.keys() ) == []

