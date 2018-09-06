from device.peripherals.classes.atlas.exceptions import DriverError


class ReadDOError(DriverError):  # type: ignore
    message_base = "Unable to read DO"


class EnableMgLOutputError(DriverError):  # type: ignore
    message_base = "Unable to enable DO mg/L output"


class DisableMgLOutputError(DriverError):  # type: ignore
    message_base = "Unable to disable DO mg/L output"


class EnablePercentSaturationOutputError(DriverError):  # type: ignore
    message_base = "Unable to enable percent saturation output"


class DisablePercentSaturationOutputError(DriverError):  # type: ignore
    message_base = "Unable to disable percent saturation output"


class SetCompensationECError(DriverError):  # type: ignore
    message_base = "Unable to set compensation EC"


class SetCompensationPressureError(DriverError):  # type: ignore
    message_base = "Unable to set compensation pressure"
