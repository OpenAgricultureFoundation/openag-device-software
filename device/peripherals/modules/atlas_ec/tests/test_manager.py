# Import standard python libraries
import os, sys, json, threading, logging

# Set system path and directory
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.accessors import get_peripheral_config
from device.utilities.modes import Modes

# Import device state
from device.state.main import State

# Import simulators
from device.communication.i2c.mux_simulator import MuxSimulator
from device.peripherals.modules.atlas_ec.simulator import AtlasECSimulator

# Import peripheral manager
from device.peripherals.modules.atlas_ec.manager import AtlasECManager

# Load test config
path = root_dir + "/device/peripherals/modules/atlas_ec/tests/config.json"
device_config = json.load(open(path))
peripheral_config = get_peripheral_config(
    device_config["peripherals"], "AtlasEC-Reservoir"
)

# Initialize logger
logging.basicConfig(level=logging.DEBUG)


def test_init() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_initialize() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()


def test_setup() -> None:
    manager = AtlasECManager(
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
    manager = AtlasECManager(
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
    manager = AtlasECManager(
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
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.shutdown()


def test_calibrate_dry() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    message, status = manager.events.create(request={"type": "Dry Calibration"})
    assert status == 200
    manager.events.check()


def test_calibrate_single() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    message, status = manager.events.create(
        request={"type": "Single Point Calibration", "value": 7.0}
    )
    assert status == 200
    manager.events.check()


def test_calibrate_low() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    message, status = manager.events.create(
        request={"type": "Low Point Calibration", "value": 4.0}
    )
    assert status == 200
    manager.events.check()


def test_calibrate_high() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    message, status = manager.events.create(
        request={"type": "High Point Calibration", "value": 10.0}
    )
    assert status == 200
    manager.events.check()


def test_clear_calibrations() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize()
    manager.mode = Modes.CALIBRATE
    message, status = manager.events.create(request={"type": "Clear Calibration"})
    assert status == 200
    manager.events.check()
