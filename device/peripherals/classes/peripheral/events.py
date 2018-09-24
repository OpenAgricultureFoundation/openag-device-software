# Import standard python modules
import queue

# Import python types
from typing import Dict, Tuple, Any

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.logger import Logger
from device.utilities.statemachine import Manager

# Initialize vars
RESET_EVENT = "Reset"
SHUTDOWN_EVENT = "Shutdown"
SET_SAMPLING_INTERVAL_EVENT = "Set Sampling Interval"
ENABLE_CALIBRATION_MODE_EVENT = "Enable Calibration Mode"
ENABLE_MANUAL_MODE_EVENT = "Enable Manual Mode"


class PeripheralEvents:
    """Event mixin for peripherals."""

    def __init__(self, manager: Manager) -> None:
        """Initializes peripheral events."""
        self.manager = manager
        self.logger = manager.logger
        self.transitions = manager.transitions
        self.logger.debug("Initialized peripheral events")

        # Initialize event queue
        self.queue: queue.Queue = queue.Queue()

    @property
    def mode(self) -> str:
        """Gets manager mode."""
        return str(self.manager.mode)

    @mode.setter
    def mode(self, value: str) -> None:
        """Sets manager mode."""
        self.manager.mode = value

    def create(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Creates a new event, checks for matching event type, pre-processes request, 
        then adds to event queue."""
        self.logger.debug("Creating event request: `{}`".format(request))

        # Get request parameters
        try:
            type_ = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400

        # Process general event requests
        if type_ == RESET_EVENT:
            return self.reset()
        elif type_ == SHUTDOWN_EVENT:
            return self.shutdown()
        elif type_ == SET_SAMPLING_INTERVAL_EVENT:
            return self.set_sampling_interval(request)
        elif type_ == ENABLE_CALIBRATION_MODE_EVENT:
            return self.enable_calibration_mode()
        elif type_ == ENABLE_MANUAL_MODE_EVENT:
            return self.enable_manual_mode()
        else:
            return self.create_peripheral_specific_event(request)

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event. This method should be 
        overridden in child class."""
        return "Unknown event request type", 400

    def check(self) -> None:
        """Checks for a new event. Only processes one event per call, even if there are 
        multiple in the queue. Events are processed first-in-first-out (FIFO)."""

        # Check for new events
        if self.queue.empty():
            return

        # Get request
        request = self.queue.get()
        self.logger.debug("Received new request: {}".format(request))

        # Get request parameters
        try:
            type_ = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.exception(message)
            return

        # Execute request
        if type_ == RESET_EVENT:
            self._reset()
        elif type_ == SHUTDOWN_EVENT:
            self._shutdown()
        elif type_ == SET_SAMPLING_INTERVAL_EVENT:
            self._set_sampling_interval(request)
        elif type_ == ENABLE_CALIBRATION_MODE_EVENT:
            self._enable_calibration_mode()
        elif type_ == ENABLE_MANUAL_MODE_EVENT:
            self._enable_manual_mode()
        else:
            self.check_peripheral_specific_events(request)

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events. This method should be 
        overwritten in child class."""
        type_ = request.get("type")
        self.logger.error("Invalid event request type in queue: {}".format(type_))

    def reset(self) -> Tuple[str, int]:
        """Pre-processes reset event request."""
        self.logger.debug("Pre-processing reset event request")

        # Check valid transitions
        if not self.transitions.is_valid(self.manager.mode, Modes.RESET):
            message = "Unable to reset peripheral from {} mode".format(
                self.manager.mode
            )
            self.logger.debug(message)
            return message, 400

        # Add reset event request to event queue
        request = {"type": RESET_EVENT}
        self.queue.put(request)

        # Return event response
        return "Resetting", 200

    def _reset(self) -> None:
        """Processes reset event request."""
        self.logger.debug("Processing reset event request")

        # Check valid transitions
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.RESET):
            self.logger.critical("Tried to reset from {} mode".format(mode))
            return

        # Transition to reset mode on next state machine update
        self.manager.mode = Modes.RESET

    def shutdown(self) -> Tuple[str, int]:
        """Pre-processes shutdown event request."""
        self.logger.debug("Pre-processing shutdown event request")

        # Check sensor isn't already in shutdown mode
        if self.manager.mode == Modes.SHUTDOWN:
            message = "Already in shutdown mode"
            self.logger.debug(message)
            return message, 200

        # Check valid transitions
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.SHUTDOWN):
            message = "Unable to shutdown from {} mode".format(mode)
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": SHUTDOWN_EVENT}
        self.queue.put(request)

        # Return event response
        return "Shutting down", 200

    def _shutdown(self) -> None:
        """Processes shutdown peripheral event request."""
        self.logger.debug("Processing shutdown event request")

        # Check valid transitions
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.SHUTDOWN):
            self.logger.critical("Tried to shutdown from {} mode".format(mode))
            return

        # Transition to shutdown mode on next state machine update
        self.manager.mode = Modes.SHUTDOWN

    def set_sampling_interval(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes set sampling interval event request."""
        self.logger.debug("Pre-processing set sampling interval event request")

        # Verify value in request
        try:
            value = request["value"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400

        # Safely get desired sampling interval
        try:
            interval = float(value)
        except ValueError:
            message = "Invalid sampling interval value"
            self.logger.debug(message)
            return message, 400

        # Check desired sampling interval larger than min interval
        msi = self.manager.min_sampling_interval
        if interval < msi:
            message = "Unable to set sampling interval below {} seconds.".format(msi)
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": SET_SAMPLING_INTERVAL_EVENT, "interval": interval}
        self.queue.put(request)

        # Return event response
        return "Setting sampling interval", 200

    def _set_sampling_interval(self, request: Dict[str, Any]) -> None:
        """Processes set sampling interval event request."""
        self.logger.debug("Processing set sampling interval event request")

        # Set sampling interval
        interval = request.get("interval")
        self.sampling_interval_seconds = interval

    def enable_calibration_mode(self) -> Tuple[str, int]:
        """Pre-processes enable calibration mode event request."""
        self.logger.debug("Pre-processing enable calibration mode event request")

        # Check if sensor alread in calibration mode
        if self.manager.mode == Modes.CALIBRATE:
            message = "Already in calibration mode"
            self.logger.debug(message)
            return message, 200

        # Check valid transition
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.CALIBRATE):
            message = "Unable to enable calibration mode from {} mode".format(mode)
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": ENABLE_CALIBRATION_MODE_EVENT}
        self.queue.put(request)

        # Return response
        return "Enabling calibration mode", 200

    def _enable_calibration_mode(self) -> None:
        """Processes enable calibration mode event request."""
        self.logger.debug("Processing enable calibration mode event request")

        # Check valid transitions
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.SHUTDOWN):
            message = "Tried to enable calibration mode from {}".format(mode)
            self.logger.critical(message)
            return

        # Transition to calibration mode on next state machine update
        self.manager.mode = Modes.CALIBRATE

    def enable_manual_mode(self) -> Tuple[str, int]:
        """Pre-processes enable manual mode event request."""
        self.logger.debug("Pre-processing enable manual mode event request")

        # Check if sensor alread in manual mode
        if self.manager.mode == Modes.MANUAL:
            message = "Already in manual mode"
            self.logger.debug(message)
            return message, 200

        # Check valid transition
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.MANUAL):
            message = "Unable to enable manual mode from {} mode".format(mode)
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": ENABLE_MANUAL_MODE_EVENT}
        self.queue.put(request)

        # Return response
        return "Enabling manual mode", 200

    def _enable_manual_mode(self) -> None:
        """Processes enable manual mode event request."""
        self.logger.debug("Processing enable manual mode event request")

        # Check peripheral is in acceptible mode
        modes = [Modes.NORMAL, Modes.CALIBRATE]
        if self.manager.mode not in modes:
            message = "Unable to enable manual mode from {} mode".format(
                self.manager.mode
            )
            self.logger.critical(message)
            return

        # Transition to manual mode on next state machine update
        self.manager.mode = Modes.MANUAL
