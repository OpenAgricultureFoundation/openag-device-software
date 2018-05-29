# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.led_dac5578.manager import LEDManager
except:
    # ... if running tests from same dir as panel.py
    sys.path.append("../../../")
    from device.peripherals.led_dac5578.manager import LEDManager
    
# Import shared memory
from device.state import State

# Change directory for importing files
os.chdir("../../../")

# Import test config
config = json.load(open("device/peripherals/led_dac5578/tests/test_config.json"))

# Set testing variable values
desired_distance_cm = 5
desired_intensity_watts = 100
desired_spectrum_nm_percent = {
    "400-449": 10,
    "449-499": 10,
    "500-549": 30, 
    "550-559": 30,
    "600-649": 10,
    "650-699": 10}

# Initialize state
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
