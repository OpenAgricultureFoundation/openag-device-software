# Import standard python libraries
import sys, os, json

# Get current working directory
cwd = os.getcwd()
print("Running test from: {}".format(cwd))

# Set correct import path
if cwd.endswith("atlas_ec"):
    print("Running test locally")
    os.chdir("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running test globally")
else:
    print("Running tests from invalid location")
    sys.exit(0)

# Import manager
from device.peripherals.modules.atlas_ec.manager import AtlasECManager

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config
    
# Import shared memory
from device.state import State

# Import test config
device_config = json.load(open("device/peripherals/modules/atlas_ec/tests/config.json"))
peripheral_config = get_peripheral_config(device_config["peripherals"], "AtlasEC-Reservoir")

# Initialize state
state = State()


def test_init():
    manager = AtlasECManager(
        name = "Test",
        state = state,
        config = peripheral_config,
        simulate = True,
    )


def test_initialize():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.initialize()
    assert True


def test_setup():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.setup()
    assert True


def test_update():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.update()
    assert True


def test_reset():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.reset()
    assert True


def test_shutdown():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.shutdown()
    assert True
