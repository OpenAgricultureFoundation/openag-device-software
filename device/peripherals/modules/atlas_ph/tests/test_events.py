# Import standard python modules
import pytest, sys, os, json, time

# Import python types
from typing import List

# Set system path
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config

# Import device state
from device.state import State

# Import device comms
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import peripheral modules
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


def test_calibrate_low() -> None:
    manager = AtlasPHManager(
        name="Test",
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
