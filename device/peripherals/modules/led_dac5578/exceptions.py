# Import driver error base class
from device.peripherals.classes.peripheral.exceptions import DriverError


class NoActivePanelsError(DriverError):  # type: ignore
    message_base = "No active panels"


class SetSPDError(DriverError):  # type: ignore
    message_base = "Unable to set SPD"


class TurnOnError(DriverError):  # type: ignore
    message_base = "Unable to turn on"


class TurnOffError(DriverError):  # type: ignore
    message_base = "Unable to turn off"


class SetOutputError(DriverError):  # type: ignore
    message_base = "Unable to set output"


class SetOutputsError(DriverError):  # type: ignore
    message_base = "Unable to set outputs"


class InvalidChannelNameError(DriverError):  # type: ignore
    message_base = "Invalid channel name"
