from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class ReadTemperatureError(DriverError):  # type: ignore
    message_base = "Unable to read temperature"


class ReadMoistureError(DriverError):  # type: ignore
    message_base = "Unable to read moisture"


class BadMoistureReading(DriverError):
    message_base = "Moisture reading out of bounds"


class ReadHwIdError(DriverError):  # type: ignore
    message_base = "Unable to read hardware id"


class ResetError(DriverError):  # type: ignore
    message_base = "Unable to reset"
