# Import standard python modules
import json, threading, logging, time, json

# Import app models
from app.models import State

# Import device utilities
from device.utility.mode import Mode
from device.utility.event import EventRequest

# Import app models
from app.models import Event as EventModel


class Recipe():
    # Initialize logger
    extra = {"console_name":"Recipe Viewer", "file_name": "recipe_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    
    def __init__(self):
        """ Initialize recipe viewer. """
        self.mode = self.get_recipe_state_value("mode")
        self.json = self.get_recipe_state_value("recipe")
        self.name = self.get_recipe_state_value("name")
        self.started = self.get_recipe_state_value("start_datestring")
        self.progress = self.get_recipe_state_value("percent_complete_string")
        self.time_elapsed = self.get_recipe_state_value("time_elapsed_string")
        self.time_remaining = self.get_recipe_state_value("time_remaining_string")
        self.current_phase = self.get_recipe_state_value("current_phase")
        self.current_cycle = self.get_recipe_state_value("current_cycle")
        self.current_environment = self.get_recipe_state_value("current_environment_name")
        self.progress = self.get_recipe_state_value("recipe")


    def create(self, request_dict):
        """ Creates a recipe. Gets recipe json, makes event request,  then
            returns event response. """
        self.logger.info("Received create recipe request")

        # Get recipe json
        if "recipe_json" not in request_dict:
            status=400
            response = {"message": "Request does not contain `recipe_json`"}
            return response, status
        else:
            recipe_json = request_dict["recipe_json"]

        # Make event request and return event response
        event_request = {
            "type": EventRequest.CREATE_RECIPE,
            "recipe_json": recipe_json}
        return self.manage_event(event_request)


    def start(self, request_dict, pk):
        """ Start a recipe. Sends start recipe command to event thread, waits 
        for recipe to start, then returns response. """
        self.logger.info("Received stop recipe request")

        # Get optional recipe start timestamp
        if "start_timestamp_minutes" not in request_dict:
            start_timestamp_minutes = None
        else:
            start_timestamp_minutes = request_dict["start_timestamp_minutes"]

        # Make event request and return event response
        event_request = {
            "type": EventRequest.START_RECIPE,
            "uuid": pk,
            "start_timestamp_minutes": start_timestamp_minutes}
        return self.manage_event(event_request)      


    def stop(self):
        """ Stops a recipe. Sends stop command to event thread, waits for 
            recipe to stop, then returns response. """
        self.logger.info("Received stop recipe request")
        event_request = {"type": EventRequest.STOP_RECIPE}
        return self.manage_event(event_request)


    def manage_event(self, event_request, timeout_seconds=3, update_interval_seconds=0.1):
        """ Manages an event request. Creates new event in database, waits for 
            event response, returns event response or timeout error. """

        # Create event in database
        event = EventModel.objects.create(request=event_request)

        # Wait for response
        start_time_seconds = time.time()
        while time.time() - start_time_seconds < timeout_seconds:
            event_response = EventModel.objects.get(pk=event.id).response
            if event_response != None:
                status = event_response["status"]
                response = {"message": event_response["message"]}
                return response, status
            # Check for response every 100ms
            time.sleep(update_interval_seconds)

        # Return timeout error
        status=500
        response = {"message": "Event response timed out"}
        return response, status


    def get_recipe_state_value(self, key):
        """ Gets recipe state value for key current recipe state. """

        # Get recipe state dict
        if not State.objects.filter(pk=1).exists():
            return None
        else:
            state = State.objects.get(pk=1)
            recipe_state_dict = json.loads(state.recipe)
        
        # Get value for key
        if key in recipe_state_dict:
            return recipe_state_dict[key]
        else:
            return None

