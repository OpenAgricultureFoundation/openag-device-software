# Import standard python modules
import time, queue, json
from json.decoder import JSONDecodeError

# Import python types
from typing import Dict, Tuple, Any, Optional

# Import json validator
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.statemachine import Manager

# Import app models
from app.models import (
    RecipeModel,
    SensorVariableModel,
    CultivarModel,
    CultivationMethodModel,
)

START_RECIPE = "Start Recipe"
STOP_RECIPE = "Stop Recipe"
LOAD_RECIPE = "Load Recipe"


class RecipeEvents:
    """Event mixin for recipe manager."""

    def check_events(self) -> None:
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
        if check_mode and not self.transitions.is_valid(self.mode, Modes.START):
            message = "Unable to start recipe from {} mode".format(self.mode)
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
        if not self.transitions.is_valid(self.mode, Modes.START):
            self.logger.critical("Tried to start recipe from {} mode".format(self.mode))
            return

        # Start recipe on next state machine update
        self.recipe_uuid = uuid
        self.start_timestamp_minutes = timestamp_minutes
        self.mode = Modes.START

    def stop_recipe(self, check_mode: bool = True) -> Tuple[str, int]:
        """Adds stop recipe event to event queue."""
        self.logger.debug("Adding stop recipe event to event queue")

        # Check valid mode transition if enabled
        if check_mode and not self.transitions.is_valid(self.mode, Modes.STOP):
            message = "Unable to stop recipe from {} mode".format(self.mode)
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
        if not self.transitions.is_valid(self.mode, Modes.STOP):
            self.logger.cricital("Tried to stop recipe from {} mode".format(self.mode))
            return

        # Stop recipe on next state machine update
        self.mode = Modes.STOP

    def create_recipe(self, json_: str) -> Tuple[str, int]:
        """Creates a recipe into database."""
        self.logger.debug("Creating recipe")

        # Check if recipe is valid
        is_valid, error = self.validate_recipe(json_, should_exist=False)
        if not is_valid:
            message = "Unable to create recipe. {}".format(error)
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
            message = "Unable to update recipe. {}".format(error)
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
            message = "Unable to create/update recipe -> {}".format(error)
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

        # Check valid json and try to parse recipe
        try:
            # Decode json
            recipe = json.loads(json_)

            # Validate recipe against schema
            validate(recipe, recipe_schema)

            # Parse recipe
            format_ = recipe["format"]
            version = recipe["version"]
            name = recipe["name"]
            uuid = recipe["uuid"]
            cultivars = recipe["cultivars"]
            cultivation_methods = recipe["cultivation_methods"]
            environments = recipe["environments"]
            phases = recipe["phases"]

        except JSONDecodeError as e:
            message = "Invalid recipe json encoding: {}".format(e)
            self.logger.debug(message)
            return False, message
        except ValidationError as e:
            message = "Invalid recipe json schema: {}".format(e.message)
            self.logger.debug(message)
            return False, message
        except KeyError as e:
            self.logger.critical("Recipe schema did not ensure `{}` exists".format(e))
            message = "Invalid recipe json schema: `{}` is requred".format(e)
            return False, message
        except Exception as e:
            self.logger.critical("Invalid recipe, unhandled exception: {}".format(e))
            return False, "Unhandled exception: {}".format(type(e))

        # Check valid uuid
        if uuid == None or len(uuid) == 0:
            return False, "Invalid uuid"

        # Check recipe existance criteria, does not check if should_exist == None
        recipe_exists = RecipeModel.objects.filter(uuid=uuid).exists()
        if should_exist == True and not recipe_exists:
            return False, "UUID does not exist"
        elif should_exist == False and recipe_exists:
            return False, "UUID already exists"

        # Check cycle environment key names are valid
        try:
            for phase in phases:
                for cycle in phase["cycles"]:
                    cycle_name = cycle["name"]
                    environment_key = cycle["environment"]
                    if environment_key not in environments:
                        message = "Invalid environment key `{}` in cycle `{}`".format(
                            environment_key, cycle_name
                        )
                        self.logger.debug(message)
                        return False, message
        except KeyError as e:
            self.logger.critical("Recipe schema did not ensure `{}` exists".format(e))
            message = "Invalid recipe json schema: `{}` is requred".format(e)
            return False, message

        # Build list of environment variables
        env_vars = []
        for env_key, env_dict in environments.items():
            for env_var, _ in env_dict.items():
                if env_var != "name" and env_var not in env_vars:
                    env_vars.append(env_var)

        # Check environment variables are valid sensor variables
        for env_var in env_vars:
            if not SensorVariableModel.objects.filter(key=env_var).exists():
                message = "Invalid recipe environment variable: `{}`".format(env_var)
                self.logger.debug(message)
                return False, message

        # Check cultivars are valid
        for cultivar in cultivars:
            cultivar_name = cultivar["name"]
            cultivar_uuid = cultivar["uuid"]
            if not CultivarModel.objects.filter(uuid=cultivar_uuid).exists():
                message = "Invalid recipe cultivar: `{}`".format(cultivar_name)
                self.logger.debug(message)
                return False, message

        # Check cultivation methods are valid
        for method in cultivation_methods:
            method_name = method["name"]
            method_uuid = method["uuid"]
            if not CultivationMethodModel.objects.filter(uuid=method_uuid).exists():
                message = "Invalid recipe cultivation method: `{}`".format(method_name)
                self.logger.debug(message)
                return False, message

        # Recipe is valid
        return True, None
