# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


class ProcessCommandError(DriverError):  # type: ignore
    message_base = "Unable to process command"


class ReadResponseError(DriverError):  # type: ignore
    message_base = "Unable to read response"


class ReadInfoError(DriverError):  # type: ignore
    message_base = "Unable to read info"


class ReadStatusError(DriverError):  # type: ignore
    message_base = "Unable to read status"


class EnableProtocolLockError(DriverError):  # type: ignore
    message_base = "Unable to enable protocol lock"


class DisableProtocolLockError(DriverError):  # type: ignore
    message_base = "Unable to disable protocol lock"


class EnableLEDError(DriverError):  # type: ignore
    message_base = "Unable to enable LED"


class DisableLEDError(DriverError):  # type: ignore
    message_base = "Unable to disable LED"


class EnableSleepModeError(DriverError):  # type: ignore
    message_base = "Unable to enable sleep mode"


class SetCompensationTemperatureError(DriverError):  # type: ignore
    message_base = "Unable to set compensation temperature"


class TakeLowPointCalibrationError(DriverError):  # type: ignore
    message_base = "Unable to take low point calibration reading"


class TakeMidPointCalibrationError(DriverError):  # type: ignore
    message_base = "Unable to take mid point calibration reading"


class TakeHighPointCalibrationError(DriverError):  # type: ignore
    message_base = "Unable to take high point calibration reading"


class ClearCalibrationError(DriverError):  # type: ignore
    message_base = "Unable to clear calibration readings"


class FactoryResetError(DriverError):  # type: ignore
    message_base = "Unable to perform factory reset"
