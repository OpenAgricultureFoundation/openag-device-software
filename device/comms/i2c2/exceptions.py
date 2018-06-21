class I2CError(Exception):
    """Base class for errors raised by I2C."""


class InitializationError(I2CError):
    """Exception raised for initialization errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class ReadError(I2CError):
    """Exception raised for read errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class WriteError(I2CError):
    """Exception raised for write errors.

    Attributes:
        message -- explanation of the error
        byte_list -- TODO
    """

    def __init__(self, message, byte_list):
        self.message = message
        self.byte_list = byte_list


class MuxError(I2CError):
    """Exception raised for write errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message, byte_list):
        self.message = message
