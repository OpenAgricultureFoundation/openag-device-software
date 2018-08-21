from device.peripherals.classes.atlas.exceptions import DriverError as AtlasDriverError


class DriverError(AtlasDriverError):
    """Base class for errors raised by driver."""
    ...


class InitError(DriverError):
    """Initialization errors for sensor driver."""
    ...


class SetupError(DriverError):
    """Setup errors for sensor driver."""
    ...


class ReadPHError(DriverError):
    """Read pH errors for sensor driver."""
    ...


class SetCompensationTemperatureError(DriverError):
    """Set compensation temperature errors for sensor driver."""
    ...


class TakeCalibrationError(DriverError):
    """Take calibration errors for sensor driver."""
    ...


class ClearCalibrationError(DriverError):
    """Clear calibration errors for sensor driver."""
    ...
