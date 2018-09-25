# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral.manager import PeripheralManager
from device.peripherals.classes.peripheral.exceptions import DriverError

# Import module elements
from device.peripherals.modules.atlas_temp.events import AtlasTempEvents
from device.peripherals.modules.atlas_temp.driver import AtlasTempDriver


class AtlasTempManager(PeripheralManager):  # type: ignore
    """ Manages an Atlas Scientific temperature driver. """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize events
        self.events = AtlasTempEvents(self)

        # Initialize variable names
        self.temperature_name = self.variables["sensor"]["temperature"]

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
        """Sets temperature value in shared state. Does not update enironment from
        calibration mode."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.temperature_name, value
        )
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.temperature_name, value
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
            self.driver = AtlasTempDriver(
                name=self.name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                address=self.address,
                mux=self.mux,
                channel=self.channel,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except DriverError as e:
            self.logger.exception("Unable to initialize")
            self.health = 0.0
            self.mode = Modes.ERROR

    def setup(self) -> None:
        """Sets up driver."""
        self.logger.info("Setting up")

        try:
            self.driver.setup()
        except DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = Modes.ERROR
            self.health = 0

    def update(self) -> None:
        """Updates driver."""
        self.logger.info("Updating")

        try:
            self.temperature = self.driver.read_temperature()
            self.health = 100.0
        except DriverError as e:
            self.logger.error("Unable to update")
            self.mode = Modes.ERROR
            self.health = 0
            return

    def reset(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")
        self.clear_reported_values()

    def shutdown(self) -> None:
        """Shutsdown sensor."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.temperature = None
