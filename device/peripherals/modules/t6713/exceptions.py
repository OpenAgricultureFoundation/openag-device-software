from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class ReadCo2Error(DriverError):  # type: ignore
    message_base = "Unable to read co2"


class ReadStatusError(DriverError):  # type: ignore
    message_base = "Unable to read status"


class EnableABCLogicError(DriverError):  # type: ignore
    message_base = "Unable to enable ABC logic"


class DisableABCLogicError(DriverError):  # type: ignore
    message_base = "Unable to disable ABC logic"


class ResetError(DriverError):  # type: ignore
    message_base = "Unable to reset"
