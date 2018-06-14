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


def test_dry_calibration():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Dry Calibration"}
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_single_point_calibration():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Single Point Calibration", "value": 7.0},
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_low_point_calibration():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Low Point Calibration", "value": 4.0}

    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_high_point_calibration():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "High Point Calibration", "value": 10.0},
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_clear_calibration():
    manager = AtlasECManager("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Clear Calibration"}
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500
