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

# TODO: Clean up or remove environment viewer


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
