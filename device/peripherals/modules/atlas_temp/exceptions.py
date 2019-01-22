from device.peripherals.classes.atlas import exceptions


SetupError = exceptions.SetupError


class ReadTemperatureError(exceptions.DriverError):
    message_base = "Unable to read temperature"


class EnableDataLoggerError(exceptions.DriverError):
    message_base = "Unable to enable data logger"


class DisableDataLoggerError(exceptions.DriverError):
    message_base = "Unable to disable data logger"


class SetTemperatureScaleCelciusError(exceptions.DriverError):
    message_base = "Unable to set temperature scale to celcius"


class SetTemperatureScaleFarenheitError(exceptions.DriverError):
    message_base = "Unable to set temperature scale to farenheit"


class SetTemperatureScaleKelvinError(exceptions.DriverError):
    message_base = "Unable to set temperature scale to kelvin"


class CalibrationError(exceptions.DriverError):
    message_base = "Unable to calibrate"
