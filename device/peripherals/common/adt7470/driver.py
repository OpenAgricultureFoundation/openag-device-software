# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Dict

# Import device utilities
from device.utilities import bitwise, logger
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.common.pca9633.simulator import PCA9633Simulator
from device.peripherals.common.pca9633 import exceptions

# Initialize registers
VERSION_REGISTER = 0x3F
CONFIG_REGISTER_1 = 0x40
CONFIG_REGISTER_2 = 0x74
TEMPERATURE_BASE_REGISTER = 0x20
MAX_TEMPERATURE_REGISTER = 0x78
TEMPERATURE_LIMIT_BASE_REGISTER = 0x44
TACHOMETER_BASE_REGISTER = 0x2A
CURRENT_DUTY_CYCLE_BASE_REGISTER = 0x32
MIN_DUTY_CYCLE_BASE_REGISTER = 0x6A
MAX_DUTY_CYCLE_BASE_REGISTER = 0x38

# Initialize masks
ENABLE_MONITORING_MASK = 0x80
DISABLE_MONITORING_MASK = 0x7F
SHUTDOWN_MASK = 0x01


class ADT7470Driver:
    """Driver for ADT7470 temperature sensor hub and fan controller."""

    def __init__(
        self,
        name: str,
        i2c_lock: threading.RLock,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes driver."""

        # Initialize logger
        logname = "ADT7470({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")

        # Initialize i2c lock
        self.i2c_lock = i2c_lock

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = PCA9633Simulator
        else:
            Simulator = None

        # Initialize driver parameters
        self.name = name

        # Initialize I2C
        try:
            self.i2c = I2C(
                name="ADT7470-{}".format(name),
                i2c_lock=i2c_lock,
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
            self.hardware_version = self.read_version()
        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

    def read_version(self, retry: bool = True) -> int:
        """Reads hardware version."""
        self.logger.debug("Reading version")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                version = self.i2c.read_register(VERSION_REGISTER)
                self.logger.debug("Version: {}".format(version))
                return version
            except I2CError as e:
                raise exceptions.ReadVersionError(logger=self.logger) from e

    # def enable_automatic_fan_control(self, fan_id: int) -> None:
    #     """Enables automatic fan control."""
    #     self.logger.debug("Enabling automatic fan control for fan {}".format(fan_id))

    #     # Lock thread in case we have multiple io expander instances
    #     with self.i2c_lock:

    #         # Send set output command to ic
    #         try:
    #             low_address = PWM_BASE_REGISTER + 2 * fan_id
    #             high_address = low_address + 1
    #             low_byte = self.i2c.read_register(low_address)
    #             high_byte = self.i2c.read_register(high_address)
    #         except I2CError as e:
    #             raise exceptions.ReadTachometerError(logger=self.logger) from e

    def enable_monitoring(self, retry: bool = True) -> None:
        """Enables temperature monitoring."""
        self.logger.debug("Enabling monitoring")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_1)
                register_byte |= ENABLE_MONITORING_MASK
                self.i2c.write_register(CONFIG_REGISTER_1, register_byte)
            except I2CError as e:
                raise exceptions.EnableMonitoringError(logger=self.logger) from e

    def disable_monitoring(self, retry: bool = True) -> None:
        """Disables temperature monitoring."""
        self.logger.debug("Disabling monitoring")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_1)
                register_byte &= DISABLE_MONITORING_MASK
                self.i2c.write_register(CONFIG_REGISTER_1, register_byte)
            except I2CError as e:
                raise exceptions.DisableMonitoringError(logger=self.logger) from e

    def shutdown(self, retry: bool = True) -> None:
        """Shuts down peripheral."""
        self.logger.debug("Shutting down")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_2)
                register_byte |= SHUTDOWN_MASK
                self.i2c.write_register(CONFIG_REGISTER_2, register_byte)
            except I2CError as e:
                raise exceptions.ShutdownError(logger=self.logger) from e

    def read_temperature(self, sensor_id: int, retry: bool = True) -> float:
        """Reads temperature sensor."""
        self.logger.debug("Reading temperature from sensor {}".format(sensor_id))

        # Validate sensor id
        if sensor_id < 0 or sensor_id > 9:
            raise ValueError("Sensor id must be a value between 0-9")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                # Take temperature reading
                self.enable_monitoring()
                time.sleep(0.2)  # Wait 200 ms
                self.disable_monitoring()

                # Get temperature value
                temperature = self.i2c.read_register(
                    TEMPERATURE_BASE_REGISTER + sensor_id
                )

                # Check for negative temperatures
                if temperature > 127:
                    temperature = temperature - 256

                # Return temperature value
                self.logger.debug("Temperature: {}".format(temperature))
                return temperature
            except I2CError as e:
                raise exceptions.ReadTemperatureError(logger=self.logger) from e

    def read_max_temperature(self, retry: bool = True) -> float:
        """Reads temperature sensor."""
        self.logger.debug("Reading max temperature")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                max_temperature = self.i2c.read_register(MAX_TEMPERATURE_REGISTER)
                self.logger.debug("Max Temperature: {}".format(max_temperature))
                return max_temperature
            except I2CError as e:
                raise exceptions.ReadMaxTemperatureError(logger=self.logger) from e

    def read_tachometer(self, fan_id: int) -> float:
        """Reads fan tachometer."""
        self.logger.debug("Reading tachometer for fan {}".format(fan_id))

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                low_address = TACHOMETER_BASE_REGISTER + 2 * fan_id
                high_address = low_address + 1
                low_byte = self.i2c.read_register(low_address)
                high_byte = self.i2c.read_register(high_address)
            except I2CError as e:
                raise exceptions.ReadTachometerError(logger=self.logger) from e

    def read_current_duty_cycle(self, fan_id: int) -> float:
        """Reads a fan pwm."""
        self.logger.debug("Reading curent duty cycle for fan {}".format(fan_id))

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Send set output command to ic
            try:
                low_address = CURRENT_DUTY_CYCLE_BASE_REGISTER + fan_id
                register_byte = self.i2c.read_register(low_address)
            except I2CError as e:
                raise exceptions.ReadCurrentDutyCycleError(logger=self.logger) from e

        # Convert register byte to duty cycle
        duty_cycle = round(0.39 * register_byte, 2)

        # Return duty cycle
        self.logger.debug("Duty cycle: {}%".format(duty_cycle))
        return duty_cycle

    def write_min_duty_cycle(self, fan_id: int, duty_cycle: float):
        """Writes max pwm duty cycle."""
        self.logger.debug("Writing min duty cycle for fan {}".format(fan_id))

        # Validate duty cycle
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError("Duty cycle must be a value between 0-100")

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Convert duty cycle
        duty_cycle_byte = int(duty_cycle / 0.39)

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Write to driver
            try:
                address = MIN_DUTY_CYCLE_BASE_REGISTER + fan_id
                self.i2c.write_register(address, duty_cycle_byte)
            except I2CError as e:
                raise exceptions.WriteMinDutyCycleError(logger=self.logger) from e

    def write_max_duty_cycle(self, fan_id: int, duty_cycle: float):
        """Writes max pwm duty cycle."""
        self.logger.debug("Writing max duty cycle for fan {}".format(fan_id))

        # Validate duty cycle
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError("Duty cycle must be a value between 0-100")

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Convert duty cycle
        duty_cycle_byte = int(duty_cycle / 0.39)

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Write to driver
            try:
                address = MAX_DUTY_CYCLE_BASE_REGISTER + fan_id
                self.i2c.write_register(address, duty_cycle_byte)
            except I2CError as e:
                raise exceptions.WriteMaxDutyCycleError(logger=self.logger) from e
