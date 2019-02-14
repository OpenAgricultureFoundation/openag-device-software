# Import standard python libraries
import os, sys, json, threading, pytest

# Set system path and directory
ROOT_DIR = str(os.getenv("PROJECT_ROOT", "."))
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import device utilities
from device.utilities import accessors
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.state.main import State

# Import peripheral manager
from device.peripherals.modules.actuator_pcf8574.manager import ActuatorPCF8574Manager

# Load test config
CONFIG_PATH = (
    ROOT_DIR + "/device/peripherals/modules/actuator_pcf8574/tests/config.json"
)
device_config = json.load(open(CONFIG_PATH))
peripheral_config = accessors.get_peripheral_config(
    device_config["peripherals"], "HeaterPTC300"
)


def test_init() -> None:
    manager = ActuatorPCF8574Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_initialize_peripheral() -> None:
    manager = ActuatorPCF8574Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()


def test_setup_peripheral() -> None:
    manager = ActuatorPCF8574Manager(
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
    manager = ActuatorPCF8574Manager(
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
    manager = ActuatorPCF8574Manager(
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
    manager = ActuatorPCF8574Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.shutdown_peripheral()
