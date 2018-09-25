# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


class WriteOutputError(DriverError):  # type: ignore
    message_base = "Unable to write output"


class WriteOutputsError(DriverError):  # type: ignore
    message_base = "Unable to write outputs"


class ReadPowerRegisterError(DriverError):  # type: ignore
    message_base = "Unable to read power register"


class SetHighError(DriverError):  # type: ignore
    message_base = "Unable to set high"


class SetLowError(DriverError):  # type: ignore
    message_base = "Unable to set low"
