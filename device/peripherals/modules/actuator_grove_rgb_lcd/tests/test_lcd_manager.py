# To run a single test:
# source ~/openag-device-software/venv/bin/activate
# pytest -s -k "test_init" test_lcd_manager.py


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
from device.peripherals.modules.actuator_grove_rgb_lcd.manager import (
    ActuatorGroveRGBLCDManager,
)

# Load test config
PERIPHERAL_NAME = "LCD"
CONFIG_PATH = (
    ROOT_DIR + "/device/peripherals/modules/actuator_grove_rgb_lcd/tests/config.json"
)
device_config = json.load(open(CONFIG_PATH))
peripheral_config = accessors.get_peripheral_config(
    device_config["peripherals"], PERIPHERAL_NAME
)


def test_init() -> None:
    manager = ActuatorGroveRGBLCDManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_peripheral_initialize() -> None:
    manager = ActuatorGroveRGBLCDManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()


def test_peripheral_setup() -> None:
    manager = ActuatorGroveRGBLCDManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.setup_peripheral()


def test_peripheral_update() -> None:
    manager = ActuatorGroveRGBLCDManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.update_peripheral()


def test_peripheral_reset() -> None:
    manager = ActuatorGroveRGBLCDManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.reset_peripheral()


def test_peripheral_shutdown() -> None:
    manager = ActuatorGroveRGBLCDManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.shutdown_peripheral()
