# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.modules.adafruit_soil import driver, exceptions


class AdafruitSoilManager(manager.PeripheralManager):
    """Manages an Adafruit Capacitive Soil Sensor 4026"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager"""

        super().__init__(*args, **kwargs)
        self.temperature_name = self.variables["sensor"]["temperature_celsius"]
        self.moisture_name = self.variables["sensor"]["soil_moisture_level"]

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
    def moisture(self) -> Optional[int]:
        """Gets Moisture Level"""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.moisture_name
        )
        if value != None:
            return int(value)
        return None

    @moisture.setter
    def moisture(self, value: int) -> None:
        """Sets moisture level in shared state. Does not update environment from calibration mode."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.moisture_name, value
        )
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.moisture_name, value
            )

    def initialize_peripheral(self):
        """initializes manager."""
        self.logger.info("Initializing")

        self.clear_reported_values()

        self.health = 100

        try:
            self.driver = driver.AdafruitSoilDriver(
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
        """Updates sensor by reading temperature and moisture values then
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
            moisture = self.driver.read_moisture()
        except exceptions.DriverError as e:
            self.logger.debug("Unable to read moisture: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0
            return

        # Update reported values
        self.temperature = temperature
        self.moisture = moisture
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

        # Successfully reset
        self.logger.debug("Successfully reset")

    def shutdown_peripheral(self) -> None:
        """Shutsdown sensor."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.temperature = None
        self.moisture = None
