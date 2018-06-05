# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ec.manager import AtlasEC
except:
    # ... if running tests from same dir as manger.py
    os.chdir("../../../../")
    from device.peripherals.modules.atlas_ec.manager import AtlasEC

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config
    
# Import shared memory
from device.state import State

# Import test config
device_config = json.load(open("device/peripherals/modules/atlas_ec/tests/config.json"))
peripheral_config = get_peripheral_config(device_config["peripherals"], "AtlasEC-1")

# Initialize state
state = State()


def test_init():
    manager = AtlasEC(
        name = "Test",
        state = state,
        config = peripheral_config,
        simulate = True,
    )


def test_initialize():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.initialize()
    assert True


def test_setup():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.setup()
    assert True


def test_update():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.update()
    assert True


def test_reset():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.reset()
    assert True


def test_shutdown():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.shutdown()
    assert True
