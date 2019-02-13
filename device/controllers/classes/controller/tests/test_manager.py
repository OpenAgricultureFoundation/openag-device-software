# Import standard python modules
import sys, os, pytest, json, threading

# Set system path and directory
root_dir = str(os.getenv("PROJECT_ROOT", "."))
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import accessors
from device.utilities.state.main import State

# Import manager elements
from device.controllers.classes.controller.manager import ControllerManager
from device.controllers.classes.controller import modes

# Load test config
path = root_dir + "/device/controllers/classes/controller/tests/config.json"
device_config = json.load(open(path))
controller_config = accessors.get_controller_config(
    device_config["controllers"], "HeaterController"
)


def test_init() -> None:
    manager = ControllerManager(name="Test", state=State(), config=controller_config)


def test_run_init_mode() -> None:
    manager = ControllerManager(name="Test", state=State(), config=controller_config)
    manager.run_init_mode()
    assert manager.mode == modes.NORMAL


def test_run_reset_mode() -> None:
    manager = ControllerManager(name="Test", state=State(), config=controller_config)
    manager.run_reset_mode()
    assert manager.mode == modes.INIT
