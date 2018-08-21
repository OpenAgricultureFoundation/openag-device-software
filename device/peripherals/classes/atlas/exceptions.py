from device.utilities.logger import Logger


class DriverError(Exception):
    """Base class for errors raised by driver."""

    def __init__(self, message: str, logger: Logger = None) -> None:
        self.message = message
        if logger != None:
            logger.error(message)


class InitError(DriverError):
    """Initialization errors for sensor driver."""
    ...


class ProcessCommandError(DriverError):
    """Process command errors for sensor driver."""
    ...


class ReadResponseError(DriverError):
    """Read response errors for sensor driver."""
    ...


class ReadInfoError(DriverError):
    """Read info errors for sensor driver."""
    ...


class ReadStatusError(DriverError):
    """Read status errors for sensor driver."""
    ...


class EnableProtocolLockError(DriverError):
    """Enable protocol lock errors for sensor driver."""
    ...


class DisableProtocolLockError(DriverError):
    """Disable protocol lock errors for sensor driver."""
    ...


class EnableLEDError(DriverError):
    """Enable led errors for sensor driver."""
    ...


class DisableLEDError(DriverError):
    """Disable led errors for sensor driver."""
    ...


class EnableSleepModeError(DriverError):
    """Enable sleep mode errors for sensor driver."""
    ...
