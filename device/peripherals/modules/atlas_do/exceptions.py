from device.peripherals.classes.atlas import exceptions


SetupError = exceptions.SetupError


class ReadDOError(exceptions.DriverError):
    message_base = "Unable to read DO"


class EnableMgLOutputError(exceptions.DriverError):
    message_base = "Unable to enable DO mg/L output"


class DisableMgLOutputError(exceptions.DriverError):
    message_base = "Unable to disable DO mg/L output"


class EnablePercentSaturationOutputError(exceptions.DriverError):
    message_base = "Unable to enable percent saturation output"


class DisablePercentSaturationOutputError(exceptions.DriverError):
    message_base = "Unable to disable percent saturation output"


class SetCompensationECError(exceptions.DriverError):
    message_base = "Unable to set compensation EC"


class SetCompensationPressureError(exceptions.DriverError):
    message_base = "Unable to set compensation pressure"
