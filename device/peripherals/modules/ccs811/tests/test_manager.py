# Import standard python libraries
import os, sys, json, threading, pytest

# Set system path and directory
ROOT_DIR = os.environ["PROJECT_ROOT"]
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import device utilities
from device.utilities.accessors import get_peripheral_config
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.state.main import State

# Import peripheral manager
from device.peripherals.modules.ccs811.manager import CCS811Manager

# Load test config
CONFIG_PATH = ROOT_DIR + "/device/peripherals/modules/ccs811/tests/config.json"
device_config = json.load(open(CONFIG_PATH))
peripheral_config = get_peripheral_config(device_config["peripherals"], "CCS811-Top")


def test_init() -> None:
    manager = CCS811Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


# def test_initialize_peripheral() -> None:
#     manager = CCS811Manager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()


# def test_setup_peripheral() -> None:
#     manager = CCS811Manager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()
#     manager.setup_peripheral()


# def test_update_peripheral() -> None:
#     manager = CCS811Manager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()
#     manager.update_peripheral()
