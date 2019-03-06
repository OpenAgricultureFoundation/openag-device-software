from device.peripherals.classes.atlas import exceptions


SetupError = exceptions.SetupError


class ReadTemperatureError(exceptions.DriverError):
    message_base = "Unable to read temperature"


class EnableDataLoggerError(exceptions.DriverError):
    message_base = "Unable to enable data logger"


class DisableDataLoggerError(exceptions.DriverError):
    message_base = "Unable to disable data logger"


class SetTemperatureScaleCelsiusError(exceptions.DriverError):
    message_base = "Unable to set temperature scale to celsius"


class SetTemperatureScaleFarenheitError(exceptions.DriverError):
    message_base = "Unable to set temperature scale to farenheit"


class SetTemperatureScaleKelvinError(exceptions.DriverError):
    message_base = "Unable to set temperature scale to kelvin"


class CalibrationError(exceptions.DriverError):
    message_base = "Unable to calibrate"
