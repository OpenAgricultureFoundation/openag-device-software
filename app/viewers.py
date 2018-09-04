# Import standard python modules
import json as json_
import time, logging

# Import common app funcitons
from app.common import Common
from app.models import CultivarModel
from app.models import CultivationMethodModel

# Import app models
from app.models import EventModel

# Import device utilities
from device.utilities.events import EventRequests


class EventViewer:

    def create(self, request):

        # Get request parameters
        try:
            recipient = json_.loads(request["recipient"])
            request_ = json_.loads(request["request"])
        except ValueError as e:
            message = "Unable to get request parameters, invalid JSON: {}".format(e)
            return message, 400
        except KeyError as e:
            message = "Unable to get request parameters, invalid key: {}".format(e)
            return message, 400

        # Create event in database
        try:
            event = EventModel.objects.create(recipient=recipient, request=request_)
        except Exception as e:
            message = "Unable to create event in database: {}".format(e)
            return message, 500

        # Wait for response
        start_time = time.time()
        while True:

            # Check response status
            event = EventModel.objects.get(id=event.id)
            if event.response != None:
                break

            # Check for timeout
            if time.time() - start_time > 10:  # 10 second timeout:
                event.response = {
                    "message": "Critical error, response timed out", "status": 500
                }
                event.save()
                break

            # Update every 100ms
            time.sleep(0.1)

        # Return response
        event = EventModel.objects.get(id=event.id)
        return event.response["message"], event.response["status"]


class RecipeViewer:
    # Initialize logger
    extra = {"console_name": "Recipe Viewer", "file_name": "recipe_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    def __init__(self):
        """ Initialize recipe viewer. """
        self.mode = Common.get_recipe_state_value("mode")
        self.recipe_name = Common.get_recipe_state_value("recipe_name")
        self.recipe_uuid = Common.get_recipe_state_value("recipe_uuid")
        self.start_datestring = Common.get_recipe_state_value("start_datestring")
        self.percent_complete_string = Common.get_recipe_state_value(
            "percent_complete_string"
        )
        self.time_elapsed_string = Common.get_recipe_state_value("time_elapsed_string")
        self.time_elapsed_minutes = Common.get_recipe_state_value("last_update_minute")
        self.time_remaining_string = Common.get_recipe_state_value(
            "time_remaining_string"
        )
        self.time_remaining_minutes = Common.get_recipe_state_value(
            "time_remaining_minutes"
        )
        self.current_phase = Common.get_recipe_state_value("current_phase")
        self.current_cycle = Common.get_recipe_state_value("current_cycle")
        self.current_environment_name = Common.get_recipe_state_value(
            "current_environment_name"
        )

    def create(self, request_dict):
        """ Creates a recipe. Gets recipe json, makes event request,  then
            returns event response. """
        self.logger.info("Received create recipe request")

        # Get recipe json
        if "json" not in request_dict:
            status = 400
            response = {"message": "Request does not contain `json`"}
            return response, status
        else:
            json = request_dict["json"]

        # Make event request and return event response
        event_request = {"type": EventRequests.CREATE_RECIPE, "json": json}
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
            "type": EventRequests.START_RECIPE,
            "uuid": pk,
            "start_timestamp_minutes": start_timestamp_minutes,
        }
        return Common.manage_event(event_request)

    def stop(self):
        """ Stops a recipe. Sends stop command to event thread, waits for 
            recipe to stop, then returns response. """
        self.logger.info("Received stop recipe request")
        event_request = {"type": EventRequests.STOP_RECIPE}
        return Common.manage_event(event_request)


class SimpleRecipeViewer:

    def __init__(self, recipe_object):
        self.recipe_dict = json_.loads(recipe_object.json)
        self.uuid = self.recipe_dict["uuid"]
        self.name = self.recipe_dict["name"]


class DeviceConfigViewer:

    def __init__(self, device_config_object):
        self.dict = json_.loads(device_config_object.json)
        self.uuid = self.dict["uuid"]
        self.name = self.dict["name"]


class CultivarsViewer:

    def __init__(self):
        cultivars = CultivarModel.objects.all()
        cultivar_dict = []
        for cultivar in cultivars:
            cultivar_dict.append(json_.loads(cultivar.json))
        self.json = json_.dumps(cultivar_dict)


class CultivationMethodsViewer:

    def __init__(self):
        cultivation_methods = CultivationMethodModel.objects.all()
        cultivation_methods_dict = []
        for cultivation_method in cultivation_methods:
            cultivation_methods_dict.append(json_.loads(cultivation_method.json))
        self.json = json_.dumps(cultivation_methods_dict)


class EnvironmentViewer:
    # Initialize logger
    extra = {"console_name": "Environment Viewer", "file_name": "environment_viewer"}
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
            if peripheral_type == "sensor":
                info = common.get_sensor_variable_info(variable)
            elif peripheral_type == "actuator":
                info = common.get_actuator_variable_info(variable)
            else:
                raise ValueError(
                    "`peripheral_type` must be either `sensor` or `actuator`"
                )

            if info is None:
                continue

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

            # Skip over repeated variables
            if variable in environment_dict[peripheral_type]["reported"]:
                continue

            # Get peripheral info
            if peripheral_type == "sensor":
                info = common.get_sensor_variable_info(variable)
            elif peripheral_type == "actuator":
                info = common.get_actuator_variable_info(variable)
            else:
                raise ValueError(
                    "`peripheral_type` must be either `sensor` or `actuator`"
                )

            if info is None:
                continue

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
    extra = {"console_name": "Device Viewer", "file_name": "device_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    def __init__(self):
        self.modes, self.healths = self.get_thread_parameters()

    def get_thread_parameters(self):

        # Initialize thread modes dict
        modes = {}
        healths = {}

        # Get device and recipe modes
        modes["Device Mode"] = Common.get_device_state_value("mode")
        modes["Recipe Mode"] = Common.get_recipe_state_value("mode")

        # Get peripherals mode and health if they exist
        peripheral_dict = Common.get_peripheral_dict()
        if peripheral_dict != None:
            for peripheral_name in peripheral_dict:
                individual_peripheral_dict = peripheral_dict[peripheral_name]
                modes[peripheral_name] = individual_peripheral_dict.get("mode", None)

                # TODO: re-instate this
                healths[peripheral_name] = individual_peripheral_dict.get(
                    "health", None
                )

        # Return thread modes
        return modes, healths


class IoTViewer:
    iot_dict = {}

    def __init__(self):
        self.iot_dict = Common.get_iot_dict()


class ResourceViewer:
    resource_dict = {}

    def __init__(self):
        self.resource_dict = Common.get_resource_dict()


class ConnectViewer:
    connect_dict = {}

    def __init__(self):
        self.connect_dict = Common.get_connect_dict()
