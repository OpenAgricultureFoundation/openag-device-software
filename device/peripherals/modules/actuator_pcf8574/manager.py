# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.common.pcf8574 import driver
from device.peripherals.modules.actuator_pcf8574 import exceptions


class ActuatorPCF8574Manager(manager.PeripheralManager):
    """Manages an actuator controlled by a pcf85764 io expander."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize active high state
        self.is_active_high = self.communication["is_active_high"]

        # Initialize variable names
        self.actuator_name = self.variables["actuator"]["output_variable"]

    @property
    def desired_output(self) -> Optional[float]:
        """Gets desired output value."""
        value = self.state.get_environment_desired_actuator_value(self.actuator_name)
        if value != None:
            return float(value)
        return None

    @property
    def reported_output(self) -> Optional[float]:
        """Gets reported output value."""
        value = self.state.get_peripheral_reported_actuator_value(
            self.name, self.actuator_name
        )
        if value != None:
            return float(value)
        return None

    @reported_output.setter
    def reported_output(self, value: float) -> None:
        """Sets reported output value in shared state. Does not update environment from 
        manual mode."""
        self.state.set_peripheral_reported_actuator_value(
            self.name, self.actuator_name, value
        )
        if self.mode != modes.MANUAL:
            self.state.set_environment_reported_actuator_value(
                self.name, self.actuator_name, value
            )

    def initialize_peripheral(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.PCF8574Driver(
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
            self.logger.debug("Unable to initialize: {}".format(e))
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("No setup required")

    def update_peripheral(self) -> None:
        """Updates sensor by reading temperature and humidity values then 
        reports them to shared state."""

        # Check if desired output is unchanged
        if self.desired_output == None or self.desired_output == self.reported_output:
            return

        # Output has changed, set output and update reported value
        if self.desired_output == 1:
            if self.is_active_high:
                self.driver.set_high()
            else:
                self.driver.set_low()
            self.health = 100.0
        elif self.desired_output == 0:
            if self.is_active_high:
                self.driver.set_low()
            else:
                self.driver.set_high()
            self.health = 100.0
        else:
            message = "Received invalid desired output value: {}".format(
                self.desired_output
            )
            self.logger.error(message)
            self.health = 0.0
            self.mode = modes.ERROR

    def reset_peripheral(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

    def shutdown_peripheral(self) -> None:
        """Shutsdown peripheral."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.output = None
