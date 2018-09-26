# Import standard python modules
import logging

# Import python types
from typing import Dict, List


class Manager(object):
    """State machine manager base class. Mainly just for type checking right now."""

    logger: logging.Logger
    mode: str


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
