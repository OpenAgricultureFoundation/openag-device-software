class DriverError(Exception):
    """Base class for errors raised by driver."""


class InitError(DriverError):
    """Initialization errors for sensor driver.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class ReadTemperatureError(DriverError):
    """Exception raised for temperature read errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class ReadTemperatureError(DriverError):
    """Exception raised for temperature read errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class ReadHumidityError(DriverError):
    """Exception raised for humidity read errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class ReadUserRegisterError(DriverError):
    """Exception raised for user register read errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)


class ResetError(DriverError):
    """Exception raised for reset errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message, logger=None):
        self.message = message
        if logger != None:
            logger.error(message)
