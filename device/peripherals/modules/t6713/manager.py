# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import driver elements
from device.peripherals.modules.t6713 import driver, exceptions


class T6713Manager(manager.PeripheralManager):
    """Manages a t6713 co2 sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager, initializes parent class, and initializes 
        sensor variable name. """

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.co2_name = self.variables["sensor"]["carbon_dioxide_ppm"]

    @property
    def co2(self) -> Optional[float]:
        """Gets carbon dioxide value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.co2_name
        )
        if value != None:
            return float(value)
        return None

    @co2.setter
    def co2(self, value: float) -> None:
        """Sets carbon dioxide value in shared state. Does not update enironment from 
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
            self.driver = driver.T6713Driver(
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
            self.logger.exception("Manager unable to initialize")
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("Setting up manager")

        try:
            self.driver.setup()
        except exceptions.DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = modes.ERROR
            self.health = 0

    def update_peripheral(self) -> None:
        """Updates peripheral by reading co2 value then reporting to shared state."""

        # Read co2
        try:
            co2 = self.driver.read_co2()
        except exceptions.DriverError:
            self.logger.exception("Unable to read co2")
            self.mode = modes.ERROR
            self.health = 0.0
            return

        # Update reported values
        self.co2 = co2
        self.health = 100.0

    def reset_peripheral(self) -> None:
        """Resets peripheral."""
        self.logger.info("Resetting")
        self.clear_reported_values()

        # Reset driver if not in error mode
        try:
            if self.mode != modes.ERROR:
                self.driver.reset()
        except exceptions.DriverError:
            self.logger.exception("Unable to reset driver")

    def shutdown_peripheral(self) -> None:
        """Shutsdown peripheral."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.co2 = None
