# To run just this test:
#   source ~/openag-device-software/venv/bin/activate
#   python -m pytest -s test_manager.py
#
# To just run a single test:
#   python -m pytest -s -k test_update_controller_positive test_manager.py

# Import standard python libraries
import os, sys, json, pytest

# Set system path and directory
ROOT_DIR = str(os.getenv("PROJECT_ROOT", "."))
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import device utilities
from device.utilities import accessors
from device.utilities.state.main import State

# Import manager
from device.controllers.modules.pid.manager import PIDControllerManager


# Load test config
CONFIG_PATH = ROOT_DIR + "/device/controllers/modules/pid/tests/config.json"
test_config = json.load(open(CONFIG_PATH))
controller_config = accessors.get_controller_config(
    test_config["controllers"], "TemperatureController"
)


def test_init() -> None:
    manager = PIDControllerManager(
        name="test_init", state=State(), config=controller_config
    )


def test_initialize_controller() -> None:
    manager = PIDControllerManager(
        name="test_initialize_controller", state=State(), config=controller_config
    )
    manager.initialize_controller()


def test_update_controller_no_sensor_values() -> None:
    manager = PIDControllerManager(
        name="test_update_controller_no_sensor_values",
        state=State(),
        config=controller_config,
    )
    manager.initialize_controller()
    manager.update_controller()


def test_update_controller_positive() -> None:
    manager = PIDControllerManager(
        name="test_update_controller_positive", state=State(), config=controller_config
    )
    manager.initialize_controller()
    sensor_name = controller_config["parameters"]["variables"]["sensor_name"]

    # Set reported value just below desired threshold
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 21.9)
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 100.0
    assert manager.desired_negative_actuator_percent == 0.0

    # Set reported value just below desired setpoint, should be no actuation
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 23.9)
    manager.update_controller()
    manager.update_controller()  # call twice because PID needs to settle out for small vals
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 0.0

    # Set reported value just above desired setpoint, should be no actuation
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 24.1)
    manager.update_controller()
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 0.0


def test_update_controller_negative() -> None:
    manager = PIDControllerManager(
        name="test_update_controller_negative", state=State(), config=controller_config
    )
    manager.initialize_controller()
    sensor_name = controller_config["parameters"]["variables"]["sensor_name"]

    # Set reported value just above desired threshold
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 26.1)
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 100.0

    # Set reported value just above desired setpoint
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 24.1)
    manager.update_controller()
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 0.0

    # Set reported value just below desired setpoint
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 23.9)
    manager.update_controller()
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 0.0


def test_reset_controller() -> None:
    manager = PIDControllerManager(
        name="test_reset_controller", state=State(), config=controller_config
    )
    manager.initialize_controller()
    manager.reset_controller()


def test_shutdown_controller() -> None:
    manager = PIDControllerManager(
        name="test_shutdown_controller", state=State(), config=controller_config
    )
    manager.initialize_controller()
    manager.shutdown_controller()
