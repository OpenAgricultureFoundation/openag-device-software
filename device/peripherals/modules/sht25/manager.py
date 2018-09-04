# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral.manager import PeripheralManager

# Import driver elements
from device.peripherals.modules.sht25.events import SHT25Events
from device.peripherals.modules.sht25.driver import SHT25Driver
from device.peripherals.modules.sht25.exceptions import DriverError


class SHT25Manager(PeripheralManager, SHT25Events):  # type: ignore
    """Manages an sht25 temperature and humidity sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.temperature_name = self.variables["sensor"]["temperature_celcius"]
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
        if self.mode != Modes.CALIBRATE:
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
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.humidity_name, value
            )

    def initialize(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = SHT25Driver(
                name=self.name,
                bus=self.bus,
                mux=self.mux,
                channel=self.channel,
                address=self.address,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except DriverError as e:
            self.logger.exception("Manager unable to initialize")
            self.health = 0.0
            self.mode = Modes.ERROR

    def setup(self) -> None:
        """Sets up manager."""
        self.logger.info("No setup required")

    def update(self) -> None:
        """Updates sensor by reading temperature and humidity values then 
        reports them to shared state."""

        # Read temperature
        try:
            temperature = self.driver.read_temperature(retry=True)
        except DriverError:
            self.logger.exception("Unable to read temperature")
            self.mode = Modes.ERROR
            self.health = 0.0
            return

        # Read humidity
        try:
            humidity = self.driver.read_humidity(retry=True)
        except DriverError:
            self.logger.exception("Unable to read humidity")
            self.mode = Modes.ERROR
            self.health = 0.0
            return

        # Update reported values
        self.temperature = temperature
        self.humidity = humidity
        self.health = 100.0

    def reset(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

        # Reset driver if not in error mode
        try:
            if self.mode != Modes.ERROR:
                self.driver.reset()
        except DriverError:
            self.logger.exception("Unable to reset driver")

        # Sucessfully reset
        self.logger.debug("Successfully reset")

    def shutdown(self) -> None:
        """Shutsdown sensor."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.temperature = None
        self.humidity = None
