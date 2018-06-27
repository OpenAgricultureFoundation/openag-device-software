from logging import LoggerAdapter
from typing import Optional


class I2CError(Exception):
    """Base class for errors raised by I2C."""

    def __init__(self, message: str, logger: Optional[LoggerAdapter] = None) -> None:
        self.message = message
        if logger != None:
            logger.error(message)  # type: ignore


class InitError(I2CError):
    """Exception raised for initialization errors."""

    ...


class ReadError(I2CError):
    """Exception raised for read errors."""

    ...


class WriteError(I2CError):
    """Exception raised for write errors."""

    ...


class MuxError(I2CError):
    """Exception raised for write errors."""

    ...
