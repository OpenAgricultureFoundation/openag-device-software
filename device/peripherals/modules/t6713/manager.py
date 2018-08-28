# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral.manager import PeripheralManager
from device.peripherals.classes.peripheral.exceptions import DriverError

# Import driver elements
from device.peripherals.modules.t6713.events import T6713Events
from device.peripherals.modules.t6713.driver import T6713Driver


class T6713Manager(PeripheralManager, T6713Events):  # type: ignore
    """Manages a t6713 co2 sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """ Instantiates manager Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.co2_name = self.parameters["variables"]["sensor"]["carbon_dioxide_ppm"]

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
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.co2_name, value
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
            self.driver = T6713Driver(
                name=self.name,
                bus=self.parameters["communication"]["bus"],
                mux=int(self.parameters["communication"]["mux"], 16),
                channel=self.parameters["communication"]["channel"],
                address=int(self.parameters["communication"]["address"], 16),
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except DriverError as e:
            self.logger.exception("Manager unable to initialize")
            self.health = 0.0
            self.mode = Modes.ERROR

    def setup(self) -> None:
        """Sets up sensor."""
        self.logger.debug("Setting up manager")

        try:
            self.driver.setup()
        except DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = Modes.ERROR
            self.health = 0

    def update(self) -> None:
        """Updates sensor by reading co2 value then reporting to shared state."""

        # Read co2
        try:
            co2 = self.driver.read_co2()
        except DriverError:
            self.logger.exception("Unable to read co2")
            self.mode = Modes.ERROR
            self.health = 0.0
            return

        # Update reported values
        self.co2 = co2
        self.health = 100.0

    def reset(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")
        self.clear_reported_values()

        # Reset driver if not in error mode
        try:
            if self.mode != Modes.ERROR:
                self.driver.reset()
        except DriverError:
            self.logger.exception("Unable to reset driver")

    def shutdown(self) -> None:
        """Shutsdown sensor."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.co2 = None
