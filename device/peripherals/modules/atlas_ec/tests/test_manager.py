# Import standard python libraries
import os, sys, json, threading, logging, pytest

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
from device.peripherals.classes.atlas import exceptions
from device.peripherals.modules.atlas_ec.manager import AtlasECManager
from device.peripherals.modules.atlas_ec import events


# Load test config
path = ROOT_DIR + "/device/peripherals/modules/atlas_ec/tests/config.json"
device_config = json.load(open(path))
peripheral_config = accessors.get_peripheral_config(
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


def test_initialize_peripheral() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()


def test_setup_peripheral() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.setup_peripheral()


def test_update_peripheral() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.update_peripheral()


def test_reset_peripheral() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.reset_peripheral()


def test_shutdown_peripheral() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.shutdown_peripheral()


##### EVENT TEST FUNCTIONS #############################################################


def test_calibrate_dry() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.mode = modes.CALIBRATE
    message, status = manager.create_event(request={"type": events.CALIBRATE_DRY})
    assert status == 200
    manager.check_events()


def test_calibrate_single() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.mode = modes.CALIBRATE
    message, status = manager.create_event(
        request={"type": events.CALIBRATE_SINGLE, "value": 7.0}
    )
    assert status == 400
    manager.check_events()


def test_calibrate_low() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.mode = modes.CALIBRATE
    message, status = manager.create_event(
        request={"type": events.CALIBRATE_LOW, "value": 4.0}
    )
    assert status == 200
    manager.check_events()


def test_calibrate_high() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.mode = modes.CALIBRATE
    message, status = manager.create_event(
        request={"type": events.CALIBRATE_HIGH, "value": 10.0}
    )
    assert status == 200
    manager.check_events()


def test_clear_calibrations() -> None:
    manager = AtlasECManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()
    manager.mode = modes.CALIBRATE
    message, status = manager.create_event(request={"type": events.CLEAR_CALIBRATION})
    assert status == 200
    manager.check_events()
