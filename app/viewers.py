# Import standard python modules
import time, logging
import json as json_

# Import python types
from typing import Dict, Tuple, Any

# Import django modules
from django.apps import apps

# Import common app funcitons
from app import models

# Import device utilities
from device.utilities import logger

# Initialize constants
APP_NAME = "app"
PERIPHERAL_RECIPIENT_TYPE = "Peripheral"
CONTROLLER_RECIPIENT_TYPE = "Controller"


class RecipeViewer:
    """Viewer for a recipe object."""

    def __init__(self, recipe_object: models.RecipeModel) -> None:
        """Initializes viewer."""
        self.recipe_dict = json_.loads(recipe_object.json)
        self.uuid = self.recipe_dict.get("uuid", "UNKNOWN")
        self.name = self.recipe_dict.get("name", "UNKNOWN")


class DeviceConfigViewer:
    """Viewer for a device config object."""

    def __init__(self, device_config_object: models.DeviceConfigModel) -> None:
        """Initializes viewer."""
        self.dict = json_.loads(device_config_object.json)
        self.uuid = self.dict.get("uuid", "UNKNOWN")
        self.name = self.dict.get("name", "UNKNOWN")


class CultivarsViewer:
    """Viewer for all cultivars."""

    def __init__(self) -> None:
        """Initializes viewer."""
        cultivars = models.CultivarModel.objects.all()
        cultivar_dict = []
        for cultivar in cultivars:
            cultivar_dict.append(json_.loads(cultivar.json))
        self.json = json_.dumps(cultivar_dict)


class CultivationMethodsViewer:
    """Viewer for all cultivation methods."""

    def __init__(self) -> None:
        """Initializes viewer."""
        cultivation_methods = models.CultivationMethodModel.objects.all()
        cultivation_methods_dict = []
        for cultivation_method in cultivation_methods:
            cultivation_methods_dict.append(json_.loads(cultivation_method.json))
        self.json = json_.dumps(cultivation_methods_dict)


class EventViewer:
    """Viewer for peripheral and controller event creation."""

    # Initialize logger
    logger = logger.Logger("EventViewer", "app")

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
        if recipient_type == PERIPHERAL_RECIPIENT_TYPE:
            manager = coordinator.peripherals.get(recipient_name)
        elif request_type == CONTROLLER_RECIPIENT_TYPE:
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
        message, status = manager.create_event(request_)

        # Successfully created event request
        self.logger.debug("Responding with ({}): {}".format(status, message))
        return message, status


class EnvironmentViewer:
    """Viewer for environment info."""

    # Initialize logger
    logger = logger.Logger("EnvironmentViewer", "app")

    def __init__(self) -> None:
        """Initialize viewer."""
        self.sensor_summary = self.get_environment_summary("sensor")
        self.actuator_summary = self.get_environment_summary("actuator")

    def get_environment_summary(self, peripheral_type: str) -> Dict[str, str]:
        """Gets environment summary of current reported --> desired value for each 
        variable in shared state."""
        self.logger.debug("Getting environment summary")

        # Get coordinator manager
        app_config = apps.get_app_config(APP_NAME)
        coordinator = app_config.coordinator

        # Get environment state dict
        environment_dict = coordinator.state.environment
        if environment_dict == None:
            return {}

        # Initialize summary dict
        summary = {}

        # Log all variables in reported values
        for variable in environment_dict[peripheral_type]["reported"]:
            # Get peripheral info
            if peripheral_type == "sensor":
                info = get_sensor_variable_info(variable)
            elif peripheral_type == "actuator":
                info = get_actuator_variable_info(variable)
            else:
                raise ValueError(
                    "`peripheral_type` must be either `sensor` or `actuator`"
                )

            if info is None or info == {}:
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
                info = get_sensor_variable_info(variable)
            elif peripheral_type == "actuator":
                info = get_actuator_variable_info(variable)
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


def get_sensor_variable_info(variable_key: str) -> Dict[str, Any]:
    """Gets sensor variable info from database."""
    if not models.SensorVariableModel.objects.filter(key=variable_key).exists():
        return {}
    else:
        variable = models.SensorVariableModel.objects.get(key=variable_key)
        variable_dict = json_.loads(variable.json)
        return variable_dict["info"]


def get_actuator_variable_info(variable_key: str) -> Dict[str, Any]:
    """Gets actuator variable info from database."""
    if not models.ActuatorVariableModel.objects.filter(key=variable_key).exists():
        return {}
    else:
        variable = models.ActuatorVariableModel.objects.get(key=variable_key)
        variable_dict = json_.loads(variable.json)
        return variable_dict["info"]
