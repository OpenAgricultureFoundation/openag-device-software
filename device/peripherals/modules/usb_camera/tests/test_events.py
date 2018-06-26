# Import standard python libraries
import sys, os, json

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("usb_camera"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import manager
from device.peripherals.modules.usb_camera.manager import USBCameraManager

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config

# Import shared memory
from device.state import State

# Set directory for loading files
if cwd.endswith("usb_camera"):
    os.chdir("../../../../")

# Import test config
device_config = json.load(
    open("device/peripherals/modules/usb_camera/tests/config.json")
)
peripheral_config = get_peripheral_config(device_config["peripherals"], "Camera-1")

# Initialize state
state = State()


def test_init():
    manager = USBCameraManager(
        name="Test", state=state, config=peripheral_config, simulate=True
    )
