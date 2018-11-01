from device.peripherals.classes.atlas import exceptions


SetupError = exceptions.SetupError


class ReadECError(exceptions.DriverError):
    message_base = "Unable to read ec"


class EnableECOutputError(exceptions.DriverError):
    message_base = "Unable to enable ec output"


class DisableECOutputError(exceptions.DriverError):
    message_base = "Unable to disable ec output"


class EnableTDSOutputError(exceptions.DriverError):
    message_base = "Unable to enable TDS output"


class DisableTDSOutputError(exceptions.DriverError):
    message_base = "Unable to disable TDS output"


class EnableSalinityOutputError(exceptions.DriverError):
    message_base = "Unable to enable salinity output"


class DisableSalinityOutputError(exceptions.DriverError):
    message_base = "Unable to disable salinity output"


class EnableSpecificGravityOutputError(exceptions.DriverError):
    message_base = "Unable to enable specific gravity output"


class DisableSpecificGravityOutputError(exceptions.DriverError):
    message_base = "Unable to disable specific gravity output"


class SetProbeTypeError(exceptions.DriverError):
    message_base = "Unable to set probe type"


class TakeDryCalibrationError(exceptions.DriverError):
    message_base = "Unable to take dry calibration"


class TakeSinglePointCalibrationError(exceptions.DriverError):
    message_base = "Unable to take single point calibration"
