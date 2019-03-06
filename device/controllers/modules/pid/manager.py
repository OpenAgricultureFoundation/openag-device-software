# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import controller manager parent class
from device.controllers.classes.controller import manager, modes

# Import PID class
from device.controllers.modules.pid.pid import PID

# TODO: the temp set point is the "desired value" of "air_temperature_celsius" sensor.

# TODO: how do I handle the defrost loop?  need to put the actuator in manual mode? Create a Defrost controller.   It puts this PIDController in manual mode, does defrost loop, puts it back in auto


class PIDControllerManager(manager.ControllerManager):
    """Manages a controller with PID logic."""

    # --------------------------------------------------------------------------------------
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.sensor_name: str = self.variables.get("sensor_name", None)
        self.positive_actuator_name: str = self.variables.get(
            "positive_actuator_name", None
        )
        self.negative_actuator_name: str = self.variables.get(
            "negative_actuator_name", None
        )

        # Get the controller properties
        self.P: float = float(self.properties.get("P", 0.0))
        self.I: float = float(self.properties.get("I", 0.0))
        self.D: float = float(self.properties.get("D", 0.0))
        self.windup: float = float(self.properties.get("windup", 0.0))
        self.set_point_celsius: float = float(
            self.properties.get("set_point_celsius", 0.0)
        )
        self.sample_time_seconds: float = float(
            self.properties.get("sample_time_seconds", 0.0)
        )

        # Initialize our PID control class
        self.pid: PID = PID(self.P, self.I, self.D)
        self.pid.setWindup(self.windup)
        self.pid.setSampleTime(self.sample_time_seconds)

    # --------------------------------------------------------------------------------------
    # This is the temperature sensor current temp.
    @property
    def sensor_value(self) -> Optional[float]:
        """Gets sensor value."""
        value = self.state.get_environment_reported_sensor_value(self.sensor_name)
        if value != None:
            return float(value)
        return None

    # --------------------------------------------------------------------------------------
    # This is the temperature sensor "set point".
    @property
    def desired_sensor_value(self) -> Optional[float]:
        """Gets desired sensor value."""
        value = self.state.get_environment_desired_sensor_value(self.sensor_name)
        if value != None:
            return float(value)
        return None

    # --------------------------------------------------------------------------------------
    @property
    def desired_positive_actuator_percent(self) -> Optional[float]:
        """Gets positive actuator value."""
        value = self.state.get_environment_desired_actuator_value(
            self.positive_actuator_name
        )
        if value != None:
            return float(value)
        return None

    # --------------------------------------------------------------------------------------
    @desired_positive_actuator_percent.setter
    def desired_positive_actuator_percent(self, value: float) -> None:
        """Sets reported output value in shared state."""
        if self.positive_actuator_name == None:
            return
        self.state.set_environment_desired_actuator_value(
            self.positive_actuator_name, value
        )

    # --------------------------------------------------------------------------------------
    @property
    def desired_negative_actuator_percent(self) -> Optional[float]:
        """Gets positive actuator value."""
        value = self.state.get_environment_desired_actuator_value(
            self.negative_actuator_name
        )
        if value != None:
            return float(value)
        return None

    # --------------------------------------------------------------------------------------
    @desired_negative_actuator_percent.setter
    def desired_negative_actuator_percent(self, value: float) -> None:
        """Sets reported output value in shared state."""
        if self.negative_actuator_name == None:
            return
        self.state.set_environment_desired_actuator_value(
            self.negative_actuator_name, value
        )

    # --------------------------------------------------------------------------------------
    def initialize_controller(self) -> None:
        """Initializes controller."""
        self.logger.info("Initializing")
        self.clear_reported_values()

    # --------------------------------------------------------------------------------------
    def update_controller(self) -> None:
        """Updates controller."""

        # Check sensor values are initialized
        if type(self.sensor_value) != float or type(self.desired_sensor_value) != float:
            self.desired_positive_actuator_percent = None
            self.desired_negative_actuator_percent = None
            self.logger.warning("sensor_value or desired_sensor_value is not a float.")
            return

        # The temp set point is the "desired" "air_temperature_celsius" sensor value.
        self.pid.setSetPoint(self.desired_sensor_value)
        self.logger.info(
            "Desired set point for {} is {}.".format(
                self.sensor_name, self.desired_sensor_value
            )
        )

        # Update the PID controller with the current temp from the sensor
        self.pid.update(self.sensor_value)
        self.logger.debug(
            "temperature={} pid_output={}".format(
                self.sensor_value, self.pid.getOutput()
            )
        )

        # For now just slam between 0 and 100%.
        # TODO: Use a smaller % as the output gets closer to the set point.

        if 1.0 > abs(self.pid.getOutput()):
            # No actuation required for tiny output values
            self.logger.debug("No actuation required")
            self.desired_positive_actuator_percent = 0.0
            self.desired_negative_actuator_percent = 0.0
        elif 0.0 > self.pid.getOutput():
            # Make it colder
            self.logger.debug(
                "Make it colder, pid output={}".format(self.pid.getOutput())
            )
            # Negative actuation is the chiller (temp goes down)
            self.desired_positive_actuator_percent = 0.0
            self.desired_negative_actuator_percent = 100.0
        else:
            # Make it warmer
            self.logger.debug(
                "Make it warmer, pid output={}".format(self.pid.getOutput())
            )
            # Positive actuation is the heater (temp goes up)
            self.desired_positive_actuator_percent = 100.0
            self.desired_negative_actuator_percent = 0.0

    # --------------------------------------------------------------------------------------
    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.desired_positive_actuator_percent = None
        self.desired_negative_actuator_percent = None
