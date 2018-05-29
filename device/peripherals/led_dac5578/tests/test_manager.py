# Import standard python libraries
import sys, os

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.led_dac5578.manager import LEDManager
except:
    # ... if running tests from same dir as panel.py
    sys.path.append("../../../")
    from device.peripherals.led_dac5578.manager import LEDManager
    os.chdir("../../../")

# Import shared memory
from device.state import State


config = {
    "name": "LightArray-1",
    "type": "LightArray",
    "uuid": "5596ed62-0cf6-4e58-b774-94fe7d537b91",
    "parameters": {
       "setup": {
            "name": "Test Setup",
            "file_name": "led_dac5578/setups/test"
        },
        "variables": {
            "sensor": {
                "intensity_watts": "light_intensity_watts",
                "spectrum_nm_percent": "light_spectrum_nm_percent",
                "illumination_distance_cm": "light_illumination_distance_cm"
            },
            "actuator": {
                "channel_output_percents": "light_channel_output_percents"
            }
        },
        "communication": {
            "panels": [
                {"name": "Test-1", "bus": 2, "mux": "0x77", "channel": 0, "address": "0x47", "x": 0, "y": 0},
                {"name": "Test-2", "bus": 2, "mux": "0x77", "channel": 1, "address": "0x47", "x": 1, "y": 0},
                {"name": "Test-3", "bus": 2, "mux": "0x77", "channel": 2, "address": "0x47", "x": 2, "y": 0}
            ]
        },

    }
}

desired_distance_cm = 5
desired_intensity_watts = 100
desired_spectrum_nm_percent = {
    "400-449": 10,
    "449-499": 10,
    "500-549": 30, 
    "550-559": 30,
    "600-649": 10,
    "650-699": 10}

state = State()


def test_init():
    array = LEDManager(
        name = "Test",
        state = state,
        config = config,
        simulate = True,
    )


def test_initialize():
    array = LEDManager("Test", state, config, simulate = True)
    array.initialize()


def test_setup():
    array = LEDManager("Test", state, config, simulate = True)
    array.initialize()
    array.setup()


def test_update():
    array = LEDManager("Test", state, config, simulate = True)
    array.initialize()
    array.setup()
    array.update()


def test_shutdown():
    array = LEDManager("Test", state, config, simulate = True)
    array.initialize()
    array.setup()
    array.update()
    array.shutdown()
