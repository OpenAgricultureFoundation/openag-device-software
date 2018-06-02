# Import standard python modules
from typing import Optional, Tuple, List, Dict
import time

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.peripheral_events import PeripheralEvents


class AtlasPHEvents(PeripheralEvents):
    """ Event mixin for led array. """


    def process_peripheral_specific_event(self, request: Dict) -> None:
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        # Execute request
        if request["type"] == "Low Point Calibration":
            self.response = self.process_low_point_calibration_event(request)
        elif request["type"] == "Mid Point Calibration":
            self.response = self.process_mid_point_calibration_event(request)
        elif request["type"] == "High Point Calibration":
            self.response = self.process_high_point_calibration_event(request)
        elif request["type"] == "Clear Calibration":
            self.response = self.process_clear_calibration_event()
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


    def process_low_point_calibration_event(self, request: Dict) -> None:
        """ Processes low point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be within range 0-4. """
        self.logger.debug("Processing low point calibration event")

        # Verify value in request
        try:
            value = int(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {
                "status": 400, "message": "Invalid request parameters: {}".format(e)
            }
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Verify value within valid range
        if value not in range(4, 10):
            error_message = "Invalid request value, not in range 4-10"
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!.",}
            return response

         # Send command
        error = self.sensor.take_low_point_calibration_reading(value)

        # Check for errors
        if error.exists():
            error.report("Unable to process low point calibration event")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            response = {"status": 500, "message": error.trace}
            return response

        # Successfully took low point calibration reading!
        response = {"status": 200, "message": "Successfully took low point calibration reading!"}
        return response


    def process_mid_point_calibration_event(self, request):
        """ Processes mid point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be in range 4-10. """
        self.logger.debug("Processing mid point calibration event")

        # Verify value in request
        try:
            value = int(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Verify value within valid range
        if value not in range(4, 10):
            error_message = "Invalid request value, not in range 4-10"
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!."}
            return response

         # Send command
        error = self.sensor.take_mid_point_calibration_reading(value)

        # Check for errors
        if error.exists():
            error.report("Unable to process mid point calibration event")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            response = {"status": 500, "message": error.trace}
            return response

        # Successfully took low point calibration reading!
        response = {"status": 200, "message": "Successfully took mid point calibration reading!"}
        return response


    def process_high_point_calibration_event(self, request):
        """ Processes high point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be within range 10-14. """
        self.logger.debug("Processing high point calibration event")

        # Verify value in request
        try:
            value = int(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
            return response
        except ValueError as e:
            error_message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Verify value within valid range
        if value not in range(10, 14):
            error_message = "Invalid request value, not in range 10-14"
            self.logger.info(error_message)
            response = {"status": 400, "message": error_message}
            return response

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to take single point calibration!."}
            return response

        # Send command
        error = self.sensor.take_high_point_calibration_reading(value)

        # Check for errors
        if error.exists():
            error.report("Unable to process high point calibration event")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            response = {"status": 500, "message": error.trace}
            return response

        # Successfully took low point calibration reading!
        response = {"status": 200, "message": "Successfully took high point calibration reading!"}
        return response



    def process_clear_calibration_event(self):
        """ Processes clear calibration event. """
        self.logger.debug("Processing clear calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            response = {"status": 400, "message": "Must be in calibration mode to clear calibration!."}
            return response

        # Send command
        error = self.sensor.clear_calibration_readings()

        # Check for errors
        if error.exists():
            error.report("Unable to process clear calibration event")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            response = {"status": 500, "message": error.trace}
            return response

        # Successfully took high point calibration reading!
        response = {"status": 200, "message": "Successfully cleared calibration readings!"}
        return response
