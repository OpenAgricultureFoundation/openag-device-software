# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.t6713.manager import T6713
except:
    # ... if running tests from same dir as manager.py
    os.chdir("../../../../")
    from device.peripherals.modules.t6713.manager import T6713

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config
    
# Import shared memory
from device.state import State

# Import test config
device_config = json.load(open("device/peripherals/modules/t6713/tests/config.json"))
peripheral_config = get_peripheral_config(device_config["peripherals"], "T6713-1")

# Initialize state
state = State()


def test_init():
    manager = T6713(
        name = "Test",
        state = state,
        config = peripheral_config,
        simulate = True,
    )


def test_initialize():
    manager = T6713("Test", state, peripheral_config, simulate = True)
    manager.initialize()
    assert True


def test_setup():
    manager = T6713("Test", state, peripheral_config, simulate = True)
    manager.setup()
    assert True


def test_update():
    manager = T6713("Test", state, peripheral_config, simulate = True)
    manager.update()
    assert True


def test_reset():
    manager = T6713("Test", state, peripheral_config, simulate = True)
    manager.reset()
    assert True


def test_shutdown():
    manager = T6713("Test", state, peripheral_config, simulate = True)
    manager.shutdown()
    assert True
