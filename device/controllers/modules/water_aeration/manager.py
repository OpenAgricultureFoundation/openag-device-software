# Import standard python modules
from typing import Optional, Tuple, Dict, Any
import time

# Import controller manager parent class
from device.controllers.classes.controller import manager, modes


class WaterAerationControllerManager(manager.ControllerManager):
    """Manages a controller for a water aerator."""

    # TODO: Incorporate air source composition (gas concentrations, temperature, etc.)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names and defaults
        self.actuator_name = self.variables.get("actuator_name")
        self.rate_name = self.variables.get("rate_name")
        self.period_name = self.variables.get("period_name")
        self.duty_cycle_name = self.variables.get("duty_cycle_name")
        self.bubble_diameter_name = self.variables.get("bubble_diameter_name")
        self.water_volume_name = self.variables.get("water_volume_name")
        self.default_water_volume = self.parameters.get("default_water_volume")

        # Initialize setup properties
        self.actuator_is_boolean = self.properties.get("actuator_is_boolean")
        self.actuator_aeration_rate_map = self.properties.get(
            "actuator_aeration_rate_map"
        )
        self.bubble_diameter = self.properties.get("bubble_diameter")

        # Initialize local state
        self._period_end_time = 0
        self._on_end_time = 0
        self._prev_desired_rate: Optional[float] = None
        self._prev_desired_period: Optional[float] = None
        self._prev_desired_duty_cycle: Optional[float] = None

    @property
    def desired_rate(self) -> Optional[float]:
        """Gets desired aeration rate from shared state."""
        value = self.state.get_environment_desired_sensor_value(self.rate_name)
        if value != None:
            return float(value)
        return None

    @property
    def rate(self) -> Optional[float]:
        """Gets aeration rate from shared state."""
        value = self.state.get_environment_reported_sensor_value(self.rate_name)
        if value != None:
            return float(value)
        return None

    @rate.setter
    def rate(self, value: float) -> None:
        """Sets aeration rate in shared state."""
        self.state.set_environment_reported_sensor_value(
            self.name, self.rate_name, value
        )

    @property
    def desired_period(self) -> Optional[float]:
        """Gets desired aeration period."""
        value = self.state.get_environment_desired_sensor_value(self.period_name)
        if value != None:
            return float(value)
        return None

    @property
    def period(self) -> Optional[float]:
        """Gets aeration period from shared state."""
        value = self.state.get_environment_reported_sensor_value(self.period_name)
        if value != None:
            return float(value)
        return None

    @period.setter
    def period(self, value: float) -> None:
        """Sets aeration period in shared state."""
        self.state.set_environment_reported_sensor_value(
            self.name, self.period_name, value
        )

    @property
    def desired_duty_cycle(self) -> Optional[float]:
        """Gets desired aeration duty cycle from shared state."""
        value = self.state.get_environment_desired_sensor_value(self.duty_cycle_name)
        if value != None:
            return float(value)
        return None

    @property
    def duty_cycle(self) -> Optional[float]:
        """Gets aeration duty cucle from shared state."""
        value = self.state.get_environment_reported_sensor_value(self.duty_cycle_name)
        if value != None:
            return float(value)
        return None

    @duty_cycle.setter
    def duty_cycle(self, value: float) -> None:
        """Sets aeration duty cycle in shared state."""
        self.state.set_environment_reported_sensor_value(
            self.name, self.duty_cycle_name, value
        )

    @property
    def bubble_diameter(self) -> Optional[float]:
        """Gets aeration bubble diameter from shared state."""
        value = self.state.get_environment_reported_sensor_value(
            self.bubble_diameter_name
        )
        if value != None:
            return float(value)
        return None

    @bubble_diameter.setter
    def bubble_diameter(self, value: float) -> None:
        """Sets aeration bubble diameter in shared state."""
        self.state.set_environment_reported_sensor_value(
            self.name, self.bubble_diameter_name, value
        )

    @property
    def water_volume(self) -> Optional[float]:
        """Gets water volume from shared state."""
        value = self.state.get_environment_reported_sensor_value(self.water_volume_name)
        if value != None:
            return float(value)
        return None

    @water_volume.setter
    def water_volume(self, value: float) -> None:
        """Sets water volume in shared state."""
        self.state.set_environment_reported_sensor_value(
            self.name, self.water_volume_name, value
        )

    @property
    def desired_actuator_percent(self) -> Optional[float]:
        """Gets desired actuator value from shared state."""
        value = self.state.get_environment_desired_actuator_value(self.actuator_name)
        if value != None:
            return float(value)
        return None

    @desired_actuator_percent.setter
    def desired_actuator_percent(self, value: float) -> None:
        """Sets desired actuator value in shared state."""
        if self.actuator_name == None:
            return
        self.state.set_environment_desired_actuator_value(self.actuator_name, value)

    def initialize_controller(self) -> None:
        """Initializes controller."""
        self.logger.info("Initializing")
        self.clear_reported_values()

    def update_controller(self) -> None:
        """Updates controller."""
        new_values_exist = self.new_desired_values()
        self.update_desired_actuator_percent(new_values_exist)

    def new_desired_values(self) -> bool:
        """Checks for new desired values."""
        new_values_exist = False
        if self.desired_rate != self._prev_desired_rate:
            self._prev_desired_rate = self.desired_rate
            new_values_exist = True
        if self.desired_period != self._prev_desired_period:
            self._prev_desired_period = self.desired_period
            self.period = self.desired_period
            new_values_exist = True
        if self.desired_duty_cycle != self._prev_desired_duty_cycle:
            self._prev_desired_duty_cycle = self.desired_duty_cycle
            self.duty_cycle = self.desired_duty_cycle
            new_values_exist = True
        return new_values_exist

    def update_desired_actuator_percent(self, new_values_exist: bool) -> None:
        """Updates desired actuator percent."""

        # Verify period and duty cycle are set
        if self.period == None or self.duty_cycle == None:
            self.rate = 0
            self.desired_actuator_percent = 0
            return

        # Get current time
        current_time = time.time()

        # Check for new values
        if new_values_exist:
            self.logger.debug("Received new values")
            self.update_timers(current_time)

        # Check for period end
        if current_time > self._period_end_time:
            self.logger.debug("Period ended")
            self.update_timers(current_time)

        # Check if actuator should be on/off
        if current_time < self._on_end_time:
            self.update_actuator_on_percent()
        else:
            self.desired_actuator_percent = 0
            self.rate = 0

    def update_timers(self, current_time: float) -> None:
        """Updates timers for translating period and duty cycle into on/off states."""
        self._period_end_time = current_time + (self.period * 60)  # type: ignore
        self._on_end_time = current_time + (  # type: ignore
            self.period * 60 * self.duty_cycle / 100  # type: ignore
        )

    def update_actuator_on_percent(self) -> None:
        """Updates actuator on percent and resulting rate."""

        # Verify water volume is set
        if self.water_volume == None:
            self.water_volume = self.default_water_volume

        # Verify actuator is boolean
        if not self.actuator_is_boolean:
            raise NotImplementedError
        else:
            self.desired_actuator_percent = 100

        # Get actuator aeration rate
        # TODO: Support interpolation
        actuator_aeration_rate = self.actuator_aeration_rate_map.get("100")

        # Verify valid actuator aeration rate
        if actuator_aeration_rate == None:
            raise ValueError

        # Calculate aeration rate
        self.rate = actuator_aeration_rate / self.water_volume

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.period = None
        self.duty_cycle = None
        self.rate = 0
        self.desired_actuator_percent = 0
