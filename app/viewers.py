# Import standard python modules
import json as json_
import time, logging

# Import python types
from typing import Dict, Tuple, Any

# Import common app funcitons
from app.common import Common

# Import app models
from app.models import CultivarModel, CultivationMethodModel, RecipeModel

# Import app models
from app.models import EventModel

# Import device utilities
from device.utilities.events import EventRequests

# Import django app
from django.apps import apps

# Initialize vars
APP_NAME = "app"
PERIPHERAL_TYPE = "Peripheral"
CONTROLLER_TYPE = "Controller"
COORDINATOR_TYPE = "Coordinator"
RECIPE_TYPE = "Recipe"
START_RECIPE = "Start Recipe"
STOP_RECIPE = "Stop Recipe"
CREATE_RECIPE = "Create Recipe"
LOAD_DEVICE_CONFIG = "Load Device Config"


class EventViewer:

    extra = {"console_name": "Event Viewer", "file_name": "event_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    def create(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Create a new event request to any known thread."""

        # Get request parameters
        try:
            recipient = json_.loads(request["recipient"])
            recipient_type = recipient["type"]
            recipient_name = recipient["name"]
            request_ = json_.loads(request["request"])
            request_type = request_["type"]
            message = "Creating new event request for {} to {}".format(
                recipient_name, request_type
            )
            self.logger.debug(message)
        except ValueError as e:
            message = "Unable to get request parameters, invalid JSON: {}".format(e)
            self.logger.debug(message)
            return message, 400
        except KeyError as e:
            message = "Unable to get request parameters, invalid key: {}".format(e)
            self.logger.debug(message)
            return message, 400

        # Get device coordinator
        app_config = apps.get_app_config(APP_NAME)
        coordinator = app_config.coordinator

        # Check valid recipient type and get manager
        if recipient_type == PERIPHERAL_TYPE:
            manager = coordinator.peripherals.get(recipient_name)
        elif request_type == CONTROLLER_TYPE:
            manager = coordinator.controllers.get(recipient_name)
        else:
            message = "Invalid recipient type `{}`".format(recipient_type)
            self.logger.debug(message)
            return message, 400

        # Check manager exists
        if manager == None:
            message = "Invalid recipient name: `{}`".format(recipient_name)
            self.logger.debug(message)
            return message, 400

        # Send event to manager
        message, status = manager.events.create(request_)

        # Save event interaction in database
        try:
            response_dict = {"message": message, "status": status}
            event = EventModel.objects.create(
                recipient=recipient, request=request_, response=response_dict
            )
        except Exception as e:
            message = "Unable to create event in database: {}".format(e)
            return message, 500

        # Successfully created event request
        self.logger.debug("Responding with ({}): {}".format(status, message))
        return message, status


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

    def create(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Creates a recipe."""
        self.logger.info("Received create recipe request")

        # Get device coordinator
        app_config = apps.get_app_config(APP_NAME)
        coordinator = app_config.coordinator

        # Get recipe json
        try:
            json = request["json"]
        except KeyError:
            message = "Request does not contain `json`"
            return message, 400

        # Create recipe and save event interaction
        try:
            # Create recipe
            message, status = coordinator.recipe.events.create_recipe(json)

            # Save event interaction in database
            event = EventModel.objects.create(
                recipient={"type": RECIPE_TYPE},
                request={"type": CREATE_RECIPE},
                response={"message": message, "status": status},
            )

            # Successfully created recipe
            self.logger.debug("Responding with ({}): {}".format(status, message))
            return message, status

        except:
            message = "Unable to create recipe, unhandled exception"
            self.logger.exception(message)
            return message, 500

    def start(self, uuid: str, request: Dict[str, Any]) -> Tuple[str, int]:
        """Starts a recipe."""
        self.logger.info("Received start recipe request")

        # Get device coordinator
        app_config = apps.get_app_config(APP_NAME)
        coordinator = app_config.coordinator

        # Get optional timestamp parameter
        t = request.get("timestamp")
        if t != None and t != "":
            timestamp = float(t)
        else:
            timestamp = None

        # Start recipe and save event interaction
        try:
            # Start recipe
            message, status = coordinator.recipe.events.start_recipe(uuid, timestamp)

            # Save event interaction in database
            event = EventModel.objects.create(
                recipient={"type": RECIPE_TYPE},
                request={"type": START_RECIPE},
                response={"message": message, "status": status},
            )

            # Successfully started recipe
            self.logger.debug("Responding with ({}): {}".format(status, message))
            return message, status
        except:
            message = "Unable to start recipe, unhandled exception"
            self.logger.exception(message)
            return message, 500

    def stop(self):
        """Stops a recipe."""
        self.logger.info("Received stop recipe request")

        # Get device coordinator
        app_config = apps.get_app_config(APP_NAME)
        coordinator = app_config.coordinator

        # Stop recipe and save event interaction
        try:
            # Stop recipe
            message, status = coordinator.recipe.events.stop_recipe()

            # Save event interaction in database
            event = EventModel.objects.create(
                recipient={"type": RECIPE_TYPE},
                request={"type": STOP_RECIPE},
                response={"message": message, "status": status},
            )

            # Successfully stopped recipe
            self.logger.debug("Responding with ({}): {}".format(status, message))
            return message, status
        except:
            message = "Unable to stop recipe, unhandled exception"
            self.logger.exception(message)
            return message, 500


class SimpleRecipeViewer:
    def __init__(self, recipe_object):
        self.recipe_dict = json_.loads(recipe_object.json)
        self.uuid = self.recipe_dict["uuid"]
        self.name = self.recipe_dict["name"]


class DeviceConfigViewer:

    # Initialize logger
    extra = {"console_name": "DeviceConfigViewer", "file_name": "device_config_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    def parse(self, device_config_object):
        """Parses device config into dict, uuid, and name."""
        self.dict = json_.loads(device_config_object.json)
        self.uuid = self.dict["uuid"]
        self.name = self.dict["name"]

    def load(self, uuid: str, request: Dict[str, Any]) -> Tuple[str, int]:
        """Loads a recipe."""
        self.logger.info("Received load device config request")

        # Get device coordinator
        app_config = apps.get_app_config(APP_NAME)
        coordinator = app_config.coordinator

        # Load config and save event interaction
        try:
            # Start recipe
            message, status = coordinator.events.load_device_config(uuid)

            # Save event interaction in database
            event = EventModel.objects.create(
                recipient={"type": COORDINATOR_TYPE},
                request={"type": LOAD_DEVICE_CONFIG, "uuid": uuid},
                response={"message": message, "status": status},
            )

            # Successfully loaded device config
            self.logger.debug("Responding with ({}): {}".format(status, message))
            return message, status
        except Exception as e:
            message = "Unable to load config, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            return message, 500


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


class UpgradeViewer:
    upgrade_dict = {}

    def __init__(self):
        self.upgrade_dict = Common.get_upgrade_dict()
