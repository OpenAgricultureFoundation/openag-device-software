# Import python types
from typing import Optional

# Import device utilities
from device.utilities.logger import Logger


class I2CError(Exception):
    """Base class for errors raised by I2C."""

    def __init__(self, message: str, logger: Optional[Logger] = None) -> None:
        self.message = message
        if logger != None:
            logger.error(message)  # type: ignore


class InitError(I2CError):
    pass


class ReadError(I2CError):
    pass


class WriteError(I2CError):
    pass


class MuxError(I2CError):
    pass
