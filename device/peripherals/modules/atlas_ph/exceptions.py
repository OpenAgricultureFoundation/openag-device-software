from device.peripherals.classes.atlas import exceptions


SetupError = exceptions.SetupError


class ReadPHError(exceptions.DriverError):
    message_base = "Unable to read pH"
