# Import standard python libraries
import sys, os

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.classes.peripheral_manager import PeripheralManager
except:
    # ... if running tests from same dir as events.py
    sys.path.append("../../../")
    from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.modes import Modes

# Import shared memory
from device.state import State

# Set directory for file upload 
os.chdir("../../../")

config = {
    "name": "Test-1",
    "type": "TestPeripheralManager",
    "uuid": "aaa-bbb-ccc",
    "parameters": {
       "setup": {
            "name": "Test Setup",
            "file_name": "classes/tests/test_setup"
        },
        "variables": {
            "sensor": None,
            "actuator": None
        },
        "communication": None
    }
}

state = State()


def test_init():
	peripheral_manager = PeripheralManager(
		name = "Test",
		state = state,
		config = config,
		simulate = True,
	)


def test_run_init_mode():
	peripheral_manager = PeripheralManager("Test", state, config, simulate = True)
	peripheral_manager.run_init_mode()
	assert peripheral_manager.mode == Modes.SETUP


def test_run_setup_mode():
	peripheral_manager = PeripheralManager("Test", state, config, simulate = True)
	peripheral_manager.run_setup_mode()
	assert peripheral_manager.mode == Modes.NORMAL


def test_run_reset_mode():
	peripheral_manager = PeripheralManager("Test", state, config, simulate = True)
	peripheral_manager.run_reset_mode()
	assert peripheral_manager.mode == Modes.INIT


# TODO: Test other modes
