# Import standard python modules
import time, queue, json, glob

# Import python types
from typing import Dict, Tuple, Any, Optional

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.statemachine import Manager

LOAD_DEVICE_CONFIG = "Load Device Config"
CONFIG_PATH = "data/config/"
# DEVICE_CONFIG_PATH = CONFIG_PATH + "device.txt"


class CoordinatorEvents:
    """Event mixin for coordinator manager."""

    def __init__(self, manager: Manager) -> None:
        """Initializes coordinator events."""

        self.manager = manager
        self.logger = manager.logger
        self.transitions = manager.transitions
        self.logger.debug("Initialized coordinator events")

        # Initialize event queue
        self.queue: queue.Queue = queue.Queue()

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
        if type_ == LOAD_DEVICE_CONFIG:
            self._load_device_config(request)
        else:
            self.logger.error("Invalid event request type in queue: {}".format(type_))

    def load_device_config(self, uuid: str) -> Tuple[str, int]:
        """Pre-processes load device config event request."""
        self.logger.debug("Pre-processing load device config request")

        # Get filename of corresponding uuid
        filename = None
        for filepath in glob.glob("data/devices/*.json"):
            self.logger.debug(filepath)
            device_config = json.load(open(filepath))
            if device_config["uuid"] == uuid:
                filename = filepath.split("/")[-1].replace(".json", "")
        # self.logger.debug(filename)

        # Verify valid config uuid
        if filename == None:
            message = "Invalid config uuid, corresponding filepath not found"
            self.logger.debug(message)
            return message, 400

        # Check valid mode transition if enabled
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.LOAD):
            message = "Unable to load device config from {} mode".format(mode)
            self.logger.debug(message)
            return message, 400

        # Add load device config event request to event queue
        request = {"type": LOAD_DEVICE_CONFIG, "filename": filename}
        self.queue.put(request)

        # Successfully added load device config request to event queue
        message = "Loading config"
        return message, 200

    def _load_device_config(self, request: Dict[str, Any]) -> None:
        """Processes load device config event request."""
        self.logger.debug("Processing load device config request")

        # Get request parameters
        filename = request.get("filename")

        # Write config filename to device config path
        with open(CONFIG_PATH + "device.txt", "w") as f:
            f.write(str(filename) + "\n")

        # Transition to load mode on next state machine update
        self.manager.mode = Modes.LOAD
