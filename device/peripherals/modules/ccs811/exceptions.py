from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class StartAppError(DriverError):
    message_base = "Unable to start app"


class HardwareIDError(DriverError):
    message_base = "Invalid hardware ID"


class StatusError(DriverError):
    message_base = "Device status error"


class ReadAlgorithmDataError(DriverError):
    message_base = "Unable to read algorith data"


class ReadRegisterError(DriverError):
    message_base = "Unable to read register"


class WriteRegisterError(DriverError):
    message_base = "Unable to write register"


class WriteMeasurementModeError(DriverError):
    message_base = "Unable to write measurement mode"


class ResetError(DriverError):
    message_base = "Unable to reset"


class WriteEnvironmentDataError(DriverError):
    message_base = "Unable to write environment data"
