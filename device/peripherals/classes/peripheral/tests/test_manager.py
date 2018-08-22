# Import standard python modules
import sys, os, pytest, json

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

# Import peripheral manager
from device.peripherals.classes.peripheral.manager import PeripheralManager

# Load test config
path = root_dir + "/device/peripherals/classes/peripheral/tests/config.json"
device_config = json.load(open(path))
peripheral_config = get_peripheral_config(device_config["peripherals"], "Camera-Top")


def test_init():
    peripheral_manager = PeripheralManager(
        name="Test", state=State(), config=peripheral_config, simulate=True
    )


def test_run_init_mode():
    peripheral_manager = PeripheralManager(
        name="Test", state=State(), config=peripheral_config, simulate=True
    )
    peripheral_manager.run_init_mode()
    assert peripheral_manager.mode == Modes.SETUP


def test_run_setup_mode():
    peripheral_manager = PeripheralManager(
        name="Test", state=State(), config=peripheral_config, simulate=True
    )
    peripheral_manager.run_setup_mode()
    assert peripheral_manager.mode == Modes.NORMAL


def test_run_reset_mode():
    peripheral_manager = PeripheralManager(
        name="Test", state=State(), config=peripheral_config, simulate=True
    )
    peripheral_manager.run_reset_mode()
    assert peripheral_manager.mode == Modes.INIT
