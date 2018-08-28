from device.peripherals.classes.atlas.exceptions import DriverError


class ReadPHError(DriverError):
    message_base = "Unable to read pH"
