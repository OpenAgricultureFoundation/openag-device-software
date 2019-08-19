# Import driver error base class
from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class ReadVersionError(DriverError):
    message_base = "Unable to read version"


class EnableManualFanControlError(DriverError):
    message_base = "Unable to enable manual fan control"


class EnableAutomaticFanControlError(DriverError):
    message_base = "Unable to enable automatic fan control"


class EnableMonitoringError(DriverError):
    message_base = "Unable to enable monitoring"


class DisableMonitoringError(DriverError):
    message_base = "Unable to disable monitoring"


class ShutdownError(DriverError):
    message_base = "Unable to power down"


class ReadTemperatureError(DriverError):
    message_base = "Unable to read temperature"


class ReadMaxTemperatureError(DriverError):
    message_base = "Unable to read max temperature"


class WriteTemperatureLimitsError(DriverError):
    message_base = "Unable to write temperature limits"
