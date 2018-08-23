# Import standard python modules
import time

# Import typing modules
from typing import Optional, Tuple, List, Dict

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral modules
from device.peripherals.classes.peripheral.events import PeripheralEvents
from device.peripherals.modules.atlas_ph.exceptions import DriverError


class AtlasPHEvents(PeripheralEvents):  # type: ignore
    """Event mixin for manager."""

    # Initialize var types
    mode: str

    def process_peripheral_specific_event(self, request: Dict) -> None:
        """Processes an event. Gets request parameters, executes request, returns 
        response."""

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
            message = "Unknown event request type"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}

    def process_low_point_calibration_event(self, request: Dict) -> Dict:
        """ Processes low point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be within range 0-4. """
        self.logger.info("Processing low point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            message = "Invalid request parameters: {}".format(e)
            return {"status": 400, "message": message}
        except ValueError as e:
            message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(message)
            return {"status": 400, "message": message}

        # Verify value within valid range
        if value not in range(4, 10):
            message = "Invalid request value, not in range 4-10"
            self.logger.info(message)
            return {"status": 400, "message": message}

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            return {"status": 400, "message": message}

        # Send command
        try:
            self.driver.take_low_point_calibration_reading(value)
        except DriverError:
            message = "Unable to process low point calibration event"
            self.logger.exception(message)
            self.mode = Modes.ERROR
            return {"status": 500, "message": message}

        # Successfully took low point calibration reading
        message = "Successfully took low point calibration reading"
        return {"status": 200, "message": message}

    def process_mid_point_calibration_event(self, request: Dict) -> Dict:
        """ Processes mid point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be in range 4-10. """
        self.logger.info("Processing mid point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            message = "Invalid request parameters: {}".format(e)
            return {"status": 400, "message": message}
        except ValueError as e:
            message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(message)
            return {"status": 400, "message": message}

        # Verify value within valid range
        if value not in range(4, 10):
            message = "Invalid request value, not in range 4-10"
            self.logger.info(message)
            return {"status": 400, "message": message}

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            return {"status": 400, "message": message}

        # Send command
        try:
            self.driver.take_mid_point_calibration_reading(value)
        except DriverError:
            message = "Unable to process mid point calibration event"
            self.logger.exception(message)
            self.mode = Modes.ERROR
            return {"status": 500, "message": message}

        # Successfully took low point calibration reading
        message = "Successfully took mid point calibration reading"
        return {"status": 200, "message": message}

    def process_high_point_calibration_event(self, request: Dict) -> Dict:
        """ Processes high point calibration event. Gets request parameters,
            executes request, returns response. Requires calibration value 
            to be within range 10-14. """
        self.logger.info("Processing high point calibration event")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.exception(message)
            return {"status": 400, "message": message}
        except ValueError as e:
            message = "Invalid request value: `{}`".format(request["value"])
            self.logger.exception(message)
            return {"status": 400, "message": message}

        # Verify value within valid range
        if value not in range(10, 14):
            message = "Invalid request value, not in range 10-14"
            self.logger.info(message)
            return {"status": 400, "message": message}

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            return {"status": 400, "message": message}

        # Send command
        try:
            self.driver.take_high_point_calibration_reading(value)
        except DriverError:
            message = "Unable to process high point calibration event"
            self.logger.exception(message)
            self.mode = Modes.ERROR
            return {"status": 500, "message": message}

        # Successfully took low point calibration reading
        message = "Successfully took high point calibration reading"
        return {"status": 200, "message": message}

    def process_clear_calibration_event(self) -> Dict:
        """ Processes clear calibration event. """
        self.logger.info("Processing clear calibration event")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to clear calibration"
            return {"status": 400, "message": message}

        # Send command
        try:
            self.driver.clear_calibration_readings()
        except DriverError:
            message = "Unable to process clear calibration event"
            self.logger.exception(message)
            self.mode = Modes.ERROR
            return {"status": 500, "message": message}

        # Successfully took high point calibration reading
        message = "Successfully cleared calibration readings"
        return {"status": 200, "message": message}
