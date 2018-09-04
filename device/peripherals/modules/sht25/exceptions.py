# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


class ReadTemperatureError(DriverError):  # type: ignore
    message_base = "Unable to read temperature"


class ReadHumidityError(DriverError):  # type: ignore
    message_base = "Unable to read humidity"


class ReadUserRegisterError(DriverError):  # type: ignore
    message_base = "Unable to read user register"


class ResetError(DriverError):  # type: ignore
    message_base = "Unable to reset"
