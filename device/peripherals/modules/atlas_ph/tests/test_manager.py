# Import standard python libraries
import os, sys, json

# Set system path and directory
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import device state
from device.state import State

# Import simulators
from device.comms.i2c2.mux_simulator import MuxSimulator
from device.peripherals.modules.atlas_ph.simulator import AtlasPHSimulator

# Import peripheral manager
from device.peripherals.modules.atlas_ph.manager import AtlasPHManager

# Load test config
path = root_dir + "/device/peripherals/modules/atlas_ph/tests/config.json"
device_config = json.load(open(path))
peripheral_config = get_peripheral_config(
    device_config["peripherals"], "AtlasPH-Reservoir"
)


def test_init() -> None:
    manager = AtlasPHManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_initialize() -> None:
    manager = AtlasPHManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()


def test_setup() -> None:
    manager = AtlasPHManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.setup()


def test_update() -> None:
    manager = AtlasPHManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.update()


def test_reset() -> None:
    manager = AtlasPHManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.reset()


def test_shutdown() -> None:
    manager = AtlasPHManager(
        name="Test",
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.shutdown()


# TODO: Test events
