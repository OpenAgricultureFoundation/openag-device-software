# Import standard python modules
import time, queue, json

# Import python types
from typing import Dict, Tuple, Any, Optional

# Import json validator
from jsonschema import validate

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.statemachine import Manager

# Import app models
from app.models import RecipeModel

START_RECIPE = "Start Recipe"
STOP_RECIPE = "Stop Recipe"
LOAD_RECIPE = "Load Recipe"


class RecipeEvents:
    """Event mixin for recipe manager."""

    def __init__(self, manager: Manager) -> None:
        """Initializes recipe events."""

        self.manager = manager
        self.logger = manager.logger
        self.transitions = manager.transitions
        self.logger.debug("Initialized recipe events")

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
        if timestamp != None and timestamp < time.time():  # type: ignore
            message = "Unable to start recipe, timestamp must be in the future"
            return message, 400

        # Check valid mode transition if enabled
        mode = self.manager.mode
        if check_mode and not self.transitions.is_valid(mode, Modes.START):
            message = "Unable to start recipe from {} mode".format(mode)
            self.logger.debug(message)
            return message, 400

        # Add start recipe event request to event queue
        request = {"type": START_RECIPE, "uuid": uuid, "timestamp": timestamp}
        self.queue.put(request)

        # Successfully added recipe to event queue
        message = "Starting recipe"
        return message, 200

    def _start_recipe(self, request: Dict[str, Any]) -> None:
        """Starts a recipe. Assumes request has been verified in public
        start recipe function."""
        self.logger.debug("Starting recipe")

        # Get request parameters
        uuid = request.get("uuid")
        timestamp = request.get("timestamp")

        # Convert timestamp to minutes if not None
        if timestamp != None:
            timestamp_minutes = int(timestamp / 60.0)  # type: ignore
        else:
            timestamp_minutes = int(time.time() / 60.0)

        # Check valid mode transition
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.START):
            self.logger.critical("Tried to start recipe from {} mode".format(mode))
            return

        # Start recipe on next state machine update
        self.manager.recipe_uuid = uuid
        self.manager.start_timestamp_minutes = timestamp_minutes
        self.manager.mode = Modes.START

    def stop_recipe(self, check_mode: bool = True) -> Tuple[str, int]:
        """Adds stop recipe event to event queue."""
        self.logger.debug("Adding stop recipe event to event queue")

        # Check valid mode transition if enabled
        mode = self.manager.mode
        if check_mode and not self.transitions.is_valid(mode, Modes.STOP):
            message = "Unable to stop recipe from {} mode".format(mode)
            self.logger.debug(message)
            return message, 400

        # Put request into queue
        request = {"type": STOP_RECIPE}
        self.queue.put(request)

        # Successfully added stop recipe to event queue
        message = "Stopping recipe"
        return message, 200

    def _stop_recipe(self) -> None:
        """Stops a recipe. Assumes request has been verified in public
        stop recipe function."""
        self.logger.debug("Stopping recipe")

        # Check valid mode transition
        mode = self.manager.mode
        if not self.transitions.is_valid(mode, Modes.STOP):
            self.logger.cricital("Tried to stop recipe from {} mode".format(mode))
            return

        # Stop recipe on next state machine update
        self.manager.mode = Modes.STOP

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

    def validate_recipe(
        self, json_: str, should_exist: Optional[bool] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validates a recipe. Returns true if valid."""

        # Load recipe schema
        recipe_schema = json.load(open("data/schemas/recipe.json"))

        # Check valid json
        try:
            recipe = json.loads(json_)
            validate(recipe, recipe_schema)
            uuid = recipe["uuid"]
        except:
            return False, "invalid json"

        # Check valid uuid
        if uuid == None or len(uuid) == 0:
            return False, "invalid uuid"

        # Check recipe existance criteria, does not check if should_exist == None
        recipe_exists = RecipeModel.objects.filter(uuid=uuid).exists()
        if should_exist == True and not recipe_exists:
            return False, "uuid does not exist"
        elif should_exist == False and recipe_exists:
            return False, "uuid already exists"

        # TODO: Validate recipe variables with database variables
        # TODO: Validate recipe cycle variables with recipe environments
        # TODO: Validate recipe cultivars with database cultivars
        # TODO: Validate recipe cultivation methods with database cultivation methods
        # TODO: Try to parse recipe...does this take awhile?...what is fast version?

        # Recipe is valid
        return True, None
