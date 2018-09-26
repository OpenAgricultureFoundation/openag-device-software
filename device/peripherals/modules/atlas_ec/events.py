# Import standard python modules
import time

# Import typing modules
from typing import Optional, Tuple, List, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral modules
from device.peripherals.classes.peripheral.events import PeripheralEvents
from device.peripherals.classes.atlas.exceptions import DriverError

CALIBRATE_DRY_EVENT = "Dry Calibration"
CALIBRATE_SINGLE_EVENT = "Single Point Calibration"
CALIBRATE_LOW_EVENT = "Low Point Calibration"
CALIBRATE_HIGH_EVENT = "High Point Calibration"
CLEAR_CALIBRATION_EVENT = "Clear Calibration"


class AtlasECEvents(PeripheralEvents):  # type: ignore
    """Event mixin for atlas electrical conductivity sensor."""

    # Define var types
    mode: str

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == CALIBRATE_DRY_EVENT:
            return self.calibrate_dry()
        elif request["type"] == CALIBRATE_SINGLE_EVENT:
            return self.calibrate_single(request)
        elif request["type"] == CALIBRATE_LOW_EVENT:
            return self.calibrate_low(request)
        elif request["type"] == CALIBRATE_HIGH_EVENT:
            return self.calibrate_high(request)
        elif request["type"] == CLEAR_CALIBRATION_EVENT:
            return self.clear_calibration()
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == CALIBRATE_DRY_EVENT:
            self._calibrate_dry()
        elif request["type"] == CALIBRATE_SINGLE_EVENT:
            self._calibrate_single(request)
        elif request["type"] == CALIBRATE_LOW_EVENT:
            self._calibrate_low(request)
        elif request["type"] == CALIBRATE_HIGH_EVENT:
            self._calibrate_high(request)
        elif request["type"] == CLEAR_CALIBRATION_EVENT:
            self._clear_calibration()
        else:
            message = "Invalid event request type in queue: {}".format(request["type"])
            self.logger.error(message)

    def calibrate_dry(self) -> Tuple[str, int]:
        """Pre-processes calibrate dry event request."""
        self.logger.debug("Pre-processing calibrate dry event request")

        # Require mode to be in calibrate
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take dry calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": CALIBRATE_DRY_EVENT}
        self.queue.put(request)

        # Return response
        return "Taking dry calibration reading", 200

    def _calibrate_dry(self) -> None:
        """Processes calibrate dry event request."""
        self.logger.debug("Processing calibrate dry event request")

        # Require mode to be in calibrate
        if self.mode != Modes.CALIBRATE:
            message = "Tried to calibrate dry from {} mode.".format(self.mode)
            self.logger.debug(message)
            return

        # Send command
        try:
            self.manager.driver.calibrate_dry()
        except DriverError:
            self.logger.exception("Unable to calibrate dry")

    def calibrate_single(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Processes calibrate single event request."""
        self.logger.debug("Processing calibrate single event request")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400
        except ValueError as e:
            message = "Invalid request value: `{}`".format(request["value"])
            self.logger.debug(message)
            return message, 400

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": CALIBRATE_SINGLE_EVENT, "value": value}
        self.queue.put(request)

        # Return response
        return "Taking single point calibration", 200

    def _calibrate_single(self, request: Dict[str, Any]) -> None:
        """Processes calibrate single event request."""
        self.logger.debug("Processing calibrate single event request")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Tried to calibrate single from {} mode".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            value = float(request["value"])
            self.manager.driver.calibrate_single(value)
        except DriverError:
            message = "Unable to process single point calibration event"
            self.logger.exception("Unable to calibrate single")

    def calibrate_low(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes calibrate low event request."""
        self.logger.info("Pre-processing calibrate low event request")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400
        except ValueError as e:
            message = "Invalid request value: `{}`".format(request["value"])
            self.logger.debug(message)
            return message, 400

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": CALIBRATE_LOW_EVENT, "value": value}
        self.queue.put(request)

        # Return response
        return "Taking low point calibration reading", 200

    def _calibrate_low(self, request: Dict[str, Any]) -> None:
        """Processes calibrate low event request."""
        self.logger.info("Processing calibrate low event request")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Tried to calibrate low from {} mode".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            value = float(request["value"])
            self.manager.driver.calibrate_low(value)
        except DriverError:
            self.logger.exception("Unable to calibrate low")

    def calibrate_high(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes calibrate high event request."""
        self.logger.info("Pre-processing calibrate high event request")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400
        except ValueError as e:
            message = "Invalid request value: `{}`".format(request["value"])
            self.logger.debug(message)
            return message, 400

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": CALIBRATE_HIGH_EVENT, "value": value}
        self.queue.put(request)

        # Return response
        return "Taking high point calibration reading", 200

    def _calibrate_high(self, request: Dict[str, Any]) -> None:
        """Processes calibrate high event request."""
        self.logger.debug("Processing calibrate high event request")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Tried to calibrate high from {} mode".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            value = float(request["value"])
            self.manager.driver.calibrate_high(value)
        except DriverError:
            self.logger.exception("Unable to calibrate high")

    def clear_calibration(self) -> Tuple[str, int]:
        """ Pre-processes clear calibration event request."""
        self.logger.debug("Pre-processing clear calibration event request")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to clear calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": CLEAR_CALIBRATION_EVENT}
        self.queue.put(request)

        # Return response
        return "Clearing calibration readings", 200

    def _clear_calibration(self) -> None:
        """ Processes clear calibration event request."""
        self.logger.info("Processing clear calibration event request")

        # Require mode to be in CALIBRATE
        if self.mode != Modes.CALIBRATE:
            message = "Tried to clear calibration from {} mode".format(self.mode)
            self.logger.debug(message)
            return

        # Send command
        try:
            self.manager.driver.clear_calibrations()
        except DriverError:
            self.logger.exception("Unable to clear calibrations")
