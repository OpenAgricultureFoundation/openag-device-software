# Import standard python modules
import threading, logging, time
import json as json_

# Import device utilities
from device.utilities.mode import Mode
from device.utilities.event import EventRequest
from device.utilities.variable import Variable

# Import common app funcitons
from app.common import Common

# Import app models
from app.models import EventModel


class RecipeViewer:
    # Initialize logger
    extra = {"console_name":"Recipe Viewer", "file_name": "recipe_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)
    
    def __init__(self):
        """ Initialize recipe viewer. """
        self.mode = Common.get_recipe_state_value("mode")
        self.recipe_name = Common.get_recipe_state_value("recipe_name")
        self.recipe_uuid = Common.get_recipe_state_value("recipe_uuid")
        self.start_datestring = Common.get_recipe_state_value("start_datestring")
        self.percent_complete_string = Common.get_recipe_state_value("percent_complete_string")
        self.time_elapsed_string = Common.get_recipe_state_value("time_elapsed_string")
        self.time_elapsed_minutes = Common.get_recipe_state_value("last_update_minute")
        self.time_remaining_string = Common.get_recipe_state_value("time_remaining_string")
        self.time_remaining_minutes = Common.get_recipe_state_value("time_remaining_minutes")
        self.current_phase = Common.get_recipe_state_value("current_phase")
        self.current_cycle = Common.get_recipe_state_value("current_cycle")
        self.current_environment_name = Common.get_recipe_state_value("current_environment_name")


    def create(self, request_dict):
        """ Creates a recipe. Gets recipe json, makes event request,  then
            returns event response. """
        self.logger.info("Received create recipe request")

        # Get recipe json
        if "json" not in request_dict:
            status=400
            response = {"message": "Request does not contain `json`"}
            return response, status
        else:
            json = request_dict["json"]

        # Make event request and return event response
        event_request = {
            "type": EventRequest.CREATE_RECIPE,
            "json": json}
        return Common.manage_event(event_request)


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
        return Common.manage_event(event_request)      


    def stop(self):
        """ Stops a recipe. Sends stop command to event thread, waits for 
            recipe to stop, then returns response. """
        self.logger.info("Received stop recipe request")
        event_request = {"type": EventRequest.STOP_RECIPE}
        return Common.manage_event(event_request)


class SimpleRecipeViewer:
    def __init__(self, recipe_object):
        self.recipe_dict = json_.loads(recipe_object.json)
        self.uuid = self.recipe_dict["uuid"]
        self.name = self.recipe_dict["name"]


class DeviceConfigurationViewer:
    def __init__(self, device_configuration_object):
        self.dict = json_.loads(device_configuration_object.json)
        self.uuid = self.dict["uuid"]
        self.name = self.dict["name"]


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
        self.logger.debug("Getting environment summary")

        # Initialize class for common functions
        common = Common()
        
        # Initialize summary dict
        summary = {}

        # Get environment dict
        environment_dict = Common.get_environment_dict()
        if environment_dict == None:
            return summary

        # Log all variables in reported values
        for variable in environment_dict[peripheral_type]["reported"]:
            # Get peripheral info
            self.logger.info("Getting peripheral info for `{}`".format(variable))
            if peripheral_type == "sensor":
                info = common.get_sensor_variable_info(variable)
            elif peripheral_type =="actuator":
                info = common.get_actuator_variable_info(variable)
            else:
                raise ValueError("`peripheral_type` must be either `sensor` or `actuator`")

            # Get peripheral name and unit
            name = info["name"]["verbose"]
            unit = info["unit"]["brief"]

            # Get reported and desired values
            reported = str(environment_dict[peripheral_type]["reported"][variable])
            if variable in environment_dict[peripheral_type]["desired"]:
                desired = str(environment_dict[peripheral_type]["desired"][variable])
            else:
                desired = "None"

            name_string = name + " (" + unit + ")"
            summary[name_string] = reported + " --> " + desired

        # Log remaining variables in desired
        for variable in environment_dict[peripheral_type]["desired"]:
            # Get peripheral info
            self.logger.debug("Getting peripheral info for `{}`".format(variable))
            if peripheral_type == "sensor":
                info = common.get_sensor_variable_info(variable)
            elif peripheral_type =="actuator":
                info = common.get_actuator_variable_info(variable)
            else:
                raise ValueError("`peripheral_type` must be either `sensor` or `actuator`")

            # Get peripheral name and unit
            name = info["name"]["verbose"]
            unit = info["unit"]["brief"]

            # Get reported and desired values
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

        # Initialize thread modes dict
        thread_modes = {}

        # Get device and recipe modes
        thread_modes["Device Mode"] = Common.get_device_state_value("mode")
        thread_modes["Recipe Mode"] = Common.get_recipe_state_value("mode")

        # Get peripheral modes if they exist
        peripheral_dict = Common.get_peripheral_dict()
        if peripheral_dict != None:
            for peripheral_name in peripheral_dict:
                individual_peripheral_dict = peripheral_dict[peripheral_name]
                thread_modes[peripheral_name] = individual_peripheral_dict["mode"]


        # Return thread modes
        return thread_modes