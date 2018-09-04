# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


class StartAppError(DriverError):  # type: ignore
    message_base = "Unable to start app"


class HardwareIDError(DriverError):  # type: ignore
    message_base = "Invalid hardware ID"


class StatusError(DriverError):  # type: ignore
    message_base = "Device status error"


class ReadAlgorithmDataError(DriverError):  # type: ignore
    message_base = "Unable to read algorith data"


class ReadRegisterError(DriverError):  # type: ignore
    message_base = "Unable to read register"


class WriteRegisterError(DriverError):  # type: ignore
    message_base = "Unable to write register"


class WriteMeasurementModeError(DriverError):  # type: ignore
    message_base = "Unable to write measurement mode"


class ResetError(DriverError):  # type: ignore
    message_base = "Unable to reset"


class WriteEnvironmentDataError(DriverError):  # type: ignore
    message_base = "Unable to write environment data"
