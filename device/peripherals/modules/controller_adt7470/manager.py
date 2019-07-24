# Import standard python modules
import time, json

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.common.pca9633 import driver
from device.peripherals.modules.indicator_pca9633 import exceptions, events


class ControllerADT7470Manager(manager.PeripheralManager):
    """Manages a temperature sensor hub and fan controller driver."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize sensors and actuators
        self.sensors = self.parameters["sensors"]
        self.actuators = self.parameters["actuators"]

        # Initialize setpoints
        # for sensor_id, temperature_limit in enumerate(self.temperature_limits):
        #     name = self.temperature_names[sensor_id]
        #     value = "<{}".format(temperature_limit)
        #     self.state.set_peripheral_desired_sensor_value(self.name, name, value)
        #     self.state.set_environment_desired_sensor_value(name, value)

        # Set default sampling interval
        self.default_sampling_interval = 3  # seconds
        self.prev_update = 0  # timestamp

    def set_temperature(self, name, value) -> None:
        """Sets a temperature value in state."""
        self.state.set_peripheral_reported_sensor_value(self.name, name, value)
        self.state.set_environment_reported_sensor_value(self.name, name, value)

    def set_fan_output_percent(self, name, value) -> None:
        """Sets a fan output percent value in state."""
        self.state.set_peripheral_reported_actuator_value(self.name, name, value)
        self.state.set_environment_reported_actuator_value(name, value)
        self.state.set_environment_desired_actuator_value(name, value)

    def initialize_peripheral(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.ADT7470(
                name=self.name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                mux=self.mux,
                channel=self.channel,
                address=self.address,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except exceptions.DriverError as e:
            self.logger.exception("Unable to initialize: {}".format(e))
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("Setting up peripheral")
        try:
            # Set fan modes and limits
            for actuator in self.actuators:
                # Setup manual fans
                if actuator["control_sensor_id"] == None:
                    self.driver.enable_manual_fan_control(actuator["fan_id"])

                # Setup automatic fans
                else:
                    self.driver.enable_automatic_fan_control(actuator["fan_id"])
                    self.driver.write_thermal_zone_config(actuator["sensor_id"])

        except exceptions.DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = modes.ERROR
            return

    def update_peripheral(self) -> None:
        """Updates peripheral by getting temperatures and fan speeds."""
        try:
            # Update temperatures
            for sensor_id, temperature_name in enumerate(self.temperature_names):
                temperature_value = self.driver.get_temperature(sensor_id)
                self.set_temperature(temperature_name, temperature_value)

            # Update fans
            for sensor_id, fan_name in enumerate(self.fan_names):
                fan_output_percent = self.driver.get_fan_output_percent(sensor_id)
                self.set_fan_output_percent(fan_name, fan_output_percent)

        except exceptions.DriverError as e:
            self.logger.exception("Unable to update peripheral: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0

    def reset_peripheral(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")
        self.clear_reported_values()

    def shutdown_peripheral(self) -> None:
        """Shutsdown peripheral."""
        self.logger.info("Shutting down")
        try:
            self.driver.shutdown()
        except exceptions.DriverError as e:
            message = "Unable to turn off driver before shutting down: {}".format(
                type(e)
            )
            self.logger.warning(message)
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        for temperature_name in self.temperature_names:
            self.set_temperature(temperature_name, None)
        for fan_name in self.fan_names:
            self.set_fan_output_percent(fan_name, None)
