# Import standard python libraries
import os, sys, json, threading

# Set system path and directory
ROOT_DIR = os.environ["PROJECT_ROOT"]
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import device utilities
from device.utilities import accessors
from device.utilities.state.main import State
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import manager elements
from device.peripherals.classes.peripheral import modes
from device.peripherals.modules.atlas_temp.manager import AtlasTempManager
from device.peripherals.modules.atlas_temp import events

# Load test config
path = ROOT_DIR + "/device/peripherals/modules/atlas_temp/tests/config.json"
device_config = json.load(open(path))
peripheral_config = accessors.get_peripheral_config(
    device_config["peripherals"], "AtlasTemp-Reservoir"
)


def test_init() -> None:
    manager = AtlasTempManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


# def test_initialize_peripheral() -> None:
#     manager = AtlasTempManager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()


# def test_setup() -> None:
#     manager = AtlasTempManager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()
#     manager.setup()


# def test_update_peripheral() -> None:
#     manager = AtlasTempManager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()
#     manager.update_peripheral()


# def test_reset_peripheral() -> None:
#     manager = AtlasTempManager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()
#     manager.reset_peripheral()


# def test_shutdown_peripheral() -> None:
#     manager = AtlasTempManager(
#         name="Test",
#         state=State(),
#         config=peripheral_config,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     manager.initialize_peripheral()
#     manager.shutdown_peripheral()
