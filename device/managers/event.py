# Import python modules
import logging, time, threading, json, os, sys

# Import device modes errors and events
from device.utilities.modes import Modes
from device.utilities.errors import Errors
from device.utilities.events import EventRequests
from device.utilities.events import EventResponses

# Import database models
from app.models import EventModel
from app.models import RecipeModel


class EventManager:
    """ Manages events. """

    # Initialize logger
    extra = {"console_name":"Event", "file_name": "event"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    # Initialize mode & error variables
    _mode = None
    _error = None

    # Initialize thread object
    thread = None


    def __init__(self, state):
        """ Initialize event handler. """
        self.state = state
        self.mode = Modes.INIT
        self.error = Errors.NONE


    @property
    def recipe_mode(self):
        """ Gets recipe mode from shared state. """
        if "mode" in self.state.recipe:
            return self.state.recipe["mode"]
        else:
            return None


    @property
    def commanded_recipe_mode(self):
        """ Gets commanded recipe mode from shared state. """
        if "commanded_mode" in self.state.recipe:
            return self.state.recipe["commanded_mode"]
        else:
            return None


    @commanded_recipe_mode.setter
    def commanded_recipe_mode(self, value):
        """ Safely updates commanded recipe mode in shared state. """
        with threading.Lock():
            self.state.recipe["commanded_mode"] = value


    @property
    def commanded_recipe_uuid(self):
        """ Gets commanded recipe uuid from shared state. """
        if "commanded_uuid" in self.state.recipe:
            return self.state.recipe["commanded_recipe_uuid"]
        else:
            return None


    @commanded_recipe_uuid.setter
    def commanded_recipe_uuid(self, value):
        """ Safely updates commanded recipe uuid in shared state. """
        with threading.Lock():
            self.state.recipe["commanded_recipe_uuid"] = value


    def process(self, sender, instance, **kwargs):
        """ Processes event when new model is saved in Event table. """
        event = EventModel.objects.latest()

        # Check if new event
        if event.response is not None:
            return
            
        # Initialize response
        event.response = {}

        # Verify request is valid
        if "type" not in event.request:
            event.response["type"] = EventResponses.INVALID_REQUEST
            event.save()
            return
        
        # Handle event
        if event.request["type"] == EventRequests.CREATE_RECIPE:
            self.create_recipe(event)
        elif event.request["type"] == EventRequests.START_RECIPE:
            self.start_recipe(event)
        elif event.request["type"] == EventRequests.STOP_RECIPE:
            self.stop_recipe(event)
        else:
            event.response["type"] = EventResponses.INVALID_EVENT
            event.save()


    def create_recipe(self, event):
        """ Creates recipe. Validates json, creates entry in database, then 
            returns response. """
        self.logger.info("Received CREATE_RECIPE")

        # Get recipe json
        if "recipe_json" not in event.request:
            event.response["status"] = 400
            event.response["message"] = "Request does not contain `recipe_json`"
            event.save()
            return
        else:
            recipe_json = event.request["recipe_json"]

        # Validate recipe
        recipe_validator = RecipeValidator()
        error_message = recipe_validator.validate(recipe_json)
        if error_message != None:
            self.logger.info("Recipe is invalid: {}".format(error_message))
            event.response["status"] = 400
            event.response["message"] = error_message
            event.save()
            return

        # Create entry in database and return
        self.logger.debug("Creating recipe in database")
        try:
            RecipeModel.objects.create(json=recipe_json)
            event.response["status"] = 200
            event.response["message"] = "Created recipe!"
            event.save()
            return
        except:
            self.logger.exception("Unable to create recipe in database")
            event.response["status"] = 500
            event.response["message"] = "Unable to create recipe in database"
            event.save()
            return


    def start_recipe(self, event, timeout_seconds=2, update_interval_seconds=0.1):
        """ Starts recipe. Gets recipe uuid and start timestamp from event
            request, checks recipe is in a mode that can be started, sends
            start recipe command, waits for recipe to start, then 
            returns response  """
        self.logger.info("Received START_RECIPE")

        # Get recipe uuid
        if "uuid" not in event.request:
            event.response["status"] = 400
            event.response["message"] = "Request does not contain `uuid`"
            event.save()
            return
        else:
            uuid = event.request["uuid"]

        # Get recipe start timestamp
        if "start_timestamp_minutes" not in event.request:
            event.response["status"] = 400
            event.response["message"] = "Request does not contain `start_timestamp_minutes`"
            event.save()
            return
        else:
            start_timestamp_minutes = event.request["start_timestamp_minutes"]

        # Check recipe is in a mode that can be started
        mode = self.recipe_mode
        if mode != Modes.NORECIPE:
            event.response["status"] = 400
            event.response["message"] = "Recipe cannot be started from {} mode".format(mode)
            event.save()
            return

        # Send start recipe command
        self.commanded_recipe_uuid = uuid
        self.commanded_recipe_mode = Modes.START

        # Wait for recipe to start
        start_time_seconds = time.time()
        while time.time() - start_time_seconds < timeout_seconds:
            if self.recipe_mode == Modes.QUEUED or self.recipe_mode == Modes.NORMAL:
                event.response["status"] = 200
                event.response["message"] = "Recipe started!"
                event.save()
                return
            time.sleep(update_interval_seconds)

        # Return timeout error
        event.response["status"] = 500
        event.response["message"] = "Start recipe event timed out"
        event.save()


    def stop_recipe(self, event, timeout_seconds=2, update_interval_seconds=0.1):
        """ Stops recipe. Checks recipe is in a mode that can be stopped, sends 
            stop command, waits for recipe to stop, returns event response. """
        self.logger.info("Received STOP_RECIPE")

        # Check recipe in a mode that can be stopped
        mode = self.recipe_mode
        self.logger.debug("Recipe currently in {} mode".format(mode))
        if mode != Modes.NORMAL and mode != Modes.PAUSE and mode != Modes.QUEUED:
            event.response["status"] = 400
            event.response["message"] = "Recipe cannot be stopped from {} mode".format(mode)
            event.save()
            return

        # Send stop command
        self.commanded_recipe_mode = Modes.STOP

        # Wait for recipe to stop
        start_time_seconds = time.time()
        while time.time() - start_time_seconds < timeout_seconds:
            if self.recipe_mode == Modes.NORECIPE:
                event.response["status"] = 200
                event.response["message"] = "Recipe stopped!"
                event.save()
                return
            time.sleep(update_interval_seconds)

        # Return timeout error
        event.response["status"] = 500
        event.response["message"] = "Stop recipe event timed out"
        event.save()