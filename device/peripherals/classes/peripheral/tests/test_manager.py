# Import standard python modules
import sys, os, pytest, json, threading

# Set system path and directory
root_dir = os.environ["PROJECT_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config
from device.utilities.state.main import State

# Import manager elements
from device.peripherals.classes.peripheral.manager import PeripheralManager
from device.peripherals.classes.peripheral import modes, events

# Load test config
path = root_dir + "/device/peripherals/classes/peripheral/tests/config.json"
device_config = json.load(open(path))
peripheral_config = get_peripheral_config(device_config["peripherals"], "Camera-Top")


def test_init() -> None:
    manager = PeripheralManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )


def test_run_init_mode() -> None:
    manager = PeripheralManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )
    manager.run_init_mode()
    assert manager.mode == modes.SETUP


def test_run_setup_mode() -> None:
    manager = PeripheralManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )
    manager.mode = modes.SETUP
    manager.run_setup_mode()
    assert manager.mode == modes.NORMAL


def test_run_reset_mode() -> None:
    manager = PeripheralManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )
    manager.run_reset_mode()
    assert manager.mode == modes.INIT


##### EVENT TEST FUNCTIONS #############################################################


def test_set_sampling_interval() -> None:
    manager = PeripheralManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        i2c_lock=threading.RLock(),
        simulate=True,
    )
    assert manager.sampling_interval == 5  # default to 5 seconds
    manager.create_event({"type": events.SET_SAMPLING_INTERVAL, "value": 33})
    manager.check_events()
    assert manager.sampling_interval == 33
