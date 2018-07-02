class DriverError(Exception):
    """Base class for errors raised by driver."""

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class InitError(DriverError):
    """Initialization errors for sensor driver."""

    ...


class ReadCo2Error(DriverError):
    """Read co2 errors for sensor driver."""

    ...


class ReadRegisterError(DriverError):
    """Exception raised for register read errors."""

    ...


class ReadAlgorithmDataError(DriverError):
    """Exception raised for read algorithm data errors."""

    ...


class WriteMeasurementModeError(DriverError):
    """Exception raised for write measurement mode errors."""

    ...


class WriteEnvironmentDataError(DriverError):
    """Exception raised for write environment data errors."""

    ...


class ResetError(DriverError):
    """Exception raised for reset errors."""

    ...
