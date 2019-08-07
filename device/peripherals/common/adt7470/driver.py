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

# Define identification registers
VERSION_REGISTER = 0x3F

# Define config registers
CONFIG_REGISTER_1 = 0x40
CONFIG_REGISTER_2 = 0x74

# Define temperature sensing registers
TEMPERATURE_BASE_REGISTER = 0x20
MAXIMUM_TEMPERATURE_REGISTER = 0x78

# Define fan control registers
PWM_CONFIG_BASE_REGISTER = 0x68
PWM_MINIMUM_DUTY_CYCLE_BASE_REGISTER = 0x6A
PWM_MAXIMUM_DUTY_CYCLE_BASE_REGISTER = 0x38
PWM_CURRENT_DUTY_CYCLE_BASE_REGISTER = 0x32
THERMAL_ZONE_CONFIG_BASE_REGISTER = 0x7C
THERMAL_ZONE_MINIMUM_TEMPERATURE_BASE_REGISTER = 0x6E
TACHOMETER_BASE_REGISTER = 0x2A
FAN_PULSES_PER_REVOLUTION_REGISTER = 0x43


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

        # Read version
        with self.i2c_lock:
            try:
                version = self.i2c.read_register(VERSION_REGISTER)
                self.logger.debug("Version: {}".format(version))
                return version
            except I2CError as e:
                raise exceptions.ReadVersionError(logger=self.logger) from e

    def enable_manual_fan_control(self, fan_id: int) -> None:
        """Enables manual fan control."""
        self.logger.debug("Enabling manual fan control for fan {}".format(fan_id))

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Enable manual fan control
        with self.i2c_lock:
            try:
                register_address = PWM_CONFIG_BASE_REGISTER + int(fan_id / 2)
                register_byte = self.i2c.read_register(register_address)
                register_byte &= 255 - (1 << 7 - fan_id % 2)
                self.i2c.write_register(register_address, register_byte)
            except I2CError as e:
                raise exceptions.EnableManualFanControlError(logger=self.logger) from e

    def enable_automatic_fan_control(self, fan_id: int) -> None:
        """Enables automatic fan control."""
        self.logger.debug("Enabling automatic fan control for fan {}".format(fan_id))

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Enable automatic fan control
        with self.i2c_lock:
            try:
                register_address = PWM_CONFIG_BASE_REGISTER + int(fan_id / 2)
                register_byte = self.i2c.read_register(register_address)
                register_byte |= 1 << 7 - fan_id % 2
                self.i2c.write_register(register_address, register_byte)
            except I2CError as e:
                raise exceptions.EnableAutomaticFanControlError(
                    logger=self.logger
                ) from e

    def write_thermal_zone_config(self, fan_id: int, control_sensor_id: int) -> None:
        """Writes thermal zone for fan id to be controlled by sensor id."""
        self.logger.debug("Writing thermal zone config")

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Check if control sensor is enabled
        if control_sensor_id is None:
            raise ValueError("Control sensor id must be 'max' or 0-9")

        # Get register nibble
        if type(control_sensor_id) is str and control_sensor_id == "max":
            register_nibble = 0
        elif (
            type(control_sensor_id) is int
            and control_sensor_id >= 0
            and control_sensor_id <= 9
        ):
            register_nibble = control_sensor_id + 1
        else:
            raise ValueError("Control sensor id must be 'max' or 0-9")

        # Write thermal zone
        with self.i2c_lock:
            try:
                register_address = THERMAL_ZONE_CONFIG_BASE_REGISTER + int(fan_id / 2)
                register_byte = self.i2c.read_register(register_address)
                # self.logger.debug("init register_byte: {}".format(hex(register_byte)))
                nibble_index = ((fan_id + 1) % 2) * 4
                # self.logger.debug("nibble_index: {}".format(nibble_index))
                register_byte &= 0xF << (4 - nibble_index)  # Clear register nibble
                # self.logger.debug("clear register_byte: {}".format(hex(register_byte)))
                register_byte += register_nibble << nibble_index
                self.i2c.write_register(register_address, register_byte)
            except I2CError as e:
                raise exceptions.WriteThermalZoneConfigError(logger=self.logger) from e

    def write_thermal_zone_minimum_temperature(
        self, fan_id: int, minimum_temperature: float
    ) -> None:
        """Writes the minimum temperature for a fan."""
        self.logger.debug("Writing minimum temperature for fan {}".format(fan_id))

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Validate minimum temperature celcius
        if minimum_temperature < -127 or minimum_temperature > 127:
            raise ValueError("Minimum temperature must be a value between -127 to 127")

        # Convert temperature float to int
        temperature_int = int(minimum_temperature)

        # Convert temperature int to byte
        if temperature_int < 0:
            temperature_byte = 128 - temperature_int
        else:
            temperature_byte = temperature_int
        self.logger.debug("temperature_byte: {}".format(temperature_byte))

        # Write minimum temperature
        with self.i2c_lock:
            try:
                register_address = (
                    THERMAL_ZONE_MINIMUM_TEMPERATURE_BASE_REGISTER + fan_id
                )
                self.i2c.write_register(register_address, temperature_byte)
            except I2CError as e:
                raise exceptions.WriteThermalZoneMinimumTemperature(
                    logger=self.logger
                ) from e

    def write_minimum_duty_cycle(self, fan_id: int, duty_cycle: float) -> None:
        """Writes minimum pwm duty cycle for a fan."""
        self.logger.debug("Writing minimum duty cycle for fan {}".format(fan_id))

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Validate duty cycle
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError("Duty cycle must be a value between 0-100")

        # Convert duty cycle from float to byte
        duty_cycle_byte = int(duty_cycle / 0.392)

        # Write minimum duty cycle
        with self.i2c_lock:
            try:
                address = PWM_MINIMUM_DUTY_CYCLE_BASE_REGISTER + fan_id
                self.i2c.write_register(address, duty_cycle_byte)
            except I2CError as e:
                raise exceptions.WriteMinDutyCycleError(logger=self.logger) from e

    def write_maximum_duty_cycle(self, fan_id: int, duty_cycle: float) -> None:
        """Writes max pwm duty cycle for a fan."""
        self.logger.debug("Writing maximum duty cycle for fan {}".format(fan_id))

        # Validate duty cycle
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError("Duty cycle must be a value between 0-100")

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Convert duty cycle from float to int
        duty_cycle_byte = int(duty_cycle / 0.392)

        # Write maximum duty cycle
        with self.i2c_lock:
            try:
                address = PWM_MAXIMUM_DUTY_CYCLE_BASE_REGISTER + fan_id
                self.i2c.write_register(address, duty_cycle_byte)
            except I2CError as e:
                raise exceptions.WriteMaxDutyCycleError(logger=self.logger) from e

    def read_current_duty_cycle(self, fan_id: int) -> float:
        """Read the current duty cycle for a fan."""
        self.logger.debug("Reading curent duty cycle for fan {}".format(fan_id))

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Read current duty cycle
        with self.i2c_lock:
            try:
                low_address = PWM_CURRENT_DUTY_CYCLE_BASE_REGISTER + fan_id
                register_byte = self.i2c.read_register(low_address)
            except I2CError as e:
                raise exceptions.ReadCurrentDutyCycleError(logger=self.logger) from e

        # Convert register byte to duty cycle
        duty_cycle = round(0.392 * register_byte, 1)

        # Return duty cycle
        self.logger.debug("Duty cycle: {}%".format(duty_cycle))
        return duty_cycle

    def write_current_duty_cycle(self, fan_id: int, duty_cycle: float) -> None:
        """Writes a current duty cycle for a fan."""

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Validate duty cycle
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError("Duty cycle must be a value between 0-100")

        # Convert duty cycle from float to byte
        duty_cycle_byte = int(duty_cycle / 0.392)

        # Write current duty cycle
        with self.i2c_lock:
            try:
                address = PWM_CURRENT_DUTY_CYCLE_BASE_REGISTER + fan_id
                self.i2c.write_register(address, duty_cycle_byte)
            except I2CError as e:
                raise exceptions.WriteCurrentDutyCycleError(logger=self.logger) from e

    def write_fan_pulses_per_revolution(
        self, fan_id: int, pulses_per_revolution: int
    ) -> None:
        """Writes the number of fan pulses per revolution for a fan."""

        # Validate fan id
        if fan_id < 0 or fan_id > 3:
            raise ValueError("Fan id must be a value between 0-3")

        # Validate duty cycle
        if pulses_per_revolution < 1 or pulses_per_revolution > 4:
            raise ValueError("Pulses per revolution must be a value between 1-4")

        # Read then write fan pulses register
        with self.i2c_lock:
            try:
                register_address = FAN_PULSES_PER_REVOLUTION_REGISTER
                register_byte = self.i2c.read_register(register_address)
                mask = 0xFF - (0x3 << (fan_id * 2))
                register_byte &= mask  # clear old value
                print("ppr: {}".format(pulses_per_revolution))
                register_byte |= (pulses_per_revolution - 1) << (
                    fan_id * 2
                )  # set new value
                self.i2c.write_register(register_address, register_byte)
            except I2CError as e:
                raise exceptions.WriteFanPulsesPerRevolutionError(
                    logger=self.logger
                ) from e

    def enable_monitoring(self, retry: bool = True) -> None:
        """Enables temperature monitoring."""
        self.logger.debug("Enabling monitoring")

        # Enable monitoring
        with self.i2c_lock:
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_1)
                register_byte |= 0x80
                self.i2c.write_register(CONFIG_REGISTER_1, register_byte)
            except I2CError as e:
                raise exceptions.EnableMonitoringError(logger=self.logger) from e

    def disable_monitoring(self, retry: bool = True) -> None:
        """Disables temperature monitoring."""
        self.logger.debug("Disabling monitoring")

        # Disable monitoring
        with self.i2c_lock:
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_1)
                register_byte &= 0x7F
                self.i2c.write_register(CONFIG_REGISTER_1, register_byte)
            except I2CError as e:
                raise exceptions.DisableMonitoringError(logger=self.logger) from e

    def enable_high_frequency_fan_drive(self, retry: bool = True) -> None:
        """Enables high frequency fan drive."""
        self.logger.debug("Enabling high frequency fan drive")

        # Enable monitoring
        with self.i2c_lock:
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_1)
                register_byte &= 0xBF
                self.i2c.write_register(CONFIG_REGISTER_1, register_byte)
            except I2CError as e:
                raise exceptions.EnableHighFrequencyFanDriveError(logger=self.logger) from e

    def enable_low_frequency_fan_drive(self, retry: bool = True) -> None:
        """Enables low frequency fan drive."""
        self.logger.debug("Enabling low frequency fan drive")

        # Enable monitoring
        with self.i2c_lock:
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_1)
                register_byte |= 0x40
                self.logger.debug('reg_byte: {}'.format(hex(register_byte)))
                self.i2c.write_register(CONFIG_REGISTER_1, register_byte)
            except I2CError as e:
                raise exceptions.EnableLowFrequencyFanDriveError(logger=self.logger) from e

    def read_temperature(self, sensor_id: int, retry: bool = True) -> float:
        """Reads a temperature sensor."""
        self.logger.debug("Reading temperature from sensor {}".format(sensor_id))

        # Validate sensor id
        if sensor_id < 0 or sensor_id > 9:
            raise ValueError("Sensor id must be a value between 0-9")

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:
            try:
                # Take temperature reading
                self.enable_monitoring()
                time.sleep(0.2)  # Wait 200 ms
                self.disable_monitoring()

                # Get temperature value
                register_address = TEMPERATURE_BASE_REGISTER + sensor_id
                temperature_byte = self.i2c.read_register(register_address)

                # Re-enable temperature monitoring
                self.enable_monitoring()
            except I2CError as e:
                raise exceptions.ReadTemperatureError(logger=self.logger) from e

            # Convert temperature byte to float
            if temperature_byte > 127:
                temperature = float(temperature_byte - 256)
            else:
                temperature = float(temperature_byte)

            # Return temperature value
            self.logger.debug("Temperature: {}".format(temperature))
            return temperature

    def read_maximum_temperature(self, retry: bool = True) -> float:
        """Reads the maximum temperature of all sensors."""
        self.logger.debug("Reading maximum temperature")

        with self.i2c_lock:
            try:
                # Read max temperature
                max_temperature_byte = self.i2c.read_register(
                    MAXIMUM_TEMPERATURE_REGISTER
                )
            except I2CError as e:
                raise exceptions.ReadMaximumTemperatureError(logger=self.logger) from e

        # Convert temperature byte to float
        if max_temperature_byte > 127:
            max_temperature = float(max_temperature_byte - 256)
        else:
            max_temperature = float(max_temperature_byte)

        # Return max temperature
        self.logger.debug("Max Temperature: {}".format(max_temperature))
        return max_temperature

    def read_fan_speed(self, fan_id: int) -> float:
        """Reads fan speed."""
        self.logger.debug("Reading fan speed for fan {}".format(fan_id))

        # Read tachometer
        with self.i2c_lock:
            try:
                low_address = TACHOMETER_BASE_REGISTER + 2 * fan_id
                high_address = low_address + 1
                low_byte = self.i2c.read_register(
                    low_address
                )  # low byte must be read first
                high_byte = self.i2c.read_register(
                    high_address
                )  # high byte freezes when low byte read
                tachometer_word = (high_byte << 8) + low_byte
                self.logger.debug("{}: {}".format(hex(low_address), hex(low_byte)))
                self.logger.debug("{}: {}".format(hex(high_address), hex(high_byte)))
                self.logger.debug("Word: {}".format(hex(tachometer_word)))
            except I2CError as e:
                raise exceptions.ReadTachometerError(logger=self.logger) from e

        # Convert bytes to float
        if tachometer_word == 0xFFFF:
            fan_speed_rpm = 0.0
        else:
            fan_speed_rpm = round(90000 * 60 / tachometer_word, 1)
        self.logger.debug("Fan Speed: {} RPM".format(fan_speed_rpm))
        return fan_speed_rpm

    def shutdown(self, retry: bool = True) -> None:
        """Shuts down peripheral."""
        self.logger.debug("Shutting down")

        # Shutdown peripheral
        with self.i2c_lock:
            try:
                register_byte = self.i2c.read_register(CONFIG_REGISTER_2)
                register_byte |= 0x01
                self.i2c.write_register(CONFIG_REGISTER_2, register_byte)
            except I2CError as e:
                raise exceptions.ShutdownError(logger=self.logger) from e
