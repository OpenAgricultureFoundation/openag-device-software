# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.classes.atlas import exceptions
from device.peripherals.modules.atlas_co2 import driver


class AtlasCo2Manager(manager.PeripheralManager):
    """Manages an Atlas Scientific co2 sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.co2_name = self.variables["sensor"]["co2"]

    @property
    def co2(self) -> Optional[float]:
        """Gets co2 value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.co2_name
        )
        if value != None:
            return float(value)
        return None

    @co2.setter
    def co2(self, value: float) -> None:
        """Sets co2 value in shared state. Does not update enironment from
        calibration mode."""
        self.state.set_peripheral_reported_sensor_value(self.name, self.co2_name, value)
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.co2_name, value
            )

    def initialize_peripheral(self) -> None:
        """Initializes peripheral."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.AtlasCo2Driver(
                name=self.name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                address=self.address,
                mux=self.mux,
                channel=self.channel,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except exceptions.DriverError as e:
            self.logger.exception("Unable to initialize")
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.info("Setting up")

        try:
            self.driver.setup()
        except exceptions.DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = modes.ERROR
            self.health = 0

    def update_peripheral(self) -> None:
        """Updates peripheral."""
        self.logger.info("Updating")

        try:
            self.co2 = self.driver.read_co2()
            self.health = 100.0
        except exceptions.DriverError as e:
            self.logger.error("Unable to update")
            self.mode = modes.ERROR
            self.health = 0
            returnte

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.co2 = None
