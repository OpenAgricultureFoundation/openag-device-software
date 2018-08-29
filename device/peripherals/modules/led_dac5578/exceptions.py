# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


class TurnOnError(DriverError):  # type: ignore
    message_base = "Unable to turn on"


class TurnOffError(DriverError):  # type: ignore
    message_base = "Unable to turn off"
