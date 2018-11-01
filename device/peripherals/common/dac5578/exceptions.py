# Import driver error base class
from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class WriteOutputError(DriverError):
    message_base = "Unable to write output"


class WriteOutputsError(DriverError):
    message_base = "Unable to write outputs"


class ReadPowerRegisterError(DriverError):
    message_base = "Unable to read power register"


class SetHighError(DriverError):
    message_base = "Unable to set high"


class SetLowError(DriverError):
    message_base = "Unable to set low"
