# Import standard python modules
import time
from typing import NamedTuple, Optional, Tuple

# Import device comms
# from device.comms.i2c import I2C
from device.comms.i2c2.main import I2C
from device.comms.i2c2.mux_simulator import MuxSimulator
from device.comms.i2c2.exceptions import I2CError

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import bitwise

# Import driver elements
from device.peripherals.modules.sht25.simulator import SHT25Simulator
from device.peripherals.modules.sht25.exceptions import (
    ReadTemperatureError,
    ReadHumidityError,
    ReadUserRegisterError,
    ResetError,
)


class UserRegister(NamedTuple):
    """ Dataclass for parsed user register byte. """
    resolution: int
    end_of_battery: bool
    heater_enabled: bool
    reload_disabled: bool


class SHT25Driver:
    """ Driver for atlas sht25 temperature and humidity sensor. """

    # Initialize variable properties
    _min_temperature = -40  # C
    _max_temperature = 125  # C
    _min_humidity = 0  # %RH
    _max_humidity = 100  # %RH

    def __init__(
        self,
        name: str,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: Optional[bool] = False,  # TODO: Remove this once no more legacy code
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """ Initializes sht25 driver. """

        # Initialize logger
        self.logger = Logger(name="Driver({})".format(name), dunder_name=__name__)

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = SHT25Simulator
        else:
            Simulator = None

        # Initialize I2C
        try:
            self.i2c = I2C(
                name=name,
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
        except I2CError as e:
            message = "Driver unable to initialize"
            raise InitError(message, logger=self.logger)

    def read_temperature(self, retry: bool = False) -> float:
        """ Reads temperature value from sensor hardware. """
        self.logger.debug("Reading temperature")

        # Send read temperature command (no-hold master)
        try:
            self.i2c.write(bytes([0xF3]), retry=retry)
        except I2CError as e:
            message = "Driver unable to read temperature"  # TODO: Make better error messages
            raise ReadTemperatureError(message, logger=self.logger) from e

        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max temperature processing time is 22ms
        time.sleep(0.22)

        # Read sensor data
        try:
            bytes_ = self.i2c.read(2, retry=retry)
        except I2CError as e:
            message = "Driver unable to read temperature"  # TODO: Make better error messages
            raise ReadTemperatureError(message, logger=self.logger) from e

        # Convert temperature data and set significant figures
        msb, lsb = bytes_
        raw = msb * 256 + lsb
        temperature = -46.85 + ((raw * 175.72) / 65536.0)
        temperature = float("{:.0f}".format(temperature))

        # Verify temperature value within valid range
        if temperature > self._min_temperature and temperature < self._min_temperature:
            self.logger.warning("Temperature outside of valid range")
            temperature = None

        # Successfully read temperature!
        self.logger.debug("Temperature: {} C".format(temperature))
        return temperature

    def read_humidity(self, retry: bool = False) -> float:
        """ Reads humidity value from sensor hardware. """
        self.logger.debug("Reading humidity value from hardware")

        # Send read humidity command (no-hold master)
        try:
            self.i2c.write(bytes([0xF5]), retry=retry)
        except I2CError as e:
            message = "Driver unable to read humidity"
            raise ReadHumidityError(message, logger=self.logger) from e

        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max humidity processing time is 29ms
        time.sleep(0.29)

        # Read sensor
        try:
            bytes_ = self.i2c.read(2, retry=retry)  # Read sensor data
        except I2CError as e:
            message = "Driver unable to read humidity"
            raise ReadHumidityError(message, logger=self.logger) from e

        # Convert humidity data and set significant figures
        msb, lsb = bytes_
        raw = msb * 256 + lsb
        humidity = -6 + ((raw * 125.0) / 65536.0)
        humidity = float("{:.0f}".format(humidity))

        # Verify humidity value within valid range
        if humidity > self._min_humidity and humidity < self._min_humidity:
            self.logger.warning("Humidity outside of valid range")
            humidity = None

        # Successfully read humidity!
        self.logger.debug("Humidity: {} %".format(humidity))
        return humidity

    def read_user_register(self, retry: bool = False) -> UserRegister:
        """ Reads user register from sensor hardware. """
        self.logger.debug("Reading user register")

        # Read register
        try:
            byte = self.i2c.read_register(0xE7, retry=retry)
        except I2CError as e:
            message = "Driver unable to read user register"
            raise ReadUserRegisterError(message, logger=self.logger) from e

        # Parse register content
        self.logger.debug("byte = 0x{:02X}".format(byte))
        resolution_msb = bitwise.get_bit_from_byte(bit=7, byte=byte)
        resolution_lsb = bitwise.get_bit_from_byte(bit=0, byte=byte)
        user_register = UserRegister(
            resolution=resolution_msb << 1 + resolution_lsb,
            end_of_battery=bool(bitwise.get_bit_from_byte(bit=6, byte=byte)),
            heater_enabled=bool(bitwise.get_bit_from_byte(bit=2, byte=byte)),
            reload_disabled=bool(bitwise.get_bit_from_byte(bit=1, byte=byte)),
        )

        # Successfully read user register!
        self.logger.debug("User register: {}".format(user_register))
        return user_register

    def reset(self, retry: bool = False) -> None:
        """ Initiates soft reset on sensor hardware. """
        self.logger.info("Initiating soft reset")

        # Send reset command
        try:
            self.i2c.write(bytes([0xFE]), retry=retry)
        except I2CError as e:
            message = "Driver unable to reset"
            raise ResetError(messsage, logger=self.logger) from e
