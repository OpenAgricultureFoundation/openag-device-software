# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Tuple

# Import device utilities
from device.utilities import logger, bitwise
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.modules.sht25 import simulator, exceptions


class UserRegister(NamedTuple):
    """Dataclass for parsed user register byte."""

    resolution: int
    end_of_battery: bool
    heater_enabled: bool
    reload_disabled: bool


class SHT25Driver:
    """Driver for sht25 temperature and humidity sensor."""

    # Initialize variable properties
    min_temperature = -40  # celsius
    max_temperature = 125  # celsius
    min_humidity = 0  # %RH
    max_humidity = 100  # %RH

    def __init__(
        self,
        name: str,
        i2c_lock: threading.RLock,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: Optional[bool] = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes driver."""

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = simulator.SHT25Simulator
        else:
            Simulator = None

        # Initialize I2C
        try:
            self.i2c = I2C(
                name=name,
                i2c_lock=i2c_lock,
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
                verify_device=False,  # need to write before device responds to read
            )
            self.read_user_register(retry=True)

        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

    def read_temperature(self, retry: bool = True) -> Optional[float]:
        """ Reads temperature value."""
        self.logger.debug("Reading temperature")

        # Send read temperature command (no-hold master)
        try:
            self.i2c.write(bytes([0xF3]), retry=retry)
        except I2CError as e:
            raise exceptions.ReadTemperatureError(logger=self.logger) from e

        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max temperature processing time is 22ms
        time.sleep(0.22)

        # Read sensor data
        try:
            bytes_ = self.i2c.read(2, retry=retry)
        except I2CError as e:
            raise exceptions.ReadTemperatureError(logger=self.logger) from e

        # Convert temperature data and set significant figures
        msb, lsb = bytes_
        raw = msb * 256 + lsb
        temperature = float(-46.85 + ((raw * 175.72) / 65536.0))
        temperature = float("{:.0f}".format(temperature))

        # Verify temperature value within valid range
        if temperature > self.min_temperature and temperature < self.min_temperature:
            self.logger.warning("Temperature outside of valid range")
            return None

        # Successfully read temperature
        self.logger.debug("Temperature: {} C".format(temperature))
        return temperature

    def read_humidity(self, retry: bool = True) -> Optional[float]:
        """Reads humidity value."""
        self.logger.debug("Reading humidity value from hardware")

        # Send read humidity command (no-hold master)
        try:
            self.i2c.write(bytes([0xF5]), retry=retry)
        except I2CError as e:
            raise exceptions.ReadHumidityError(logger=self.logger) from e

        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max humidity processing time is 29ms
        time.sleep(0.29)

        # Read sensor
        try:
            bytes_ = self.i2c.read(2, retry=retry)  # Read sensor data
        except I2CError as e:
            raise exceptions.ReadHumidityError(logger=self.logger) from e

        # Convert humidity data and set significant figures
        msb, lsb = bytes_
        raw = msb * 256 + lsb
        humidity = float(-6 + ((raw * 125.0) / 65536.0))
        humidity = float("{:.0f}".format(humidity))

        # Verify humidity value within valid range
        if humidity > self.min_humidity and humidity < self.min_humidity:
            self.logger.warning("Humidity outside of valid range")
            return None

        # Successfully read humidity
        self.logger.debug("Humidity: {} %".format(humidity))
        return humidity

    def read_user_register(self, retry: bool = True) -> UserRegister:
        """ Reads user register."""
        self.logger.debug("Reading user register")

        # Read register
        try:
            byte = self.i2c.read_register(0xE7, retry=retry)
        except I2CError as e:
            raise exceptions.ReadUserRegisterError(logger=self.logger) from e

        # Parse register content
        resolution_msb = bitwise.get_bit_from_byte(bit=7, byte=byte)
        resolution_lsb = bitwise.get_bit_from_byte(bit=0, byte=byte)
        user_register = UserRegister(
            resolution=resolution_msb << 1 + resolution_lsb,
            end_of_battery=bool(bitwise.get_bit_from_byte(bit=6, byte=byte)),
            heater_enabled=bool(bitwise.get_bit_from_byte(bit=2, byte=byte)),
            reload_disabled=bool(bitwise.get_bit_from_byte(bit=1, byte=byte)),
        )

        # Successfully read user register
        self.logger.debug("User register: {}".format(user_register))
        return user_register

    def reset(self, retry: bool = True) -> None:
        """Initiates soft reset."""
        self.logger.info("Initiating soft reset")

        # Send reset command
        try:
            self.i2c.write(bytes([0xFE]), retry=retry)
        except I2CError as e:
            raise exceptions.ResetError(logger=self.logger) from e
