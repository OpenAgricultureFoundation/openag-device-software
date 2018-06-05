# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ph.manager import AtlasPH
except:
    # ... if running tests from same dir as manger.py
    sys.path.append("../../../../")
    from device.peripherals.modules.atlas_ph.manager import AtlasPH

# Import device utilities
from device.utilities.modes import Modes
    
# Import shared memory
from device.state import State

# Change directory for importing files
os.chdir("../../../../")

# Import test config
device_config = json.load(open("device/peripherals/modules/atlas_ph/tests/config.json"))
peripheral_config = device_config["peripherals"][0]

# Initialize state
state = State()

def test_init():
    manager = AtlasPH(
        name = "Test",
        state = state,
        config = peripheral_config,
        simulate = True,
    )


def test_initialize():
    manager = AtlasPH("Test", state, peripheral_config, simulate = True)
    manager.initialize()
    assert True


def test_setup():
    manager = AtlasPH("Test", state, peripheral_config, simulate = True)
    manager.setup()
    assert True


def test_update():
    manager = AtlasPH("Test", state, peripheral_config, simulate = True)
    manager.update()
    assert True


def test_reset():
    manager = AtlasPH("Test", state, peripheral_config, simulate = True)
    manager.reset()
    assert True


def test_shutdown():
    manager = AtlasPH("Test", state, peripheral_config, simulate = True)
    manager.shutdown()
    assert True
