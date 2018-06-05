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


def test_dry_calibration():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Dry Calibration"}
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_single_point_calibration():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Single Point Calibration", "value": 7.0},
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_low_point_calibration():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Low Point Calibration", "value": 4.0}

    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_high_point_calibration():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "High Point Calibration", "value": 10.0},
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500


def test_clear_calibration():
    manager = AtlasEC("Test", state, peripheral_config, simulate = True)
    manager.mode = Modes.CALIBRATE
    manager.process_event(
        request = {"type": "Clear Calibration"}
    )
    assert manager.mode == Modes.ERROR
    assert manager.response["status"] == 500
