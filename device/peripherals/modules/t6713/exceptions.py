class DriverError(Exception):
    """Base class for errors raised by driver."""

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class InitError(DriverError):
    """Initialization errors for sensor driver."""
    ...


class SetupError(DriverError):
    """Setup errors for sensor driver."""
    ...


class ReadCo2Error(DriverError):
    """Read Co2 errors for sensor driver."""
    ...


class ReadStatusError(DriverError):
    """Read status errors for sensor driver."""
    ...


class EnableABCLogicError(DriverError):
    """Enable ABC logic errors for sensor driver."""
    ...


class DisableABCLogicError(DriverError):
    """Disable ABC logic errors for sensor driver."""
    ...


class ResetError(DriverError):
    """Reset errors for sensor driver."""
    ...
