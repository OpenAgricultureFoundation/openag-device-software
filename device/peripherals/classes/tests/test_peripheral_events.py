# Import standard python libraries
import sys, os

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    """
    Jake TODO, no PeripheralEventMixin class
    from device.peripherals.classes.peripheral_events import PeripheralEventMixin
    """
except:
    # ... if running tests from same dir as events.py
    sys.path.append("../../../")
    """
    Jake TODO, no PeripheralEventMixin class
    from device.peripherals.classes.peripheral_events import PeripheralEventMixin
    """

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.modes import Modes

# Import peripheral manager
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import shared memory
from device.state import State

"""
TODO Jake, is this needed?
# Set directory for file upload 
os.chdir("../../../")
"""

config = {
    "name": "Test-1",
    "type": "TestPeripheralManager",
    "uuid": "aaa-bbb-ccc",
    "parameters": {
        "setup": {"name": "Test Setup", "file_name": "classes/tests/test_setup"},
        "variables": {"sensor": None, "actuator": None},
        "communication": None,
    },
}

state = State()


"""
Jake TODO, no PeripheralEventMixin class
class PeripheralManagerExample(PeripheralManager, PeripheralEventMixin):
    ...
"""


class PeripheralManagerExample(PeripheralManager):

    def process_event(self, request):
        pass


def test_init():
    manager = PeripheralManagerExample("Test", state, config, simulate=True)


"""
Jake TODO, no event processing in base class!
def test_reset():
    manager = PeripheralManagerExample("Test", state, config, simulate = True)
    manager.process_event(
        request = {"type": "Reset"}
    )
    assert manager.mode == Modes.RESET
    assert manager.response["status"] == 200


def test_shutdown():
    manager = PeripheralManagerExample("Test", state, config, simulate = True)
    manager.process_event(
        request = {"type": "Shutdown"}
    )
    assert manager.mode == Modes.SHUTDOWN
    assert manager.response["status"] == 200


def test_set_sampling_interval():
    manager = PeripheralManagerExample("Test", state, config, simulate = True)
    manager.process_event(
      request = {"type": "Set Sampling Interval", "value": 5}
    )
    assert manager.sampling_interval_seconds == 5
    assert manager.response["status"] == 200


def test_enable_calibration_mode():
    manager = PeripheralManagerExample("Test", state, config, simulate = True)
    manager.process_event(
        request = {"type": "Enable Calibration Mode"}
    )
    assert manager.mode == Modes.CALIBRATE
    assert manager.response["status"] == 200


def test_enable_manual_mode():
    manager = PeripheralManagerExample("Test", state, config, simulate = True)
    manager.process_event(
        request = {"type": "Enable Manual Mode"}
    )
    assert manager.mode == Modes.MANUAL
    assert manager.response["status"] == 200


def test_unknown_event():
    manager = PeripheralManagerExample("Test", state, config, simulate = True)
    manager.process_event(
        request = {"type": "Junk Event Name"}
    )
    assert manager.response["status"] == 400
"""
