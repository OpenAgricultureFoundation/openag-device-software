# Import standard python libraries
import os, sys, pytest, json

# Set system path
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config

# Import device state
from device.state import State

# Import mux simulator
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.led_dac5578.manager import LEDDAC5578Manager

# Load test config and setup
path = root_dir + "/device/peripherals/modules/led_dac5578/tests/config.json"
device_config = json.load(open(path))
peripheral_config = get_peripheral_config(device_config["peripherals"], "LEDPanel-1")

# Set testing variable values
# desired_distance_cm = 5
# desired_ppfd_umol_m2_s = 100
# desired_spectrum_nm_percent = {
#     "400-449": 10,
#     "449-499": 10,
#     "500-549": 30,
#     "550-559": 30,
#     "600-649": 10,
#     "650-699": 10,
# }


def test_init() -> None:
    manager = LEDDAC5578Manager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_initialize() -> None:
    manager = LEDDAC5578Manager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()


def test_setup() -> None:
    manager = LEDDAC5578Manager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.setup()


def test_update() -> None:
    manager = LEDDAC5578Manager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.update()


def test_reset() -> None:
    manager = LEDDAC5578Manager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.reset()


def test_shutdown() -> None:
    manager = LEDDAC5578Manager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.shutdown()
