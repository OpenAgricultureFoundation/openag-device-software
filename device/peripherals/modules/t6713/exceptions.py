# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


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
