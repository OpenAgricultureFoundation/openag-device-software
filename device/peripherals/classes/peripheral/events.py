# Import python types
from typing import Dict, Tuple, Any

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.logger import Logger

# Initialize vars
RESET_EVENT = "Reset"
SHUTDOWN_EVENT = "Shutdown"
SET_SAMPLING_INTERVAL_EVENT = "Set Sampling Interval"
ENABLE_CALIBRATION_MODE_EVENT = "Enable Calibration Mode"
ENABLE_MANUAL_MODE_EVENT = "Enable Manual Mode"


class PeripheralEvents:
    """Event mixin for peripherals."""

    # Initialize parent class var types
    logger: Logger
    mode: str
    min_sampling_interval_seconds: float

    def process_event(self, request: Dict) -> Tuple[str, int]:
        """Processes an event. Returns response message and status."""
        self.logger.debug("Processing event request: `{}`".format(request))

        # Get request parameters
        try:
            request_type = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400

        # Process general event requests
        if request_type == RESET_EVENT:
            return self.process_reset_event()
        elif request_type == SHUTDOWN_EVENT:
            return self.process_shutdown_event()
        elif request_type == SET_SAMPLING_INTERVAL_EVENT:
            return self.process_set_sampling_interval_event(request)
        elif request_type == ENABLE_CALIBRATION_MODE_EVENT:
            return self.process_enable_calibration_mode_event()
        elif request_type == ENABLE_MANUAL_MODE_EVENT:
            return self.process_enable_manual_mode_event()
        else:
            return self.process_peripheral_specific_event(request)

    def process_reset_event(self) -> Tuple[str, int]:
        """Processes reset event."""
        self.logger.debug("Processing reset event")

        # Check sensor is in acceptible mode
        modes = [
            Modes.NORMAL, Modes.ERROR, Modes.CALIBRATE, Modes.SHUTDOWN, Modes.MANUAL
        ]
        if self.mode not in modes:
            message = "Unable to reset peripheral from {} mode".format(self.mode)
            self.logger.info(message)
            return message, 400

        # Transition to reset mode on next state machine update
        self.mode = Modes.RESET

        # Return event response
        return "Resetting", 200

    def process_shutdown_event(self) -> Tuple[str, int]:
        """Processes shutdown event."""
        self.logger.debug("Processing shutdown event")

        # Check sensor isn't already in shutdown mode
        if self.mode == Modes.SHUTDOWN:
            return "Already in shutdown mode", 200

        # Transition to shutdown mode on next state machine update
        self.mode = Modes.SHUTDOWN

        # Return event response
        return "Shutting down", 200

    def process_set_sampling_interval_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes shutdown event."""
        self.logger.debug("Processing set sampling interval event")

        # Verify value in request
        try:
            value = request["value"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.info(message)
            return message, 400

        # Check sensor is in acceptible mode
        valid_modes = [Modes.NORMAL, Modes.SHUTDOWN]
        if self.mode not in valid_modes:
            message = "Unable to set sampling interval from {} mode".format(self.mode)
            self.logger.info(message)
            return message, 400

        # Safely get desired sampling interval
        try:
            desired_sampling_interval_seconds = float(value)
        except ValueError:
            return "Invalid sampling interval value", 400

        # Check desired sampling interval larger than min interval
        if desired_sampling_interval_seconds < self.min_sampling_interval_seconds:
            message = "Unable to set sampling interval below {} seconds.".format(
                self.min_sampling_interval_seconds
            )
            self.logger.info(message)
            return message, 400

        # Set new sampling interval
        self.sampling_interval_seconds = desired_sampling_interval_seconds

        # Successfully set sampling interval
        return "Set sampling interval", 200

    def process_enable_calibration_mode_event(self) -> Tuple[str, int]:
        """Processes enable calibration mode event."""
        self.logger.debug("Processing enable calibration mode event")

        # Check if sensor alread in calibration mode
        if self.mode == Modes.CALIBRATE:
            return "Already in calibration mode", 200

        # Check sensor is in acceptible mode
        modes = [Modes.NORMAL, Modes.MANUAL]
        if self.mode not in modes:
            mode = self.mode.lower()
            message = "Unable to enable calibration mode from {} mode".format(mode)
            return message, 400

        # Enable calibration mode
        self.mode = Modes.CALIBRATE
        return "Enabling calibration mode", 200

    def process_enable_manual_mode_event(self) -> Tuple[str, int]:
        """Processes enable manual mode event."""
        self.logger.debug("Processing enable manual mode event")

        # Check if sensor alread in manual mode
        if self.mode == Modes.MANUAL:
            return "Already in manual mode", 200

        # Check sensor is in acceptible mode
        modes = [Modes.NORMAL, Modes.CALIBRATE]
        if self.mode not in modes:
            mode = self.mode.lower()
            message = "Unable to enable manual mode from {} mode".format(mode)
            return message, 400

        # Enable manual mode
        self.mode = Modes.MANUAL
        return "Enabling manual mode", 200

    def process_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event. This method should be overridden in 
        child class to handle child classes events."""
        return "Unknown event request type", 400
