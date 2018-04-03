# Import python modules
import logging, time, threading, json, os, sys

# Import device utilities
from device.utility.mode import Mode
from device.utility.error import Error
from device.utility.format import Format
from device.utility.event import EventRequest
from device.utility.event import EventResponse

# Import database models
from app.models import Event as EventModel
from app.models import Recipe as RecipeModel

# Import common functions
from device.common import Common


class Event:
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
        self.mode = Mode.INIT
        self.error = Error.NONE


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
            event.response["type"] = EventResponse.INVALID_REQUEST
            event.save()
            return
        
        # Handle event
        if event.request["type"] == EventRequest.CREATE_RECIPE:
            self.create_recipe(event)
        elif event.request["type"] == EventRequest.START_RECIPE:
            self.start_recipe(event)
        elif event.request["type"] == EventRequest.STOP_RECIPE:
            self.stop_recipe(event)
        else:
            event.response["type"] = EventResponse.INVALID_EVENT
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

        # Validate json
        message, status = self.validate(recipe_json)
        if status != 200:
            self.logger.info("Recipe is invalid: {}".format(message))
            event.response["status"] = status
            event.response["message"] = message
            event.save()
            return

        # Create entry in database and return
        self.logger.debug("Creating recipe in database")
        try:
            RecipeModel.objects.create(recipe_json=recipe_json)
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
        if mode != Mode.NORECIPE:
            event.response["status"] = 400
            event.response["message"] = "Recipe cannot be started from {} mode".format(mode)
            event.save()
            return

        # Send start recipe command
        self.commanded_recipe_uuid = uuid
        self.commanded_recipe_mode = Mode.START

        # Wait for recipe to start
        start_time_seconds = time.time()
        while time.time() - start_time_seconds < timeout_seconds:
            if self.recipe_mode == Mode.QUEUED or self.recipe_mode == Mode.NORMAL:
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
        if mode != Mode.NORMAL and mode != Mode.PAUSE and mode != Mode.QUEUED:
            event.response["status"] = 400
            event.response["message"] = "Recipe cannot be stopped from {} mode".format(mode)
            event.save()
            return

        # Send stop command
        self.commanded_recipe_mode = Mode.STOP

        # Wait for recipe to stop
        start_time_seconds = time.time()
        while time.time() - start_time_seconds < timeout_seconds:
            if self.recipe_mode == Mode.NORECIPE:
                event.response["status"] = 200
                event.response["message"] = "Recipe stopped!"
                event.save()
                return
            time.sleep(update_interval_seconds)

        # Return timeout error
        event.response["status"] = 500
        event.response["message"] = "Stop recipe event timed out"
        event.save()


    def validate(self, recipe_json):
        """ Validates recipe json. """
        self.logger.info("Validating recipe")

        # Create recipe dict
        recipe_dict = json.loads(recipe_json)

        # Verify uuid uniqueness if supplied
        if "uuid" in recipe_dict and self.uuid_exists(recipe_dict["uuid"]):
            status = 400
            response = {"message": "Recipe uuid already exists"}
            return response, status

        """ TODO: Verify values and/or value types (e.g. date is formatted 
            properly, name is a string and not a list) """

        # Verify format key
        if "format" not in recipe_dict or recipe_dict["format"] == None:
            status = 400
            response = {"message": "Recipe json does not contain `format`"}
            return response, status
        
        # Get format type
        if "type" not in recipe_dict["format"] or recipe_dict["format"]["type"] == None:
            status = 400
            response = {"message": "Recipe json does not contain `type`"}
            return response, status
        else:
            format_type = recipe_dict["format"]["type"]

        # Get format version 
        if "version" not in recipe_dict["format"] or recipe_dict["format"]["version"] == None:
            status = 400
            response = {"message": "Recipe json does not contain `version`"}
            return response, status
        else:
            format_version = recipe_dict["format"]["version"]

        # Verify format specific parameters
        if format_type == "phased-environment" and format_version == Format.VERSION_1:
            # Verify phased-environment v1 keys 
            if "name" not in recipe_dict or recipe_dict["name"] == None:
                status = 400
                response = {"message": "Recipe json does not contain `name`"}
                return response, status
            if "date_created" not in recipe_dict or recipe_dict["date_created"] == None:
                status = 400
                response = {"message": "Recipe json does not contain `date_created`"}
                return response, status
            if "author" not in recipe_dict or recipe_dict["author"] == None:
                status = 400
                response = {"message": "Request json does not contain `author`"}
                return response, status
            if "seeds" not in recipe_dict or recipe_dict["seeds"] == None:
                status = 400
                response = {"message": "Request json does not contain `seeds`"}
                return response, status

            # Verify able to generate transitions
            common = Common()
            phase_transitions, error_message = common.generate_recipe_transitions(recipe_dict)
            if phase_transitions == None:
                status = 400
                response = {"message": error_message}
                return response, status
        else: 
            # Unsupported format / version
            status = 400
            response = {"message": "Recipe format / version not supported"}
            return response, status

        # Return valid recipe format
        status = 200
        response = {"message": "Recipe is valid!"}
        return response, status


    def uuid_exists(self, uuid):
        """ Checks if uuid is unique. """
        self.logger.debug("Checking if uuid is unique")
        return RecipeModel.objects.filter(uuid=uuid).exists()
        