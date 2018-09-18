# Import standard python modules
import pytest, sys, os, json, threading

# Import python types
from typing import List

# Set system path
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config

# Import device state
from device.state.main import State

# Import peripheral manager
from device.peripherals.classes.peripheral.manager import PeripheralManager
from device.peripherals.classes.peripheral.events import PeripheralEvents


# Load test config
path = root_dir + "/device/peripherals/classes/peripheral/tests/config.json"
device_config = json.load(open(path))
peripheral_config = get_peripheral_config(device_config["peripherals"], "Camera-Top")

# Create peripheral manager with event mixin
class PM(PeripheralEvents, PeripheralManager):
    ...


def test_init():
    manager = PM(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )


def test_shutdown():
    manager = PM(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )
    manager.process_event(request={"type": "Shutdown"})
    assert manager.mode == Modes.SHUTDOWN
    assert manager.response["status"] == 200


def test_set_sampling_interval():
    manager = PM(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )
    manager.process_event(request={"type": "Set Sampling Interval", "value": 5})
    assert manager.sampling_interval_seconds == 5


def test_unknown_event():
    manager = PM(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )
    manager.process_event(request={"type": "Junk Event Name"})
    assert manager.response["status"] == 400
