# Import standard python libraries
import os, sys, json, pytest

# Set system path and directory
ROOT_DIR = str(os.getenv("PROJECT_ROOT", "."))
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import device utilities
from device.utilities import accessors
from device.utilities.state.main import State

# Import peripheral manager
from device.controllers.modules.hysteretic.manager import HystereticControllerManager

# Load test config
CONFIG_PATH = ROOT_DIR + "/device/controllers/modules/hysteretic/tests/config.json"
device_config = json.load(open(CONFIG_PATH))
controller_config = accessors.get_controller_config(
    device_config["controllers"], "TemperatureController"
)


def test_init() -> None:
    manager = HystereticControllerManager(
        name="Test", state=State(), config=controller_config
    )


def test_initialize_controller() -> None:
    manager = HystereticControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()


def test_update_controller_no_sensor_values() -> None:
    manager = HystereticControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()
    manager.update_controller()


def test_update_controller_positive() -> None:
    manager = HystereticControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()
    sensor_name = controller_config["parameters"]["variables"]["sensor_name"]

    # Set reported value just below desired threshold
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 21.9)
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 100.0
    assert manager.desired_negative_actuator_percent == 0.0

    # Set reported value just below desired setpoint
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 23.9)
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 100.0
    assert manager.desired_negative_actuator_percent == 0.0

    # Set reported value just above desired setpoint
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 24.1)
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 0.0


def test_update_controller_negative() -> None:
    manager = HystereticControllerManager(
        name="Test", state=State(), config=controller_config
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
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 100.0

    # Set reported value just below desired setpoint
    manager.state.set_environment_desired_sensor_value(sensor_name, 24)
    manager.state.set_environment_reported_sensor_value("SHT25", sensor_name, 23.9)
    manager.update_controller()
    assert manager.desired_positive_actuator_percent == 0.0
    assert manager.desired_negative_actuator_percent == 0.0


def test_reset_controller() -> None:
    manager = HystereticControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()
    manager.reset_controller()


def test_shutdown_controller() -> None:
    manager = HystereticControllerManager(
        name="Test", state=State(), config=controller_config
    )
    manager.initialize_controller()
    manager.shutdown_controller()
