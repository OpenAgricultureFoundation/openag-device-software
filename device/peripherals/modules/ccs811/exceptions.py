# from device.peripherals.modules.ccs811.driver import StatusRegister


class DriverError(Exception):
    """Base class for errors raised by driver."""

    def __init__(self, message: str, logger=None) -> None:
        self.message = message
        if logger != None:
            logger.error(message)


class InitError(DriverError):
    """Exception rasied for initialization errors."""
    ...


class SetupError(DriverError):
    """Exception raised for setup errors."""
    ...


class StatusError(DriverError):
    """Exception raised for write measurement mode errors."""

    def __init__(self, message: str, status, logger=None) -> None:
        self.message = message
        self.status = status
        if logger != None:
            logger.error(message)
            logger.debug(status)


class ReadAlgorithmDataError(DriverError):
    """Exception raised for read algorithm data errors."""
    ...


class ReadRegisterError(DriverError):
    """Exception raised for read register errors."""
    ...


class WriteRegisterError(DriverError):
    """Exception raised for write register errors."""
    ...


class WriteMeasurementModeError(DriverError):
    """Exception raised for write measurement mode errors."""
    ...
