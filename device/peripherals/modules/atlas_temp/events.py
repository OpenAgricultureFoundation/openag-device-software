# Import python types
from typing import Optional, Tuple, List, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral.events import PeripheralEvents
from device.peripherals.classes.peripheral.exceptions import DriverError


CALIBRATE_EVENT = "Calibrate"


class AtlasTempEvents(PeripheralEvents):  # type: ignore
    """Event mixin for manager."""

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == CALIBRATE_EVENT:
            return self.calibrate(request)
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        type_ = request.get("type")
        if request["type"] == CALIBRATE_EVENT:
            self._calibrate(request)
        else:
            self.logger.error("Invalid event request type in queue: {}".format(type_))

    def calibrate(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes calibrate event request."""
        self.logger.debug("Pre-processing calibrate event request")

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

        # Require mode to be in calibrate
        if self.mode != Modes.CALIBRATE:
            message = "Must be in calibration mode to take calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": CALIBRATE_EVENT, "value": value}
        self.queue.put(request)

        # Return response
        return "Taking dry calibration reading", 200

    def _calibrate(self, request: Dict[str, Any]) -> None:
        """Processes calibrate event request."""
        self.logger.debug("Processing calibrate event request")

        # Require mode to be in calibrate
        if self.mode != Modes.CALIBRATE:
            message = "Tried to calibrate from {} mode.".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            self.manager.driver.calibrate()
        except DriverError:
            self.logger.exception("Unable to calibrate")
