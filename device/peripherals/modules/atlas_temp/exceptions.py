from device.peripherals.classes.atlas.exceptions import DriverError


class ReadTemperatureError(DriverError):  # type: ignore
    message_base = "Unable to read temperature"


class EnableDataLoggerError(DriverError):  # type: ignore
    message_base = "Unable to enable data logger"


class DisableDataLoggerError(DriverError):  # type: ignore
    message_base = "Unable to disable data logger"


class SetTemperatureScaleCelciusError(DriverError):  # type: ignore
    message_base = "Unable to set temperature scale to calcius"


class SetTemperatureScaleFarenheitError(DriverError):  # type: ignore
    message_base = "Unable to set temperature scale to farenheit"


class SetTemperatureScaleKelvinError(DriverError):  # type: ignore
    message_base = "Unable to set temperature scale to kelvin"


class CalibrationError(DriverError):  # type: ignore
    message_base = "Unable to calibrate"
