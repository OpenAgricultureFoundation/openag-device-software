# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import controller manager parent class
from device.controllers.classes.controller import manager, modes


class HystereticControllerManager(manager.ControllerManager):
    """Manages a controller with hystretic logic."""

    actuation_direction = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.sensor_name = self.variables.get("sensor_name", None)
        self.positive_actuator_name = self.variables.get("positive_actuator_name", None)
        self.negative_actuator_name = self.variables.get("negative_actuator_name", None)
        self.accuracy_value = float(self.properties.get("accuracy_value", None))

    @property
    def sensor_value(self) -> Optional[float]:
        """Gets sensor value."""
        value = self.state.get_environment_reported_sensor_value(self.sensor_name)
        if value != None:
            return float(value)
        return None

    @property
    def desired_sensor_value(self) -> Optional[float]:
        """Gets desired sensor value."""
        value = self.state.get_environment_desired_sensor_value(self.sensor_name)
        if value != None:
            return float(value)
        return None

    @property
    def desired_positive_actuator_percent(self) -> Optional[float]:
        """Gets positive actuator value."""
        value = self.state.get_environment_desired_actuator_value(
            self.positive_actuator_name
        )
        if value != None:
            return float(value)
        return None

    @desired_positive_actuator_percent.setter
    def desired_positive_actuator_percent(self, value: float) -> None:
        """Sets reported output value in shared state."""
        if self.positive_actuator_name == None:
            return
        self.state.set_environment_desired_actuator_value(
            self.positive_actuator_name, value
        )

    @property
    def desired_negative_actuator_percent(self) -> Optional[float]:
        """Gets positive actuator value."""
        value = self.state.get_environment_desired_actuator_value(
            self.negative_actuator_name
        )
        if value != None:
            return float(value)
        return None

    @desired_negative_actuator_percent.setter
    def desired_negative_actuator_percent(self, value: float) -> None:
        """Sets reported output value in shared state."""
        if self.negative_actuator_name == None:
            return
        self.state.set_environment_desired_actuator_value(
            self.negative_actuator_name, value
        )

    def initialize_controller(self) -> None:
        """Initializes controller."""
        self.logger.info("Initializing")
        self.clear_reported_values()

    def update_controller(self) -> None:
        """Updates controller."""

        # Check sensor values are initialized
        if (
            type(self.sensor_value) != float
            or type(self.desired_sensor_value) != float
            or type(self.accuracy_value) != float
        ):
            self.desired_positive_actuator_percent = None
            self.desired_negative_actuator_percent = None
            return

        # Check if actuating positively
        if self.actuation_direction == "+":

            # Check if we have hit the setpoint
            if self.sensor_value >= self.desired_sensor_value:
                self.desired_positive_actuator_percent = 0.0
                self.desired_negative_actuator_percent = 0.0
                self.actuation_direction = None

            # More positive actuation is requried to hit setpoint
            else:
                self.desired_positive_actuator_percent = 100.0
                self.desired_negative_actuator_percent = 0.0

        # Check if actuating negatively
        elif self.actuation_direction == "-":

            # Check if we have hit the setpoint
            if self.sensor_value <= self.desired_sensor_value:
                self.desired_positive_actuator_percent = 0.0
                self.desired_negative_actuator_percent = 0.0
                self.actuation_direction = None

            # More negative actuation is requried to hit setpoint
            else:
                self.desired_positive_actuator_percent = 0.0
                self.desired_negative_actuator_percent = 100.0

        # Check if starting positive actuation
        elif self.sensor_value <= self.desired_sensor_value - self.accuracy_value:
            self.logger.debug("Starting positive actuation")
            self.desired_positive_actuator_percent = 100.0
            self.desired_negative_actuator_percent = 0.0
            self.actuation_direction = "+"

        # Check if starting negative actuation
        elif self.sensor_value >= self.desired_sensor_value + self.accuracy_value:
            self.logger.debug("Starting negative actuation")
            self.desired_positive_actuator_percent = 0.0
            self.desired_negative_actuator_percent = 100.0
            self.actuation_direction = "-"

        # No actuation required
        else:
            self.logger.debug("No actuation required")
            self.desired_positive_actuator_percent = 0.0
            self.desired_negative_actuator_percent = 0.0
            self.actuation_direction = None

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.desired_positive_actuator_percent = None
        self.desired_negative_actuator_percent = None
