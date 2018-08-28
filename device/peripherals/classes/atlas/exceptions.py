# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


class ProcessCommandError(DriverError):
    message_base = "Unable to process command"


class ReadResponseError(DriverError):
    message_base = "Unable to read response"


class ReadInfoError(DriverError):
    message_base = "Unable to read info"


class ReadStatusError(DriverError):
    message_base = "Unable to read status"


class EnableProtocolLockError(DriverError):
    message_base = "Unable to enable protocol lock"


class DisableProtocolLockError(DriverError):
    message_base = "Unable to disable protocol lock"


class EnableLEDError(DriverError):
    message_base = "Unable to enable LED"


class DisableLEDError(DriverError):
    message_base = "Unable to disable LED"


class EnableSleepModeError(DriverError):
    message_base = "Unable to enable sleep mode"


class SetCompensationTemperatureError(DriverError):
    message_base = "Unable to set compensation temperature"


class TakeLowPointCalibrationError(DriverError):
    message_base = "Unable to take low point calibration reading"


class TakeMidPointCalibrationError(DriverError):
    message_base = "Unable to take mid point calibration reading"


class TakeHighPointCalibrationError(DriverError):
    message_base = "Unable to take high point calibration reading"


class ClearCalibrationError(DriverError):
    message_base = "Unable to clear calibration readings"


class FactoryResetError(DriverError):
    message_base = "Unable to perform factory reset"
