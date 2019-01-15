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
from device.peripherals.modules.atlas_co2.manager import AtlasCo2Manager

# Load test config
CONFIG_PATH = ROOT_DIR + "/device/peripherals/modules/atlas_co2/tests/config.json"
device_config = json.load(open(CONFIG_PATH))
peripheral_config = accessors.get_peripheral_config(
    device_config["peripherals"], "AtlasCo2-Top"
)


def test_init() -> None:
    manager = AtlasCo2Manager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
