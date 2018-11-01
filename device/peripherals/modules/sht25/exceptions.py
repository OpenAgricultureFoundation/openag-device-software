from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class ReadTemperatureError(DriverError):  # type: ignore
    message_base = "Unable to read temperature"


class ReadHumidityError(DriverError):  # type: ignore
    message_base = "Unable to read humidity"


class ReadUserRegisterError(DriverError):  # type: ignore
    message_base = "Unable to read user register"


class ResetError(DriverError):  # type: ignore
    message_base = "Unable to reset"
