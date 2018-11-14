from device.peripherals.classes.atlas import exceptions


SetupError = exceptions.SetupError


class ReadCo2Error(exceptions.DriverError):
    message_base = "Unable to read co2"


class ReadInternalTemperatureError(exceptions.DriverError):
    message_base = "Unable to read temperature"


class EnableInternalTemperatureError(exceptions.DriverError):
    message_base = "Unable to enable internal temperature"


class DisableInternalTemperatureError(exceptions.DriverError):
    message_base = "Unable to disable internal temperature"


class EnableAlarmError(exceptions.DriverError):
    message_base = "Unable to enable alarm"


class DisableAlarmError(exceptions.DriverError):
    message_base = "Unable to disable alarm"
