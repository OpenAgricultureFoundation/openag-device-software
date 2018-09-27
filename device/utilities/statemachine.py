# Import standard python modules
import logging, threading, queue

# Import python types
from typing import Dict, List


# TODO: Make modes their own classes instead of strings...
# E.g. class ErrorMode(BaseMode)


class StateMachineManager:
    """State machine manager base class."""

    # Initialize var types
    mode: str
    transitions: Dict[str, List[str]]

    def __init__(self):
        """Initializes state machine manager."""

        # Initialize event queue
        self.event_queue: queue.Queue = queue.Queue()

        # Not sure we need this
        self.stop_event = threading.Event()

    def spawn(self) -> None:
        """ Spawns recipe thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

    def stopped(self) -> bool:
        return self.stop_event.is_set()

    def valid_transition(self, from_mode: str, to_mode: str) -> bool:
        """Checks if transition from mode to mode is valid."""
        if to_mode in self.transitions[from_mode]:
            return True
        else:
            return False

    def new_transition(self, mode: str) -> bool:
        """Checks for a new transition. Logs errors if tries invalid transition."""

        # Check if state machine mode still in current mode
        if mode == self.mode:
            return False

        # Check if state machine mode is a valid transition from the current mode
        if self.valid_transition(mode, self.mode):
            return True
        else:
            message = "Invalid transition attempt from {} to {}".format(mode, self.mode)
            self.mode = "ERROR"  # this is error prone
            return True


# Temporary -- remove me
class Manager(StateMachineManager):
    ...


class Transitions(object):
    """Explicates and verifies state machine transitions."""

    def __init__(
        self, manager: Manager, transition_table: Dict[str, List[str]]
    ) -> None:
        """Initializes transitions object."""
        self.manager = manager
        self.table = transition_table
        self.logger = manager.logger

    def is_new(self, mode: str) -> bool:
        """Checks for a new and valid transition mode."""

        # Check if no mode transition
        if mode == self.manager.mode:
            return False

        # Check if valid mode transition
        if self.manager.mode in self.table[mode]:
            return True

        # Otherwise is invalid mode transition
        else:
            message = "Invalid mode transition, cannot transition from {} to {}".format(
                mode, self.manager.mode
            )
            self.logger.critical(message)
            return False

    def is_valid(self, from_: str, to: str) -> bool:
        """Checks if transition from mode to mode is valid."""
        if to in self.table[from_]:
            return True
        else:
            return False
