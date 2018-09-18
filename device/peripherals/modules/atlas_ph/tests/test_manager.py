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
from device.state import State

# Import simulators
from device.communication.i2c.mux_simulator import MuxSimulator

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
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_initialize() -> None:
    manager = AtlasPHManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()


def test_setup() -> None:
    manager = AtlasPHManager(
        name="Test",
        i2c_lock=threading.RLock(),
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
        i2c_lock=threading.RLock(),
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
        i2c_lock=threading.RLock(),
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
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.shutdown()


def test_calibrate_low() -> None:
    manager = AtlasPHManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    request = {"type": "Low Point Calibration", "value": "4.0"}
    manager.process_event(request)
    assert manager.response["status"] == 200


def test_calibrate_mid() -> None:
    manager = AtlasPHManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    request = {"type": "Mid Point Calibration", "value": "7.0"}
    manager.process_event(request)
    assert manager.response["status"] == 200


def test_calibrate_high() -> None:
    manager = AtlasPHManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    request = {"type": "High Point Calibration", "value": "10.0"}
    manager.process_event(request)
    assert manager.response["status"] == 200


def test_clear_calibration() -> None:
    manager = AtlasPHManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    request = {"type": "Clear Calibration"}
    manager.process_event(request)
    assert manager.response["status"] == 200
