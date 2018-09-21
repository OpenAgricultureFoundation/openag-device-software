# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral.manager import PeripheralManager
from device.peripherals.classes.peripheral.exceptions import DriverError

# Import module elements
from device.peripherals.modules.atlas_ec.events import AtlasECEvents
from device.peripherals.modules.atlas_ec.driver import AtlasECDriver


class AtlasECManager(PeripheralManager):  # type: ignore
    """Manages an atlas scientific electrical conductivity sensor."""

    # Initialize compensation temperature parameters
    temperature_threshold = 0.1  # celcius
    prev_temperature = 0  # celcius

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize event handler
        self.events = AtlasECEvents(self)

        # Initialize variable names
        self.ec_name = self.variables["sensor"]["ec_ms_cm"]
        self.temperature_name = self.variables["compensation"]["temperature_celcius"]

    @property
    def ec(self) -> Optional[float]:
        """Gets electrical conductivity value."""
        value = self.state.get_peripheral_reported_sensor_value(self.name, self.ec_name)
        if value != None:
            return float(value)
        return None

    @ec.setter
    def ec(self, value: float) -> None:
        """Sets electrical conductivity value in shared state. 
        Does not update enironment from calibration mode."""
        self.state.set_peripheral_reported_sensor_value(self.name, self.ec_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.ec_name, value
            )

    @property
    def temperature(self) -> Optional[float]:
        """Gets compensation temperature value from shared environment state."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.temperature_name
        )
        if value != None:
            return float(value)
        return None

    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.debug("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = AtlasECDriver(
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
        """ Sets up manager."""
        self.logger.debug("Setting up manager")
        try:
            self.driver.setup()
        except DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = Modes.ERROR
            self.health = 0

    def update(self) -> None:
        """Updates sensor."""

        try:
            # Update compensation temperature if new value
            if self.new_compensation_temperature():
                self.driver.set_compensation_temperature(self.temperature)

            # Read pH and update health
            self.ec = self.driver.read_ec()
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
        self.ec = None
