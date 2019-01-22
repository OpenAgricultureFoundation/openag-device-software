# Import driver error base class
from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class GetPortByteError(DriverError):
    message_base = "Unable to get port byte"


class SetHighError(DriverError):
    message_base = "Unable to set high"


class SetLowError(DriverError):
    message_base = "Unable to set low"
