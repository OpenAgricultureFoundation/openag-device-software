# Import standard python modules
import logging, threading, queue, time

# Import python types
from typing import Dict, List, Tuple, Any

# Import device utilities
from device.utilities.logger import Logger

# Import module elements
from device.utilities.statemachine.modes import (
    INIT_MODE,
    NORMAL_MODE,
    RESET_MODE,
    SHUTDOWN_MODE,
    ERROR_MODE,
    INVALID_MODE,
)
from device.utilities.statemachine.events import RESET_EVENT, SHUTDOWN_EVENT


class StateMachineManager:
    """Manages state machines. Runs as a daemon thread, ensures valid transitions, 
    and handles external events with an Events mixin class."""

    def __init__(self) -> None:
        """Initializes state machine manager."""
        self.logger: Logger = Logger("StateMachineManager", __name__)
        self.thread: threading.Thread = threading.Thread(target=self.run)
        self.event_queue: queue.Queue = queue.Queue()
        self.is_shutdown: bool = False
        self.mode: str = INIT_MODE
        self.transitions: Dict[str, List[str]] = {
            INIT_MODE: [NORMAL_MODE, SHUTDOWN_MODE, ERROR_MODE],
            NORMAL_MODE: [RESET_MODE, SHUTDOWN_MODE, ERROR_MODE],
            RESET_MODE: [INIT_MODE, SHUTDOWN_MODE, ERROR_MODE],
            ERROR_MODE: [RESET_MODE, SHUTDOWN_MODE],
        }
        self.logger.debug("Initialized")

    def spawn(self) -> None:
        """ Spawns state machine thread. """
        self.thread.daemon = True
        self.thread.start()

    def run(self) -> None:
        """Runs state machine."""

        # Loop forever
        while True:

            # Check if thread is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == INIT_MODE:
                self.run_init_mode()
            elif self.mode == NORMAL_MODE:
                self.run_normal_mode()
            elif self.mode == RESET_MODE:
                self.run_reset_mode()
            elif self.mode == ERROR_MODE:
                self.run_error_mode()
            elif self.mode == SHUTDOWN_MODE:
                self.run_shutdown_mode()
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = INVALID_MODE
                self.is_shutdown = True
                break

    def run_init_mode(self) -> None:
        """Runs init mode."""
        self.logger.debug("Entered INIT")

        # Do something

        # Transition to normal mode on next state machine update
        self.mode = NORMAL_MODE

    def run_normal_mode(self) -> None:
        """Runs normal mode."""
        self.logger.debug("Entered NORMAL")

        # Loop forever:
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(NORMAL_MODE):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_reset_mode(self) -> None:
        """Runs reset mode."""
        self.logger.debug("Entered RESET")

        # Do something

        # Transition to init mode on next state machine update
        self.mode = INIT_MODE

    def run_error_mode(self) -> None:
        """Runs error mode."""
        self.logger.debug("Entered ERROR")

        # Loop forever:
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(ERROR_MODE):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_shutdown_mode(self) -> None:
        """Runs shutdown mode."""
        self.logger.debug("Entered SHUTDOWN")

        # Break out of run thread on next state machine update
        self.is_shutdown = True

    def valid_transition(self, from_mode: str, to_mode: str) -> bool:
        """Checks if transition from mode to mode is valid."""

        # Check valid mode name
        if from_mode not in self.transitions:
            self.logger.critical("Invalid mode name: `{}`".format(from_mode))
            return False

        # Check if `to mode` registed in transitions for `from mode`
        if to_mode in self.transitions[from_mode]:
            return True
        else:
            return False

    def new_transition(self, current_mode: str) -> bool:
        """Checks for a new transition. Logs errors if tries invalid transition."""

        self.logger.debug("current_mode = {}".format(current_mode))
        self.logger.debug("self.mode = {}".format(self.mode))

        # Check if state machine mode still in current mode
        if current_mode == self.mode:
            return False

        # Check if state machine mode is a valid transition from the current mode
        if self.valid_transition(current_mode, self.mode):
            return True
        else:
            message = "Invalid transition attempt from {} to {}".format(
                current_mode, self.mode
            )
            self.mode = ERROR_MODE
            return True

    def create_event(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Creates a new event, checks for matching event type, pre-processes request,
        then adds to event queue. Returns message and http status code."""

        if request["type"] == RESET_EVENT:
            return self.reset()
        elif request["type"] == SHUTDOWN_EVENT:
            return self.shutdown()
        else:
            return "Unknown event request type", 400

    def check_events(self) -> None:
        """Checks for a new event. Only processes one event per call, even if there are 
        multiple in the queue. Events are processed first-in-first-out (FIFO)."""

        # Check for new events
        if self.event_queue.empty():
            return

        # Get request
        request = self.event_queue.get()
        self.logger.debug("Received new request: {}".format(request))

        # Get request parameters
        try:
            type_ = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.error(message)
            return

        # Execute request
        if type_ == SHUTDOWN_EVENT:
            self._shutdown()
        elif type_ == RESET_EVENT:
            self._reset()
        else:
            self.logger.error("Invalid event request type in queue: {}".format(type_))

    def shutdown(self) -> Tuple[str, int]:
        """Pre-processes shutdown event. Returns message and http status code."""
        self.logger.debug("Pre-processing shutdown event request")

        # Add start recipe event request to event queue
        request = {"type": SHUTDOWN_EVENT}
        self.event_queue.put(request)

        # Successfully added shutdown event to event queue
        message = "Shutting down"
        return message, 200

    def _shutdown(self) -> None:
        """Processes shutdown event."""
        self.logger.debug("Processing shutdown event request")

        # Transition to shutdown mode on next state machine update
        self.mode = SHUTDOWN_MODE

    def reset(self) -> Tuple[str, int]:
        """Pre-processes reset event request. Returns message and http status code."""
        self.logger.debug("Pre-processing reset event request")

        # Check valid transitions
        if not self.valid_transition(self.mode, RESET_MODE):
            message = "Unable to reset from {} mode".format(self.mode)
            self.logger.debug(message)
            return message, 400

        # Add reset event request to event queue
        request = {"type": RESET_EVENT}
        self.event_queue.put(request)

        # Return event response
        return "Resetting", 200

    def _reset(self) -> None:
        """Processes reset event request."""
        self.logger.debug("Processing reset event request")

        # Check valid transitions
        if not self.valid_transition(self.mode, RESET_MODE):
            self.logger.critical("Tried to reset from {} mode".format(self.mode))
            return

        # Transition to reset mode on next state machine update
        self.mode = RESET_MODE
