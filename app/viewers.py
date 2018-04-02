# Import standard python modules
import json, threading, logging, time, json
import uuid as uuid_module

# Import app models
from app.models import State

# Import device utilities
from device.utility.mode import Mode
from device.utility.format import Format
from device.utility.event import EventRequest
from device.utility.event import EventResponse

# Import app models
from app.models import Recipe as RecipeModel
from app.models import Event as EventModel


class Recipe():
    # Initialize logger
    extra = {"console_name":"Recipe Viewer", "file_name": "recipe_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    try:
        # TODO: Stop being lazy and do this the right way...
        state = State.objects.filter(pk=1).first()
        dict_ = json.loads(state.recipe)
        json = dict_["recipe"]
        name = json["name"]
        started = dict_["start_datestring"]
        progress = dict_["percent_complete_string"]
        time_elapsed = dict_["time_elapsed_string"]
        time_remaining = dict_["time_remaining_string"]
        current_phase = dict_["current_phase"]
        current_cycle = dict_["current_cycle"]
        current_environment = dict_["current_environment_name"]
    except:
        self.logger.exception("Unable to initialize recipe viewer")
        self.logger.critical("Unable to initialize recipe viewer")


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


    def create(self, request):
        """ Creates a recipe. Validates json, creates entry in database, then 
            returns response. """
        self.logger.info("Received create recipe request")
        event_request = {
            "type": EventRequest.CREATE_RECIPE,
            "recipe_json": request["recipe_json"]}
        return self.manage_event(event_request)


    def stop(self):
        """ Stops a recipe. Sends stop command to recipe thread, waits for 
            recipe to stop, then returns response. """
        self.logger.info("Received stop recipe request")
        event_request = {"type": EventRequest.STOP_RECIPE}
        return self.manage_event(event_request)
