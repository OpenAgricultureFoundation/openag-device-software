# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.modules.atlas_do import driver, exceptions


class AtlasDOManager(manager.PeripheralManager):
    """Manages an atlas scientific dissolved oxygen driver."""

    # Initialize variable parameters
    temperature_threshold = 0.1  # celsius
    prev_temperature = 0
    pressure_threshold = 0.1  # kPa
    prev_pressure = 0
    ec_threshold = 0.1  # mS/cm
    prev_ec = 0

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.do_name = self.variables["sensor"]["do_mg_l"]
        self.temperature_name = self.variables["compensation"]["temperature_celsius"]
        self.pressure_name = self.variables["compensation"]["pressure_kpa"]
        self.ec_name = self.variables["compensation"]["ec_ms_cm"]

    @property
    def do(self) -> Optional[float]:
        """Gets dissolved oxygen value."""
        value = self.state.get_peripheral_reported_sensor_value(self.name, self.do_name)
        if value != None:
            return float(value)
        return None

    @do.setter
    def do(self, value: float) -> None:
        """Sets dissolved oxygen value in shared state. Does not update enironment from
        calibration mode."""
        self.state.set_peripheral_reported_sensor_value(self.name, self.do_name, value)
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.do_name, value
            )

    @property
    def temperature(self) -> Optional[float]:
        """Gets compensation temperature value from shared environment state."""
        value = self.state.get_environment_reported_sensor_value(self.temperature_name)
        if value != None:
            return float(value)
        return None

    @property
    def pressure(self) -> Optional[float]:
        """Gets compensation pressure value from shared environment state."""
        value = self.state.get_environment_reported_sensor_value(self.pressure_name)
        if value != None:
            return float(value)
        return None

    @property
    def ec(self) -> Optional[float]:
        """Gets compensation EC value from shared environment state."""
        value = self.state.get_environment_reported_sensor_value(self.ec_name)
        if value != None:
            return float(value)
        return None

    def initialize_peripheral(self) -> None:
        """Initializes peripheral."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.AtlasDODriver(
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
            self.logger.exception("Unable to setup: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0

    def update_peripheral(self) -> None:
        """Updates peripheral."""
        self.logger.info("Updating")

        try:
            # Update compensation temperature if new value
            if self.new_compensation_temperature():
                self.driver.set_compensation_temperature(self.temperature)

            # Update compensation pressure if new value
            if self.new_compensation_pressure():
                self.driver.set_compensation_pressure(self.pressure)

            # Update compensation temperature if new value
            if self.new_compensation_ec():
                self.driver.set_compensation_ec(self.ec)

            # Read pH and update health
            self.do = self.driver.read_do()
            self.health = 100.0

        except exceptions.DriverError as e:
            self.logger.error("Unable to update")
            self.mode = modes.ERROR
            self.health = 0
            return

    def new_compensation_temperature(self) -> bool:
        """Checks if there is a new compensation temperature value."""

        # Check if calibrating
        if self.mode == modes.CALIBRATE:
            return False

        # Check if compensation temperature exists
        if self.temperature == None:
            return False

        # Check if prev temperature is not none
        if self.prev_temperature == None:
            return True

        # Check if temperature value sufficiently different
        delta_t = abs(self.temperature - self.prev_temperature)  # type: ignore
        if delta_t < self.temperature_threshold:
            return False

        # New compensation temperature exists
        return True

    def new_compensation_pressure(self) -> bool:
        """Checks if there is a new compensation pressure value."""

        # Check if calibrating
        if self.mode == modes.CALIBRATE:
            return False

        # Check if compensation pressure exists
        if self.pressure == None:
            return False

        # Check if prev pressure is not none
        if self.prev_pressure == None:
            return True

        # Check if pressure value sufficiently different
        delta_p = abs(self.pressure - self.prev_pressure)  # type: ignore
        if delta_p < self.pressure_threshold:
            return False

        # New compensation pressure exists
        return True

    def new_compensation_ec(self) -> bool:
        """Checks if there is a new compensation electrical conductivity value."""

        # Check if calibrating
        if self.mode == modes.CALIBRATE:
            return False

        # Check if compensation ec exists
        if self.ec == None:
            return False

        # Check if prev ec is not none
        if self.prev_ec == None:
            return True

        # Check if electrical conductivity value sufficiently different
        delta_e = abs(self.ec - self.prev_ec)  # type: ignore
        if delta_e < self.ec_threshold:
            return False

        # New compensation electrical conductivity exists
        return True

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.do = None
