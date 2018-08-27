# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral.manager import PeripheralManager

# Import module elements
from device.peripherals.modules.atlas_ph.events import AtlasPHEvents
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver
from device.peripherals.classes.atlas.exceptions import DriverError


class AtlasPHManager(PeripheralManager, AtlasPHEvents):  # type: ignore
    """Manages an Atlas Scientific pH sensor."""

    # Initialize compensation temperature parameters
    temperature_threshold = 0.1  # celcius
    prev_temperature = 0.0  # celcius

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.ph_name = self.variables["sensor"]["ph"]
        self.temperature_name = self.variables["compensation"]["temperature_celcius"]

    @property
    def ph(self) -> Optional[float]:
        """Gets potential hydrogen value."""
        value = self.state.get_peripheral_reported_sensor_value(self.name, self.ph_name)
        if value != None:
            return float(value)
        return None

    @ph.setter
    def ph(self, value: float) -> None:
        """Sets potential hydrogen value in shared state. Does not update enironment 
        from calibration mode."""
        self.state.set_peripheral_reported_sensor_value(self.name, self.ph_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.ph_name, value
            )

    @property
    def temperature(self) -> Optional[float]:
        """Gets compensation temperature value from shared environment state."""
        value = self.state.get_environment_reported_sensor_value(self.temperature_name)
        if value != None:
            return float(value)
        return None

    def initialize(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = AtlasPHDriver(
                name=self.name,
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
            return

    def setup(self) -> None:
        """Sets up sensor."""
        self.logger.info("Setting up")

        try:
            self.driver.setup()
        except DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = Modes.ERROR
            self.health = 0

    def update(self) -> None:
        """Updates sensor."""
        self.logger.info("Updating")

        try:
            # Update compensation temperature if new value
            if self.new_compensation_temperature():
                self.driver.set_compensation_temperature(self.temperature)

            # Read pH and update health
            self.ph = self.driver.read_ph()
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

    def new_compensation_temperature(self) -> bool:
        """Checks if there is a new compensation temperature value."""

        # Check if calibrating
        if self.mode == Modes.CALIBRATE:
            return False

        # Check if compensation temperature exists
        if self.temperature == None:
            return False

        # Check if temperature value sufficiently different
        delta = abs(self.temperature - self.prev_temperature)  # type: ignore
        if delta < self.temperature_threshold:
            return False

        # New compensation temperature exists
        return True

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.ph = None
