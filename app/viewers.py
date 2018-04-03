# Import standard python modules
import json, threading, logging, time, json

# Import app models
from app.models import State

# Import device utilities
from device.utility.mode import Mode
from device.utility.event import EventRequest
from device.utility.variable import Variable

# Import common app funcitons
from app import common

# Import app models
from app.models import Event as EventModel


class SimpleRecipeViewer:
    def __init__(self, recipe_object):
        self.recipe_dict = json.loads(recipe_object.recipe_json)
        self.uuid = self.recipe_dict["uuid"]
        self.name = self.recipe_dict["name"]


class RecipeViewer:
    # Initialize logger
    extra = {"console_name":"Recipe Viewer", "file_name": "recipe_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)
    
    def __init__(self):
        """ Initialize recipe viewer. """
        self.mode = common.get_recipe_state_value("mode")
        self.recipe_name = common.get_recipe_state_value("recipe_name")
        self.recipe_uuid = common.get_recipe_state_value("recipe_uuid")
        self.start_datestring = common.get_recipe_state_value("start_datestring")
        self.percent_complete_string = common.get_recipe_state_value("percent_complete_string")
        self.time_elapsed_string = common.get_recipe_state_value("time_elapsed_string")
        self.time_elapsed_minutes = common.get_recipe_state_value("last_update_minute")
        self.time_remaining_string = common.get_recipe_state_value("time_remaining_string")
        self.time_remaining_minutes = common.get_recipe_state_value("time_remaining_minutes")
        self.current_phase = common.get_recipe_state_value("current_phase")
        self.current_cycle = common.get_recipe_state_value("current_cycle")
        self.current_environment_name = common.get_recipe_state_value("current_environment_name")


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
        return common.manage_event(event_request)      


    def stop(self):
        """ Stops a recipe. Sends stop command to event thread, waits for 
            recipe to stop, then returns response. """
        self.logger.info("Received stop recipe request")
        event_request = {"type": EventRequest.STOP_RECIPE}
        return common.manage_event(event_request)


class EnvironmentViewer:
    # Initialize logger
    extra = {"console_name":"Environment Viewer", "file_name": "environment_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    def __init__(self):
        self.sensor_summary = self.get_environment_summary("sensor")
        self.actuator_summary = self.get_environment_summary("actuator")


    def get_environment_summary(self, peripheral_type):
        """ Gets environment summary of current reported --> desired value 
            for each variable in shared state. """
        
        # Initialize summary dict
        summary = {}

        # Get environment dict
        environment_dict = common.get_environment_dict()
        if environment_dict == None:
            return summary

        # Log all variables in reported
        for variable in environment_dict[peripheral_type]["reported"]:
            name = Variable[variable]["name"]
            unit = Variable[variable]["unit"]
            reported = str(environment_dict[peripheral_type]["reported"][variable])
            if variable in environment_dict[peripheral_type]["desired"]:
                desired = str(environment_dict[peripheral_type]["desired"][variable])
            else:
                desired = "None"

            name_string = name + " (" + unit + ")"
            summary[name_string] = reported + " --> " + desired

        # Log remaining variables in desired
        for variable in environment_dict[peripheral_type]["desired"]:
            if variable not in environment_dict[peripheral_type]["reported"]:
                name = Variable[variable]["name"]
                unit = Variable[variable]["unit"]
                desired = str(environment_dict[peripheral_type]["desired"][variable])
                reported = "None"
                name_string = name + " (" + unit + ")"
                summary[name_string] = reported + " --> " + desired
        
        return summary


class DeviceViewer:
    # Initialize logger
    extra = {"console_name":"Device Viewer", "file_name": "device_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    def __init__(self):
        self.thread_modes = self.get_thread_modes()


    def get_thread_modes(self):
        thread_modes = {}
        thread_modes["Device Mode"] = common.get_device_state_value("mode")
        thread_modes["Recipe Mode"] = common.get_recipe_state_value("mode")
        return thread_modes




            # for peripheral_name in self.state.peripherals:
            #     verbose_name = self.config["peripherals"][peripheral_name]["verbose_name"]
            #     mode = self.state.peripherals[peripheral_name]["mode"]
            #     summary += "\n        {}: {}".format(verbose_name, mode)

