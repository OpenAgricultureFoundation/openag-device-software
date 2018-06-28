# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.led_dac5578.manager import LEDDAC5578Manager
except:
    # ... if running tests from same dir as events.py
    sys.path.append("../../../../")
    from device.peripherals.modules.led_dac5578.manager import LEDDAC5578Manager

# Import device utilities
from device.utilities.modes import Modes

# Import shared memory
from device.state import State

# Set directory for file upload
os.chdir("../../../../")

# Import test config
device_config = json.load(
    open("device/peripherals/modules/led_dac5578/tests/config.json")
)
peripheral_config = device_config["peripherals"][0]

# Initialize state
state = State()


def test_init():
    led_manager = LEDDAC5578Manager("Test", state, peripheral_config, simulate=True)


def test_turn_on():
    led_manager = LEDDAC5578Manager("Test", state, peripheral_config, simulate=True)

    # Try to turn on outside manual mode
    led_manager.mode = Modes.NORMAL
    led_manager.process_event(request={"type": "Turn On"})
    assert led_manager.response["status"] == 400

    # Turn on from manual mode
    led_manager.mode = Modes.MANUAL
    led_manager.process_event(request={"type": "Turn On"})
    assert led_manager.response["status"] == 200


def test_turn_off():
    led_manager = LEDDAC5578Manager("Test", state, peripheral_config, simulate=True)

    # Try to turn off outside manual mode
    led_manager.mode = Modes.NORMAL
    led_manager.process_event(request={"type": "Turn Off"})
    assert led_manager.response["status"] == 400

    # Turn off from manual mode
    led_manager.mode = Modes.MANUAL
    led_manager.process_event(request={"type": "Turn Off"})
    assert led_manager.response["status"] == 200


def test_calculate_ulrf_from_percents():
    led_manager = LEDDAC5578Manager("Test", state, peripheral_config, simulate=True)

    request = {
        "type": "Calculate ULRF From Percents",
        "value": '{"channel_power_percents": {"WW": 100, "CW": 31.0, "B": 50, "G": 25, "R": 50, "FR": 40}, "illumination_distance_cm": 10}',
    }

    led_manager.process_event(request)
    assert led_manager.response["status"] == 200
    assert led_manager.response["intensity_watts"] == 160.0
    assert led_manager.response["illumination_distance_cm"] == 5.0
    spectrum = {"400-499": 17.5, "500-599": 65.0, "600-699": 17.5}
    assert led_manager.response["spectrum_nm_percents"] == spectrum
