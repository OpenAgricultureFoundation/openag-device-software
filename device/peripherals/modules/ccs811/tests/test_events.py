# Import standard python libraries
import sys, os, json

# Get current working directory
cwd = os.getcwd()
print("Running test from: {}".format(cwd))

# Set correct import path
if cwd.endswith("sht25"):
    print("Running test locally")
    os.chdir("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running test globally")
else:
    print("Running test from invalid location")
    sys.exit(0)

# Import manager
from device.peripherals.modules.sht25.manager import SHT25Manager

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config
    
# Import shared memory
from device.state import State

# Import test config
device_config = json.load(open("device/peripherals/modules/sht25/tests/config.json"))
peripheral_config = get_peripheral_config(device_config["peripherals"], "SHT25-Top")

# Initialize state
state = State()


def test_init():
    manager = SHT25Manager(
        name = "Test",
        state = state,
        config = peripheral_config,
        simulate = True,
    )