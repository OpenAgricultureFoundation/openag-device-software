from device.peripherals.classes.peripheral.exceptions import DriverError


class GetCameraError(DriverError):  # type: ignore
    message_base = "Unable to get camera"


class EnableCameraError(DriverError):  # type: ignore
    message_base = "Unable to enable camera"


class DisableCameraError(DriverError):  # type: ignore
    message_base = "Unable to disable camera"


class CaptureError(DriverError):  # type: ignore
    message_base = "Unable to capture"


class CaptureImageError(DriverError):  # type: ignore
    message_base = "Unable to capture image"
