# Import standard python libraries
import os, sys, pytest, json, threading

# Set system path
root_dir = os.environ["PROJECT_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.led_dac5578.driver import LEDDAC5578Driver

# Load test config and setup
base_path = root_dir + "/device/peripherals/modules/led_dac5578/tests/"
device_config = json.load(open(base_path + "config.json"))
peripheral_config = get_peripheral_config(device_config["peripherals"], "LEDPanel-1")
panel_configs = peripheral_config["parameters"]["communication"]["panels"]
peripheral_setup = json.load(open(base_path + "setup.json"))
panel_properties = peripheral_setup["properties"]


def test_init() -> None:
    driver = LEDDAC5578Driver(
        name="Test",
        panel_configs=panel_configs,
        panel_properties=panel_properties,
        i2c_lock=threading.RLock(),
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_turn_on() -> None:
    driver = LEDDAC5578Driver(
        name="Test",
        panel_configs=panel_configs,
        panel_properties=panel_properties,
        i2c_lock=threading.RLock(),
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.turn_on()


def test_turn_off() -> None:
    driver = LEDDAC5578Driver(
        name="Test",
        panel_configs=panel_configs,
        panel_properties=panel_properties,
        i2c_lock=threading.RLock(),
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.turn_off()


def test_set_spd() -> None:
    driver = LEDDAC5578Driver(
        name="Test",
        panel_configs=panel_configs,
        panel_properties=panel_properties,
        i2c_lock=threading.RLock(),
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    distance = 10
    ppfd = 800
    spectrum = {
        "380-399": 0,
        "400-499": 26,
        "500-599": 22,
        "600-700": 39,
        "701-780": 13,
    }
    driver.set_spd(distance, ppfd, spectrum)
