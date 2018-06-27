# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class PeripheralEvents:
    """ Event mixin for peripherals. """

    def process_event(self, request):
        """ Processes an event. Gets request parameters, executes request, returns 
            response. """

        self.logger.debug("Processing event request: `{}`".format(request))

        # Get request parameters
        try:
            request_type = request["type"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            self.response = {
                "status": 400,
                "message": "Invalid request parameters: {}".format(e),
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

    def process_reset_event(self):
        """ Processes reset event. """
        self.logger.debug("Processing reset event")

        # Check sensor is in normal, error, or calibration mode
        if (
            (self.mode != Modes.NORMAL)
            and (self.mode != Modes.ERROR)
            and (self.mode != Modes.CALIBRATE)
            and (self.mode != Modes.SHUTDOWN)
        ):
            error_message = "Unable to reset peripheral from {} mode!".format(self.mode)
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}

        # Transition to reset mode on next state machine update
        self.mode = Modes.RESET

        # Return event response
        response = {"status": 200, "message": "Resetting!"}
        return response

    def process_shutdown_event(self):
        """ Processes shutdown event. """
        self.logger.debug("Processing shutdown event")

        # Check sensor isn't already in shutdown mode
        if self.mode == Modes.SHUTDOWN:
            error_message = "Device already in shutdown mode!"
            self.logger.info(error_message)
            response = {"status": 200, "message": error_message}

        # Transition to shutdown mode on next state machine update
        self.mode = Modes.SHUTDOWN

        # Return event response
        response = {"status": 200, "message": "Shutting down!"}
        return response

    def process_set_sampling_interval_event(self, request):
        """ Processes shutdown event. """
        self.logger.debug("Processing set sampling interval event")

        # Verify value in request
        try:
            value = request["value"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            self.response = {
                "status": 400,
                "message": "Invalid request parameters: {}".format(e),
            }

        # Check sensor is in normal or shutdown mode
        if (self.mode != Modes.NORMAL) and (self.mode != Modes.SHUTDOWN):
            error_message = "Unable to set sampling interval from {} mode!".format(
                self.mode
            )
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}

        # Safely get desired sampling interval
        try:
            desired_sampling_interval_seconds = float(value)
        except ValueError:
            response = {"status": 400, "message": "Invalid sampling interval value!"}
            return response

        # Check desired sampling interval larger than min interval
        if desired_sampling_interval_seconds < self._min_sampling_interval_seconds:
            error_message = "Unable to set sampling interval below {} seconds.".format(
                self._min_sampling_interval_seconds
            )
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}

        # Set new sampling interval
        self.sampling_interval_seconds = desired_sampling_interval_seconds

        # Return event response
        response = {"status": 200, "message": "Set sampling interval!"}
        return response

    def process_enable_calibration_mode_event(self):
        """ Processes enable calibration mode event. """
        self.logger.debug("Processing enable calibration mode event")

        # TODO: Verify transition from valid mode

        if self.mode == Modes.CALIBRATE:
            response = {"status": 200, "message": "Already in calibration mode!"}
        else:
            self.mode = Modes.CALIBRATE
            response = {"status": 200, "message": "Enabling calibration mode!"}
        return response

    def process_enable_manual_mode_event(self):
        """ Processes enable manual mode event. """
        self.logger.debug("Processing enable manual mode event")

        # TODO: Verfiy transition from valid mode

        if self.mode == Modes.MANUAL:
            response = {"status": 200, "message": "Already in manual mode!"}
        else:
            self.mode = Modes.MANUAL
            response = {"status": 200, "message": "Enabling manual mode!"}
        return response

    def process_peripheral_specific_event(self, request):
        """ Processes peripheral specific event. """

        # Execute request
        if False:  # New event condition goes here
            ...
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}
