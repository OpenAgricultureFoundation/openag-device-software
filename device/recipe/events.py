# Import standard python modules
import time, queue, json

# Import python types
from typing import Dict, Tuple, Any, Optional

# Import device utilities
from device.utilities.modes import Modes

# Import app models
from app.models import RecipeModel


START_RECIPE = "Start Recipe"
STOP_RECIPE = "Stop Recipe"
LOAD_RECIPE = "Load Recipe"


class RecipeEvents:
    """Event mixin for recipe manager."""

    event_queue = queue.Queue()

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
            self.logger.exception(message)
            return

        # Execute request
        if type_ == START_RECIPE:
            self._start_recipe(request)
        elif type_ == STOP_RECIPE:
            self._stop_recipe()
        else:
            self.logger.error("Invalid event request type in queue: {}".format(type_))

    def _start_recipe(self, request: Dict[str, Any]) -> None:
        """Starts a recipe. Assumes request has been verified in public
        start recipe function."""
        self.logger.debug("Starting recipe")

        # Get request parameters
        uuid = request.get("uuid")
        timestamp = request.get("timestamp")

        # Convert timestamp to minutes if not None
        if timestamp != None:
            timestamp_minutes = int(timestamp / 60.0)
        else:
            timestamp_minutes = int(time.time() / 60.0)

        # Start recipe on next state machine update
        self.recipe_uuid = uuid
        self.start_timestamp_minutes = timestamp_minutes
        self.mode = Modes.START

    def _stop_recipe(self) -> None:
        """Stops a recipe. Assumes request has been verified in public
        stop recipe function."""
        self.logger.debug("Stopping recipe")

        # Stop recipe on next state machine update
        self.mode = Modes.STOP

    def verify_recipe(self, json_: str) -> None:
        """Verifies a recipe."""
        ...

    ##################### PUBLIC FUNCTIONS #####################################

    def start_recipe(self, uuid: str, timestamp: Optional[float]) -> Tuple[str, int]:
        """Adds a start recipe event to event queue."""
        self.logger.debug("Adding start recipe event to event queue")
        self.logger.debug("Recipe UUID: {}, timestamp: {}".format(uuid, timestamp))

        # Check recipe uuid exists
        if not RecipeModel.objects.filter(uuid=uuid).exists():
            message = "Unable to start recipe, invalid uuid"
            return message, 400

        # Check timestamp is valid if provided
        if timestamp != None and timestamp < time.time():
            message = "Unable to start recipe, timestamp must be in the future"
            return message, 400

        # Check valid mode transition
        valid_modes = [Modes.NORECIPE, Modes.PAUSE]
        if self.mode not in valid_modes:
            message = "Unable to stop recipe, make sure recipe is in NORECIPE or PAUSE mode"
            self.logger.debug(message)
            return message, 400

        # Put request into queue
        request = {"type": START_RECIPE, "uuid": uuid, "timestamp": timestamp}
        self.event_queue.put(request)

        # Successfully added recipe to event queue
        message = "Queued start recipe event, this may take a few moments depending on the recipe size"
        return message, 200

    def stop_recipe(self) -> Tuple[str, int]:
        """Adds stop recipe event to event queue."""
        self.logger.debug("Adding stop recipe event to event queue")

        # Check valid mode transition
        valid_modes = [Modes.NORMAL, Modes.QUEUED]
        if self.mode not in valid_modes:
            message = "Unable to stop recipe, please wait for recipe to enter NORMAL or QUEUED mode"
            self.logger.debug(message)
            return message, 400

        # Put request into queue
        request = {"type": STOP_RECIPE}
        self.event_queue.put(request)

        # Successfully added stop recipe to event queue
        message = "Queued stop recipe event"
        return message, 200

    def create_recipe(self, json_: str) -> Tuple[str, int]:
        """Creates a new recipe entry in database."""
        self.logger.debug("Creating recipe")

        # TODO: Validate recipe json
        self.logger.debug(json_)
        self.logger.debug(type(json_))

        recipe = json.loads(json_)

        # Check recipe uuid does not already exist
        uuid = recipe["uuid"]
        if RecipeModel.objects.filter(uuid=uuid).exists():
            message = "Unable to load recipe, uuid already exists"
            self.logger.debug(message)
            return message, 400

        # Create recipe in database
        RecipeModel.objects.create(json=json.dumps(recipe))

        # Successfully loaded recipe
        message = "Successfully loaded recipe"
        return message, 200
