from device.peripherals.classes.atlas.exceptions import DriverError


class ReadECError(DriverError):
    message_base = "Unable to read ec"


class EnableECOutputError(DriverError):
    message_base = "Unable to enable ec output"


class DisableECOutputError(DriverError):
    message_base = "Unable to disable ec output"


class EnableTDSOutputError(DriverError):
    message_base = "Unable to enable TDS output"


class DisableTDSOutputError(DriverError):
    message_base = "Unable to disable TDS output"


class EnableSalinityOutputError(DriverError):
    message_base = "Unable to enable salinity output"


class DisableSalinityOutputError(DriverError):
    message_base = "Unable to disable salinity output"


class EnableSpecificGravityOutputError(DriverError):
    message_base = "Unable to enable specific gravity output"


class DisableSpecificGravityOutputError(DriverError):
    message_base = "Unable to disable specific gravity output"


class TakeDryCalibrationError(DriverError):
    message_base = "Unable to take dry calibration"


class TakeSinglePointCalibrationError(DriverError):
    message_base = "Unable to take single point calibration error"
