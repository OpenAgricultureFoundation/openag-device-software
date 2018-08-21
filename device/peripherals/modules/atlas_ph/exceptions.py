class DriverError(Exception):
    """Base class for errors raised by driver."""

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class InitError(DriverError):
    """Initialization errors for sensor driver."""
    ...


# class SetupError(DriverError):
#     """Setup errors for sensor driver."""
#     ...


class ReadInfoError(DriverError):
    """Read info errors for sensor driver."""
    ...


class ReadStatusError(DriverError):
    """Read status errors for sensor driver."""
    ...


class ResetError(DriverError):
    """Reset errors for sensor driver."""
    ...
