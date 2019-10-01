# Import standard python libraries
import os, sys, json, pytest

# Set system path and directory
ROOT_DIR = str(os.getenv("PROJECT_ROOT", "."))
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import device utilities
from device.utilities import accessors
from device.utilities.state.main import State

# Import peripheral manager
from device.controllers.modules.water_aeration.manager import WaterAerationControllerManager

# Load test config
CONFIG_PATH = ROOT_DIR + "/device/controllers/modules/water_aeration/tests/config.json"
device_config = json.load(open(CONFIG_PATH))
controller_config = accessors.get_controller_config(
    device_config["controllers"], "WaterAerationController"
)


def test_init() -> None:
    manager = WaterAerationControllerManager(
        name="Test", state=State(), config=controller_config
    )

def test_initialize_controller() -> None:
    manager = WaterAerationControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()

def test_reset_controller() -> None:
    manager = WaterAerationControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()
    manager.reset_controller()

def test_shutdown_controller() -> None:
    manager = WaterAerationControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()
    manager.shutdown_controller()
