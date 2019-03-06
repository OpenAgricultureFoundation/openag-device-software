# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.modules.ccs811 import driver, exceptions


class CCS811Manager(manager.PeripheralManager):  # type: ignore
    """Manages an ccs811 co2 sensor."""

    # Initialize compensation variable parameters
    temperature_threshold = 0.1  # celsius
    prev_temperature: Optional[float] = 25.0
    humidity_threshold = 0.1  # percent
    prev_humidity: Optional[float] = 50.0

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.co2_name = self.variables["sensor"]["co2_ppm"]
        self.tvoc_name = self.variables["sensor"]["tvoc_ppb"]
        self.temperature_name = self.variables["compensation"]["temperature_celsius"]
        self.humidity_name = self.variables["compensation"]["humidity_percent"]

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
        """Sets co2 value in shared state. Does not update environment from 
        calibration mode."""
        self.state.set_peripheral_reported_sensor_value(self.name, self.co2_name, value)
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.co2_name, value
            )

    @property
    def tvoc(self) -> Optional[float]:
        """Gets tvoc value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.tvoc_name
        )
        if value != None:
            return float(value)
        return None

    @tvoc.setter
    def tvoc(self, value: float) -> None:
        """ Sets tvoc value in shared state. Does not update environment from 
        calibration mode. """
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.tvoc_name, value
        )
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.tvoc_name, value
            )

    @property
    def temperature(self) -> Optional[float]:
        """Gets compensation temperature value from shared environment state."""
        value = self.state.get_environment_reported_sensor_value(self.temperature_name)
        if value != None:
            return float(value)
        return None

    @property
    def humidity(self) -> Optional[float]:
        """Gets compensation humidity value from shared environment state."""
        value = self.state.get_environment_reported_sensor_value(self.humidity_name)
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
            self.driver = driver.CCS811Driver(
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
            self.logger.exception("Unable to initialize")
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("Setting up")
        self.driver.setup()

    def update_peripheral(self) -> None:
        """Updates peripheral by reading co2 and tvoc values then reports them to shared 
        state. Checks for compensation variables before read."""

        # Update compensation variables if new value
        if self.new_compensation_variables():

            # Set compensation variables
            try:
                self.driver.write_environment_data(
                    temperature=self.temperature, humidity=self.humidity
                )

                # Update previous values
                if self.temperature != None:
                    self.prev_temperature = self.temperature
                if self.humidity != None:
                    self.prev_humidity = self.humidity

            except exceptions.DriverError:
                self.logger.exception("Unable to set compensation variables")
                self.mode = modes.ERROR
                self.health = 0.0

        # Read co2 and tvoc
        try:
            co2, tvoc = self.driver.read_algorithm_data()
        except exceptions.DriverError:
            self.logger.exception("Unable to read co2, tvoc")
            self.mode = modes.ERROR
            self.health = 0.0
            return

        # Update reported values
        self.co2 = co2
        self.tvoc = tvoc
        self.health = 100.0

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.co2 = None
        self.tvoc = None

    def new_compensation_variables(self) -> bool:
        """Checks if there is a new compensation variable value."""

        # Check if in calibration mode
        if self.mode == modes.CALIBRATE:
            return False

        # Check for new temperature
        if self.temperature != None:

            # Check for prev temperature
            if self.prev_temperature == None:
                return True

            # Check for sufficiently different temperature
            delta_t = abs(self.temperature - self.prev_temperature)  # type: ignore
            if delta_t > self.temperature_threshold:
                return True

        # Check for new humidity
        if self.humidity != None:

            # Check for prev humidity
            if self.prev_humidity == None:
                return True

            # Check for sufficiently different humidity
            delta_h = abs(self.humidity - self.prev_humidity)  # type: ignore
            if delta_h > self.humidity_threshold:
                return True

        # New compensation variable does not exists
        return False
