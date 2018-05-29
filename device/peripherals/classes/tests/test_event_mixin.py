# Import standard python libraries
import sys, os

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.classes.event_mixin import PeripheralEventMixin
except:
    # ... if running tests from same dir as events.py
    sys.path.append("../../../")
    from device.peripherals.classes.event_mixin import PeripheralEventMixin

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.modes import Modes

# Import peripheral manager
from device.peripherals.classes.manager import PeripheralManager

# Import shared memory
from device.state import State

# Set directory for file upload 
os.chdir("../../../")

config = {
    "name": "Test-1",
    "type": "TestPeripheralManager",
    "uuid": "aaa-bbb-ccc",
    "parameters": {
       "setup": {
            "name": "Test Setup",
            "file_name": "classes/tests/test_setup"
        },
        "variables": {
            "sensor": None,
            "actuator": None
        },
        "communication": None
    }
}

state = State()


class PeripheralManagerExample(PeripheralManager, PeripheralEventMixin):
    ...


def test_init():
    peripheral_manager = PeripheralManagerExample("Test", state, config, simulate = True)


def test_reset():
    peripheral_manager = PeripheralManagerExample("Test", state, config, simulate = True)
    peripheral_manager.process_event(
        request = {"type": "Reset"}
    )
    assert peripheral_manager.mode == Modes.RESET
    assert peripheral_manager.response["status"] == 200


def test_shutdown():
    peripheral_manager = PeripheralManagerExample("Test", state, config, simulate = True)
    peripheral_manager.process_event(
        request = {"type": "Shutdown"}
    )
    assert peripheral_manager.mode == Modes.SHUTDOWN
    assert peripheral_manager.response["status"] == 200


def test_set_sampling_interval():
    peripheral_manager = PeripheralManagerExample("Test", state, config, simulate = True)
    peripheral_manager.process_event(
      request = {"type": "Set Sampling Interval", "value": 5}
    )
    assert peripheral_manager.sampling_interval_seconds == 5
    assert peripheral_manager.response["status"] == 200


def test_enable_calibration_mode():
    peripheral_manager = PeripheralManagerExample("Test", state, config, simulate = True)
    peripheral_manager.process_event(
        request = {"type": "Enable Calibration Mode"}
    )
    assert peripheral_manager.mode == Modes.CALIBRATE
    assert peripheral_manager.response["status"] == 200


def test_enable_manual_mode():
    peripheral_manager = PeripheralManagerExample("Test", state, config, simulate = True)
    peripheral_manager.process_event(
        request = {"type": "Enable Manual Mode"}
    )
    assert peripheral_manager.mode == Modes.MANUAL
    assert peripheral_manager.response["status"] == 200


def test_unknown_event():
    peripheral_manager = PeripheralManagerExample("Test", state, config, simulate = True)
    peripheral_manager.process_event(
        request = {"type": "Junk Event Name"}
    )
    assert peripheral_manager.response["status"] == 400
