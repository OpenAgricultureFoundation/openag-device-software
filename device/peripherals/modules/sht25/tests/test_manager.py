# Import standard python libraries
import os, sys, json, threading

# Set system path and directory
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.accessors import get_peripheral_config
from device.utilities.modes import Modes

# Import device state
from device.state.main import State

# Import simulators
from device.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral manager
from device.peripherals.modules.sht25.manager import SHT25Manager

# Load test config
path = root_dir + "/device/peripherals/modules/sht25/tests/config.json"
device_config = json.load(open(path))
peripheral_config = get_peripheral_config(device_config["peripherals"], "SHT25-Top")


def test_init() -> None:
    manager = SHT25Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_initialize_peripheral() -> None:
    manager = SHT25Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()


def test_setup_peripheral() -> None:
    manager = SHT25Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.setup_peripheral()


def test_update_peripheral() -> None:
    manager = SHT25Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.update_peripheral()


def test_reset_peripheral() -> None:
    manager = SHT25Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.reset_peripheral()


def test_shutdown_peripheral() -> None:
    manager = SHT25Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.shutdown_peripheral()
