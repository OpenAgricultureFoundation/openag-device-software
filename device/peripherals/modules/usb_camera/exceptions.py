from device.utilities.exceptions import ExceptionLogger


class DriverError(ExceptionLogger):
    pass


class InitError(DriverError):
    message_base = "Unable to initialize"


class SetupError(DriverError):
    message_base = "Unable to setup"


class GetCameraError(DriverError):
    message_base = "Unable to get camera"


class EnableCameraError(DriverError):
    message_base = "Unable to enable camera"


class DisableCameraError(DriverError):
    message_base = "Unable to disable camera"


class CaptureError(DriverError):
    message_base = "Unable to capture"


class CaptureImageError(DriverError):
    message_base = "Unable to capture image"
