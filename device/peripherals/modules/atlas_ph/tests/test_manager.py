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
from device.peripherals.modules.atlas_ph.manager import AtlasPHManager
from device.peripherals.modules.atlas_ph import events

# Load test config
CONFIG_PATH = ROOT_DIR + "/device/peripherals/modules/atlas_ph/tests/config.json"
device_config = json.load(open(CONFIG_PATH))
peripheral_config = accessors.get_peripheral_config(
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


def test_initialize_peripheral() -> None:
    manager = AtlasPHManager(
        name="Test",
        i2c_lock=threading.RLock(),
        state=State(),
        config=peripheral_config,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    manager.initialize_peripheral()


def test_setup_peripheral() -> None:
    manager = AtlasPHManager(
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
    manager = AtlasPHManager(
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
    manager = AtlasPHManager(
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
    manager = AtlasPHManager(
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


def test_calibrate_low() -> None:
    manager = AtlasPHManager(
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
        request={"type": events.CALIBRATE_LOW, "value": "4.0"}
    )
    assert status == 200
    manager.check_events()


def test_calibrate_mid() -> None:
    manager = AtlasPHManager(
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
        request={"type": events.CALIBRATE_MID, "value": "7.0"}
    )
    assert status == 200
    manager.check_events()


def test_calibrate_high() -> None:
    manager = AtlasPHManager(
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
        request={"type": events.CALIBRATE_HIGH, "value": "10.0"}
    )
    assert status == 200
    manager.check_events()


def test_clear_calibration() -> None:
    manager = AtlasPHManager(
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
