# Import python types
from typing import Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.logger import Logger


class PeripheralEvents:
   """Event mixin for peripherals."""

    # Initialize parent class var types
    logger: Logger
    mode: str
    min_sampling_interval_seconds: float

    def process_event(self, request: Dict) -> None:
       """Processes an event. Gets request parameters, executes request, returns 
        response."""

        self.logger.debug("Processing event request: `{}`".format(request))

        # Get request parameters
        try:
            request_type = request["type"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            self.response = {
                "status": 400, "message": "Invalid request parameters: {}".format(e)
            }

        # Process general event requests
        if request_type == "Reset":
            self.response = self.process_reset_event()
        elif request_type == "Shutdown":
            self.response = self.process_shutdown_event()
        elif request_type == "Set Sampling Interval":
            self.response = self.process_set_sampling_interval_event(request)
        elif request_type == "Enable Calibration Mode":
            self.response = self.process_enable_calibration_mode_event()
        elif request_type == "Enable Manual Mode":
            self.response = self.process_enable_manual_mode_event()
        else:
            # Process peripheral specific requests
            self.process_peripheral_specific_event(request)

    def process_reset_event(self) -> Dict:
       """Processes reset event."""
        self.logger.debug("Processing reset event")

        # Check sensor is in acceptible mode
        modes = [Modes.NORMAL, Modes.ERROR, Modes.CALIBRATE, Modes.SHUTDOWN]
        if self.mode not in modes:
            message = "Unable to reset peripheral from {} mode!".format(self.mode)
            self.logger.info(message)
            return {"status": 400, "message": message}

        # Transition to reset mode on next state machine update
        self.mode = Modes.RESET

        # Return event response
        return {"status": 200, "message": "Resetting!"}

    def process_shutdown_event(self) -> Dict:
       """Processes shutdown event."""
        self.logger.debug("Processing shutdown event")

        # Check sensor isn't already in shutdown mode
        if self.mode == Modes.SHUTDOWN:
            message = "Device already in shutdown mode"
            self.logger.info(message)
            return {"status": 200, "message": message}

        # Transition to shutdown mode on next state machine update
        self.mode = Modes.SHUTDOWN

        # Return event response
        return {"status": 200, "message": "Shutting down"}

    def process_set_sampling_interval_event(self, request: Dict) -> Dict:
       """Processes shutdown event."""
        self.logger.debug("Processing set sampling interval event")

        # Verify value in request
        try:
            value = request["value"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.info(message)
            return {"status": 400, "message": message}

        # Check sensor is in acceptible mode
        modes = [Modes.NORMAL, Modes.SHUTDOWN]
        if self.mode not in modes:
            message = "Unable to set sampling interval from {} mode".format(self.mode)
            self.logger.info(message)
            return {"status": 400, "message": message}

        # Safely get desired sampling interval
        try:
            desired_sampling_interval_seconds = float(value)
        except ValueError:
            return {"status": 400, "message": "Invalid sampling interval value"}

        # Check desired sampling interval larger than min interval
        if desired_sampling_interval_seconds < self.min_sampling_interval_seconds:
            message = "Unable to set sampling interval below {} seconds.".format(
                self.min_sampling_interval_seconds
            )
            self.logger.info(message)
            return {"status": 400, "message": message}

        # Set new sampling interval
        self.sampling_interval_seconds = desired_sampling_interval_seconds

        # Successfully set sampling interval
        return {"status": 200, "message": "Set sampling interval"}

    def process_enable_calibration_mode_event(self) -> Dict:
       """Processes enable calibration mode event."""
        self.logger.debug("Processing enable calibration mode event")

        # Check if sensor alread in calibration mode
        if self.mode == Modes.CALIBRATE:
            return {"status": 200, "message": "Already in calibration mode"}

        # Check sensor is in acceptible mode
        modes = [Modes.NORMAL, Modes.MANUAL]
        if self.mode not in modes:
            mode = self.mode.lower()
            message = "Unable to enable calibration mode from {} mode".format(mode)
            return {"status": 400, "message": message}

        # Enable calibration mode
        self.mode = Modes.CALIBRATE
        return {"status": 200, "message": "Enabling calibration mode"}

    def process_enable_manual_mode_event(self) -> Dict:
       """Processes enable manual mode event."""
        self.logger.debug("Processing enable manual mode event")

        # Check if sensor alread in manual mode
        if self.mode == Modes.MANUAL:
            return {"status": 200, "message": "Already in manual mode"}

        # Check sensor is in acceptible mode
        modes = [Modes.NORMAL, Modes.CALIBRATE]
        if self.mode not in modes:
            mode = self.mode.lower()
            message = "Unable to enable manual mode from {} mode".format(mode)
            return {"status": 400, "message": message}

        # Enable manual mode
        self.mode = Modes.MANUAL
        return {"status": 200, "message": "Enabling manual mode"}

    def process_peripheral_specific_event(self, request: Dict) -> None:
       """Processes peripheral specific event. This method should be overridden in 
        child class to handle child classes events."""

        message = "Unknown event request type!"
        self.logger.info(message)
        self.response = {"status": 400, "message": message}
