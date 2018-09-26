from device.peripherals.classes.atlas.exceptions import DriverError


class ReadECError(DriverError):  # type: ignore
    message_base = "Unable to read ec"


class EnableECOutputError(DriverError):  # type: ignore
    message_base = "Unable to enable ec output"


class DisableECOutputError(DriverError):  # type: ignore
    message_base = "Unable to disable ec output"


class EnableTDSOutputError(DriverError):  # type: ignore
    message_base = "Unable to enable TDS output"


class DisableTDSOutputError(DriverError):  # type: ignore
    message_base = "Unable to disable TDS output"


class EnableSalinityOutputError(DriverError):  # type: ignore
    message_base = "Unable to enable salinity output"


class DisableSalinityOutputError(DriverError):  # type: ignore
    message_base = "Unable to disable salinity output"


class EnableSpecificGravityOutputError(DriverError):  # type: ignore
    message_base = "Unable to enable specific gravity output"


class DisableSpecificGravityOutputError(DriverError):  # type: ignore
    message_base = "Unable to disable specific gravity output"


class SetProbeTypeError(DriverError):  # type: ignore
    message_base = "Unable to set probe type"


class TakeDryCalibrationError(DriverError):  # type: ignore
    message_base = "Unable to take dry calibration"


class TakeSinglePointCalibrationError(DriverError):  # type: ignore
    message_base = "Unable to take single point calibration"
