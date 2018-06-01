# Import standard python modules
from typing import Optional, Tuple, List, Dict
import time

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.peripheral_events import PeripheralEventMixin


class EventMixin(PeripheralEventMixin):
    """ Event mixin for led array. """


    def process_peripheral_specific_event(self, request):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        # Execute request
        if request["type"] == "Enable Calibration Mode":
            self.response = self.process_enable_calibration_mode_event()
        elif request["type"] == "Dry Calibration":
            self.response = self.process_dry_calibration_event()
        elif request["type"] == "Single Point Calibration":
            self.response = self.process_single_point_calibration_event(request)
        elif request["type"] == "Low Point Calibration":
            self.response = self.process_low_point_calibration_event(request)
        elif request["type"] == "High Point Calibration":
            self.response = self.process_high_point_calibration_event(request)
        elif request["type"] == "Clear Calibration":
            self.response = self.process_clear_calibration_event()
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


    def process_enable_calibration_mode_event(self):
        """ Processes calibrate event. """
        self.logger.debug("Processing enable calibration mode event")

        if self.mode == Modes.CALIBRATE:
            response = {"status": 200, "message": "Already in calibration mode!"}
        else:
            self.mode = Modes.CALIBRATE
            response = {"status": 200, "message": "Enabling calibration mode!"}
        return response


    def process_dry_calibration_event(self):
        """ Processes dry calibration event. Verifies sensor in calibrate mode,
            then takes dry calibration reading. """
        self.logger.debug("Processing dry calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take dry calibration!"}
            return response

        # Execute request
        try:
            self.take_dry_calibration_reading()
            response = {"status": 200, "message": "Successfully took dry calibration reading!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take dry calibration reading!")
            response = {"status": 500, "message": "Unable to take dry calibration reading: {}".format(e)}
            return response


    def process_single_point_calibration_event(self, request):
        """ Processes single point calibration event. Gets request parameters,
            executes request, returns response. """
        self.logger.debug("Processing single point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!."}
            return response

        # Execute request
        try:
            self.take_single_point_calibration_reading(value)
            response = {"status": 200, "message": "Set single point calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take single point calibration reading")
            response = {"status": 500, "message": "Unable to take single point calibration reading: {}!".format(e)}
            return response


    def process_low_point_calibration_event(self, request):
        """ Processes low point calibration event. Gets request parameters,
            executes request, returns response. """
        self.logger.debug("Processing low point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take low point calibration!."}
            return response

        # Execute request
        try:
            self.take_low_point_calibration_reading(value)
            response = {"status": 200, "message": "Set low point calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take low point calibration reading")
            response = {"status": 500, "message": "Unable to take low point calibration reading: {}!".format(e)}
            return response


    def process_high_point_calibration_event(self, request):
        """ Processes high point calibration event. Gets request parameters,
            executes request, returns response. """
        self.logger.debug("Processing high point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take high point calibration!."}
            return response

        # Execute request
        try:
            self.take_high_point_calibration_reading(value)
            response = {"status": 200, "message": "Set high point calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to take high point calibration reading")
            response = {"status": 500, "message": "Unable to take high point calibration reading: {}!".format(e)}
            return response


    def process_clear_calibration_event(self):
        """ Processes clear calibration event. """
        self.logger.debug("Processing clear calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to clear calibration!."}
            return response

        # Execute request
        try:
            self.clear_calibration_data()
            response = {"status": 200, "message": "Cleared calibration!"}
            return response
        except Exception as e:
            self.logger.exception("Unable to clear calibration reading")
            response = {"status": 500, "message": "Unable to clear calibration reading: {}!".format(e)}
            return response