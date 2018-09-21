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

    def start_recipe(
        self, uuid: str, timestamp: Optional[float] = None, check_mode: bool = True
    ) -> Tuple[str, int]:
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

        # Check valid mode transition if enabled
        valid_modes = [Modes.NORECIPE, Modes.PAUSE]
        if check_mode and self.mode not in valid_modes:
            message = "Unable to start recipe, make sure recipe is in NORECIPE or PAUSE mode"
            self.logger.debug(message)
            return message, 400

        # Put request into queue
        request = {"type": START_RECIPE, "uuid": uuid, "timestamp": timestamp}
        self.event_queue.put(request)

        # Successfully added recipe to event queue
        message = "Starting recipe"
        return message, 200

    def stop_recipe(self, check_mode: bool = True) -> Tuple[str, int]:
        """Adds stop recipe event to event queue."""
        self.logger.debug("Adding stop recipe event to event queue")

        # Check valid mode transition if enabled
        valid_modes = [Modes.NORMAL, Modes.QUEUED]
        if check_mode and self.mode not in valid_modes:
            message = "Unable to stop recipe, please wait for recipe to enter NORMAL or QUEUED mode"
            self.logger.debug(message)
            return message, 400

        # Put request into queue
        request = {"type": STOP_RECIPE}
        self.event_queue.put(request)

        # Successfully added stop recipe to event queue
        message = "Stopping recipe"
        return message, 200

    def create_recipe(self, json_: str) -> Tuple[str, int]:
        """Creates a recipe into database."""
        self.logger.debug("Creating recipe")

        # Check if recipe is valid
        is_valid, error = self.validate_recipe(json_, should_exist=False)
        if not is_valid:
            message = "Unable to create recipe, {}".format(error)
            self.logger.debug(message)
            return message, 400

        # Create recipe in database
        try:
            recipe = json.loads(json_)
            RecipeModel.objects.create(json=json.dumps(recipe))
            message = "Successfully created recipe"
            return message, 200
        except:
            message = "Unable to create recipe, unhandled exception"
            self.logger.exception(message)
            return message, 500

    def update_recipe(self, json_: str) -> Tuple[str, int]:
        """Updates an existing recipe in database."""

        # Check if recipe is valid
        is_valid, error = self.validate_recipe(json_, should_exist=False)
        if not is_valid:
            message = "Unable to update recipe, {}".format(error)
            self.logger.debug(message)
            return message, 400

        # Update recipe in database
        try:
            recipe = json.loads(json_)
            r = RecipeModel.objects.get(uuid=recipe["uuid"])
            r.json = json.dumps(recipe)
            r.save()
            message = "Successfully updated recipe"
            return message, 200
        except:
            message = "Unable to update recipe, unhandled exception"
            self.logger.exception(message)
            return message, 500

    def create_or_update_recipe(self, json_: str) -> Tuple[str, int]:
        """Creates or updates an existing recipe in database."""

        # Check if recipe is valid
        is_valid, error = self.validate_recipe(json_, should_exist=None)
        if not is_valid:
            message = "Unable to update recipe, {}".format(error)
            return message, 400

        # Check if creating or updating recipe in database
        recipe = json.loads(json_)
        if not RecipeModel.objects.filter(uuid=recipe["uuid"]).exists():

            # Create recipe
            try:
                recipe = json.loads(json_)
                RecipeModel.objects.create(json=json.dumps(recipe))
                message = "Successfully created recipe"
                return message, 200
            except:
                message = "Unable to create recipe, unhandled exception"
                self.logger.exception(message)
                return message, 500
        else:

            # Update recipe
            try:
                r = RecipeModel.objects.get(uuid=recipe["uuid"])
                r.json = json.dumps(recipe)
                r.save()
                message = "Successfully updated recipe"
                return message, 200
            except:
                message = "Unable to update recipe, unhandled exception"
                self.logger.exception(message)
                return message, 500

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

        # Check valid mode transition
        valid_modes = [Modes.NORECIPE, Modes.PAUSE]
        if self.mode not in valid_modes:
            self.logger.critical("Tried to start recipe from {} mode".format(self.mode))
            return

        # Start recipe on next state machine update
        self.recipe_uuid = uuid
        self.start_timestamp_minutes = timestamp_minutes
        self.mode = Modes.START

    def _stop_recipe(self) -> None:
        """Stops a recipe. Assumes request has been verified in public
        stop recipe function."""
        self.logger.debug("Stopping recipe")

        # Check valid mode transition
        valid_modes = [Modes.NORMAL, Modes.QUEUED]
        if self.mode not in valid_modes:
            self.logger.cricital("Tried to stop recipe from {} mode".format(self.mode))
            return

        # Stop recipe on next state machine update
        self.mode = Modes.STOP
