# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.modules.sht25 import driver, exceptions


class SHT25Manager(manager.PeripheralManager):
    """Manages an sht25 temperature and humidity sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.temperature_name = self.variables["sensor"]["temperature_celsius"]
        self.humidity_name = self.variables["sensor"]["humidity_percent"]

    @property
    def temperature(self) -> Optional[float]:
        """Gets temperature value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.temperature_name
        )
        if value != None:
            return float(value)
        return None

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Sets temperature value in shared state. Does not update environment from 
        calibration mode."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.temperature_name, value
        )
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.temperature_name, value
            )

    @property
    def humidity(self) -> Optional[float]:
        """Gets humidity value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.humidity_name
        )
        if value != None:
            return float(value)
        return None

    @humidity.setter
    def humidity(self, value: float) -> None:
        """Sets humidity value in shared state. Does not update environment from 
        calibration mode."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.humidity_name, value
        )
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.humidity_name, value
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
            self.driver = driver.SHT25Driver(
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

        # Read temperature
        try:
            temperature = self.driver.read_temperature()
        except exceptions.DriverError as e:
            self.logger.debug("Unable to read temperature: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0
            return

        # Read humidity
        try:
            humidity = self.driver.read_humidity()
        except exceptions.DriverError as e:
            self.logger.debug("Unable to read humidity: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0
            return

        # Update reported values
        self.temperature = temperature
        self.humidity = humidity
        self.health = 100.0

    def reset_peripheral(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

        # Reset driver
        try:
            self.driver.reset()
        except exceptions.DriverError as e:
            self.logger.debug("Unable to reset driver: {}".format(e))

        # Sucessfully reset
        self.logger.debug("Successfully reset")

    def shutdown_peripheral(self) -> None:
        """Shutsdown sensor."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.temperature = None
        self.humidity = None
