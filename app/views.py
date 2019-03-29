# Import standard python modules
import os, json, logging, shutil, glob

# Import django modules
from django.apps import apps
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet

from django.conf import settings

# Import django rest modules
from rest_framework import views, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import list_route, detail_route, permission_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

# Import app modules
from app import forms, models, serializers, viewers

# Import device utilities
from device.utilities import logger, system

# Initialize project root
PROJECT_ROOT = str(os.getenv("PROJECT_ROOT", ""))

# Initialize file paths
APP_NAME = "app"
# LOG_DIR = "data/logs/"
LOG_DIR = settings.LOG_DIR

IMAGE_PATH = PROJECT_ROOT + "/data/images/*.png"
# STORED_IMAGE_PATH = PROJECT_ROOT + "/data/images/stored/*.png"
STORED_IMAGE_PATH = settings.DATA_PATH + "/images/stored/*.png"

# DEVICE_CONFIG_PATH = "data/config/device.txt"
DEVICE_CONFIG_PATH = os.path.join(settings.DATA_PATH, "config", "device.txt")


##### API Views ########################################################################


class Dashboard(views.APIView):
    """Dashboard view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "dashboard.html"

    # Initialize logger
    logger = logger.Logger("DashboardView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets dashboard view."""
        self.logger.debug("Getting dashboard view")

        # Get managers
        app_config = apps.get_app_config(APP_NAME)
        coordinator = app_config.coordinator
        network = coordinator.network
        recipe = coordinator.recipe

        # Get current environment state object
        current_environment = viewers.EnvironmentViewer()  # TODO: Fix me!

        # Get stored recipe objects
        recipe_objects = models.RecipeModel.objects.all().order_by("name")
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(viewers.RecipeViewer(recipe_object))

        # Get datetime picker form
        datetime_form = forms.DateTimeForm()

        # Build and return response
        response = {
            "manager_modes": coordinator.manager_modes,
            "manager_healths": coordinator.manager_healths,
            "current_environment": current_environment,
            "recipe_mode": recipe.mode,
            "recipe_name": recipe.recipe_name,
            "recipe_uuid": recipe.recipe_uuid,
            "recipe_start_datestring": recipe.start_datestring,
            "recipe_percent_complete_string": recipe.percent_complete_string,
            "recipe_time_elapsed_string": recipe.time_elapsed_string,
            "recipe_time_remaining_string": recipe.time_remaining_string,
            "recipe_current_phase": recipe.current_phase,
            "recipe_current_cycle": recipe.current_cycle,
            "recipe_current_environment_name": recipe.current_environment_name,
            "recipes": recipes,
            "datetime_form": datetime_form,
            "network_is_connected": network.is_connected,
        }

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)


class DeviceConfig(views.APIView):
    """Device config view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "device_config.html"

    # Initialize logger
    logger = logger.Logger("DeviceConfigView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets device config view."""
        self.logger.debug("Getting device config view")

        # Get stored device config objects
        config_objects = models.DeviceConfigModel.objects.all()
        configs = []
        for config_object in config_objects:
            config = viewers.DeviceConfigViewer(config_object)
            configs.append(config)

        # Sort configs by name
        configs.sort(key=lambda x: x.name)

        # Get coordinator manager
        app_config = apps.get_app_config(APP_NAME)
        coordinator_manager = app_config.coordinator

        # Get current config
        current_config_uuid = coordinator_manager.config_uuid

        # Convert current config uuid to name
        if current_config_uuid != None:
            for config in configs:
                if config.uuid == current_config_uuid:
                    current_config_name = config.name
                    break
        else:
            current_config_name = "unspecified"

        # Build and return response
        response = {"configs": configs, "current_config_name": current_config_name}
        return Response(response)


class Logs(views.APIView):
    """Logs view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "logs.html"

    # Initialize logger
    logger = logger.Logger("LogsView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets logs view."""
        self.logger.debug("Getting logs view")

        # TODO: Clean up the method / make more DRY

        # Load device config
        if os.path.exists(DEVICE_CONFIG_PATH):
            with open(DEVICE_CONFIG_PATH) as f:
                config_name = f.readline().strip()
        else:
            config_name = "unspecified"
        device_config = json.load(open("data/devices/{}.json".format(config_name)))

        # Build peripheral logs
        logs = []
        peripherals = device_config.get("peripherals", {})
        if peripherals == None:
            peripherals = {}
        for peripheral in peripherals:

            # Get log file path
            name = peripheral["name"]
            PERIPHERAL_PATH = LOG_DIR + "peripherals/{}.log".format(name)

            # Check path exists
            if not os.path.exists(PERIPHERAL_PATH):
                continue

            # Load in log file
            log_file = open(PERIPHERAL_PATH)
            lines = log_file.readlines()

            # Return up to 500 lines
            if len(lines) < 500:
                entries = lines
            else:
                entries = lines[-500:]

            # Append to log
            logs.append({"name": name, "entries": entries})

        # Build controller logs
        controllers = device_config.get("controllers", {})
        if controllers == None:
            controllers = {}
        for controller in controllers:

            # Get log file path
            name = controller["name"]
            CONTROLLER_PATH = LOG_DIR + "controllers/{}.log".format(name)

            # Check path exists
            if not os.path.exists(CONTROLLER_PATH):
                continue

            # Load in log file
            log_file = open(CONTROLLER_PATH)
            lines = log_file.readlines()

            # Return up to 500 lines
            if len(lines) < 500:
                entries = lines
            else:
                entries = lines[-500:]

            # Append to log
            logs.append({"name": name, "entries": entries})

        # Build device top-level logs
        log_filenames = [
            "app",
            "device",
            "coordinator",
            "recipe",
            "resource",
            "iot",
            "i2c",
            "connect",
            "upgrade",
        ]

        # Load in all log files
        for name in log_filenames:

            # Get log file path
            LOG_PATH = LOG_DIR + name + ".log"

            # Check path exists
            if not os.path.exists(LOG_PATH):
                continue

            # Load log filenames
            file = open(LOG_PATH)
            lines = file.readlines()

            # Return up to 500 lines
            if len(lines) < 500:
                entries = lines
            else:
                entries = lines[-500:]

            # Append to log
            logs.append({"name": name.capitalize(), "entries": entries})

        # Return response
        return Response({"logs": logs, "logs_json": json.dumps(logs)})


class Peripherals(views.APIView):
    """Peripherals view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "peripherals.html"

    # Initialize logger
    logger = logger.Logger("PeripheralsView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets peripherals view."""
        self.logger.debug("Getting peripherals view")

        # Get stored peripheral setups
        peripheral_setups = models.PeripheralSetupModel.objects.all()
        peripheral_setups = []
        for periheral_setup in peripheral_setups:
            peripheral_setups.append(json.loads(peripheral_setups.json))

        # Build response
        response = {"peripheral_setups": peripheral_setups}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)


class Recipes(views.APIView):
    """Recipes view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "recipes.html"

    # Initialize logger
    logger = logger.Logger("RecipesView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets recipes view."""
        self.logger.debug("Getting recipes view")
        recipe_objects = models.RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(viewers.RecipeViewer(recipe_object))
        return Response({"recipes": recipes}, 200)


class Environments(views.APIView):
    """Environments view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "environments.html"

    # Initialize logger
    logger = logger.Logger("EnvironmentsView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets environments view."""
        environments = models.EnvironmentModel.objects.all().order_by("-timestamp")
        return Response({"environments": environments}, 200)


class Images(views.APIView):
    """Images view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "images.html"

    # Initialize logger
    logger = logger.Logger("ImagesView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets images view."""
        self.logger.debug("Getting image view")

        # Get absolute image paths
        non_stored_image_paths = glob.glob(IMAGE_PATH)
        stored_image_paths = glob.glob(STORED_IMAGE_PATH)
        non_stored_image_paths.sort()
        stored_image_paths.sort()
        absolute_image_paths = stored_image_paths + non_stored_image_paths

        # Convert to relative image paths
        relative_image_paths = []
        for absolute_image_path in absolute_image_paths:
            relative_image_path = absolute_image_path.replace(
                PROJECT_ROOT + "/data/images/", ""
            )
            relative_image_paths.append(relative_image_path)

        # Build response
        self.logger.debug("relative_image_paths = {}".format(relative_image_paths))
        filepaths_json = json.dumps(relative_image_paths)
        response = {"filepaths_json": filepaths_json}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)


class Resource(views.APIView):
    """Resource view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "resource.html"

    # Initialize logger
    logger = logger.Logger("ResourceView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets resource view."""
        self.logger.debug("Getting resource view")

        # Get resource manager
        app_config = apps.get_app_config(APP_NAME)
        resource_manager = app_config.coordinator.resource

        # Build response
        response = {
            "status": resource_manager.status,
            "free_disk": resource_manager.free_disk,
            "free_memory": resource_manager.free_memory,
        }

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)


class Connect(views.APIView):
    """Connect page view."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "connect.html"

    # Initialize logger
    logger = logger.Logger("ConnectView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets connect view."""
        self.logger.debug("Getting connect view")
        return Response({})


class ConnectAdvanced(views.APIView):
    """Connect advanced page view."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "connect_advanced.html"

    # Initialize logger
    logger = logger.Logger("ConnectAdvancedView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets connect advanced view."""
        self.logger.debug("Getting connect advanced view")
        return Response({})


class IoT(views.APIView):
    """Iot view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "iot.html"

    # Initialize logger
    logger = logger.Logger("IotView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets iot view."""
        self.logger.debug("Getting iot view")

        # Get iot manager
        app_config = apps.get_app_config(APP_NAME)
        iot_manager = app_config.coordinator.iot

        # Build response
        response = {
            "is_connected": iot_manager.is_connected,
            "is_registered": iot_manager.is_registered,
            "device_id": iot_manager.device_id,
            "verification_code": iot_manager.verification_code,
            "received_message_count": iot_manager.received_message_count,
            "published_message_count": iot_manager.published_message_count,
        }

        # Retun response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)


class Upgrade(views.APIView):
    """Upgrade view page."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "upgrade.html"

    # Initialize logger
    logger = logger.Logger("UpgradeView", "app")

    @method_decorator(login_required)
    def get(self, request: Request) -> Response:
        """Gets upgrade view."""
        self.logger.debug("Getting upgrade view")

        # Get upgrade manager
        app_config = apps.get_app_config(APP_NAME)
        upgrade = app_config.coordinator.upgrade

        # Build and return response
        response = {
            "status": upgrade.status,
            "current_version": upgrade.current_version,
            "upgrade_version": upgrade.upgrade_version,
            "upgrade_available": upgrade.upgrade_available,
        }
        return Response(response, 200)


##### API View Sets ####################################################################


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for interacting with state."""

    # Initialize view set
    serializer_class = serializers.StateSerializer
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("StateViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets state queryset."""
        queryset = models.StateModel.objects.all()
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    """View set for creating peripheral and controller events."""

    permission_classes = [IsAuthenticated]

    def create(self, request: Request) -> Response:
        """Creates a new event."""

        # Get parameters
        try:
            request_dict = request.data.dict()
        except Exception as e:
            message = "Unable to create request dict: {}".format(e)
            return Response(message, 400)

        # Get request parameters
        event_viewer = viewers.EventViewer()
        message, status = event_viewer.create(request_dict)
        response_dict = {"message": message}
        return Response(response_dict, status=status)


class EnvironmentViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for environment interactions."""

    # Initialize view set parameters
    serializer_class = serializers.EnvironmentSerializer
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("EnvironmentViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets environments queryset."""
        queryset = models.EnvironmentModel.objects.all()
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """View set for recipe interactions."""

    # Initialize view set parameters
    serializer_class = serializers.RecipeSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("RecipeViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets recipe queryset."""
        queryset = models.RecipeModel.objects.all().order_by("name")
        return queryset

    def create(self, request: Request) -> Response:
        """Creates a recipe."""
        self.logger.debug("Creating recipe")

        # Initialize permission classes
        permission_classes = [IsAuthenticated, IsAdminUser]

        # Get recipe json
        try:
            request_dict = request.data.dict()
            recipe_json = request_dict["json"]
        except KeyError as e:
            message = "Unable to create recipe, {} is required".format(e)
            return Response({"message": message}, 400)

        # Get recipe manager
        app_config = apps.get_app_config(APP_NAME)
        recipe_manager = app_config.coordinator.recipe

        # Create recipe
        message, status = recipe_manager.create_recipe(recipe_json)

        # Build response
        response = {"message": message}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)

    @detail_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def start(self, request: Request, uuid: str) -> Response:
        """Starts a recipe."""
        self.logger.debug("Starting recipe")
        self.logger.debug("request type = {}".format(type(request)))

        # Get optional timestamp parameter
        request_dict = request.data.dict()
        timestamp_ = request_dict.get("timestamp")

        # Ensure timestamp format
        if timestamp_ != None and timestamp_ != "":
            timestamp = float(timestamp_)
        else:
            timestamp = None  # type: ignore

        # Get recipe manager
        app_config = apps.get_app_config(APP_NAME)
        recipe_manager = app_config.coordinator.recipe

        # Start recipe
        message, status = recipe_manager.start_recipe(uuid, timestamp)

        # Build response
        response = {"message": message}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        res = Response(response, status)
        self.logger.debug("res type = {}".format(type(res)))
        return Response(response, status)

    @list_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def stop(self, request: Request) -> Response:
        """Stops a recipe."""
        self.logger.debug("Stopping recipe")

        # Get recipe manager
        app_config = apps.get_app_config(APP_NAME)
        recipe_manager = app_config.coordinator.recipe

        # Stop recipe
        message, status = recipe_manager.stop_recipe()

        # Build response
        response = {"message": message}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)


class RecipeTransitionViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for recipe transaction interactions."""

    # Initialize view set parameters
    serializer_class = serializers.RecipeTransitionSerializer

    # Initialize logger
    logger = logger.Logger("RecipeTransitionViewSet", "app")

    @method_decorator(login_required)
    def get_queryset(self) -> QuerySet:
        """Gets recipe transition queryset."""
        queryset = models.RecipeTransitionModel.objects.all()
        return queryset


class CultivarViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for cultivar interactions."""

    # Initialize class parameters
    serializer_class = serializers.CultivarSerializer
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("CultivarViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets cultivar queryset."""
        queryset = models.CultivarModel.objects.all()
        return queryset


class CultivationMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for interacting with cultivation methods."""

    # Initialize class parameters
    serializer_class = serializers.CultivationMethodSerializer
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("CultivationMethodViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets cultivation methods queryset."""
        queryset = models.CultivationMethodModel.objects.all()
        return queryset


class SensorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for interacting with sensor variables."""

    # Initialize view set parameters
    serializer_class = serializers.SensorVariableSerializer
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("SensorVariableViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets sensor variable queryset."""
        queryset = models.SensorVariableModel.objects.all()
        return queryset


class ActuatorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for interacting with actuator variables."""

    # Initialize view set parameters
    serializer_class = serializers.ActuatorVariableSerializer
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("ActuatorVariableViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets actuator variable queryset."""
        queryset = models.ActuatorVariableModel.objects.all()
        return queryset


class PeripheralSetupViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for interacting with peripheral setups."""

    # Initialize view set parameters
    serializer_class = serializers.PeripheralSetupSerializer
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("PeripheralSetupViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets peripheral setup queryset."""
        queryset = models.PeripheralSetupModel.objects.all()
        return queryset


class DeviceConfigViewSet(viewsets.ModelViewSet):
    """View set for interacting with device configs."""

    # Initialize view set parameters
    serializer_class = serializers.DeviceConfigSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    # Initialize logger
    logger = logger.Logger("DeviceConfigViewSet", "app")

    def get_queryset(self) -> QuerySet:
        """Gets device config queryset."""
        queryset = models.DeviceConfigModel.objects.all()
        return queryset

    @detail_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def load(self, request: Request, uuid: str) -> Response:
        """Loads a device config."""
        self.logger.debug("Loading device config")

        # TODO: This throws errors -- fix them...

        # Get coordinator manager
        app_config = apps.get_app_config(APP_NAME)
        coordinator_manager = app_config.coordinator

        # Load config
        message, status = coordinator_manager.load_device_config(uuid)

        # Build response
        response = {"message": message}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)


class SystemViewSet(viewsets.ModelViewSet):
    """View set for system interactions."""

    # Initialize logger
    logger = logger.Logger("SystemViewSet", "app")

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def info(self, request: Request) -> Response:
        """Gets system info."""
        self.logger.debug("Getting system info")

        try:
            response = {
                "message": "Successfully got system info",
                "platform": os.getenv("PLATFORM"),
                "serial_number": os.getenv("SERIAL_NUMBER"),
                "remote_device_ui_url": os.getenv("REMOTE_DEVICE_UI_URL"),
                "is_wifi_enabled": os.getenv("IS_WIFI_ENABLED") == "true",
            }
            self.logger.debug("Returning response: {}".format(response))
            return Response(response, 200)
        except Exception as e:
            message = "Unable to get system info, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return Response({"message": message}, 500)


class NetworkViewSet(viewsets.ModelViewSet):
    """View set for network interactions."""

    # Initialize logger
    logger = logger.Logger("NetworkViewSet", "app")

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def info(self, request: Request) -> Response:
        """Gets network info."""
        self.logger.debug("Getting network info")

        # Get network manager
        app_config = apps.get_app_config(APP_NAME)
        network_manager = app_config.coordinator.network

        # Build response
        response = {
            "message": "Successfully got network info",
            "is_connected": network_manager.is_connected,
            "ip_address": network_manager.ip_address,
            "wifi_ssids": network_manager.wifi_ssids,
        }

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def joinwifi(self, request: Request) -> Response:
        """Joins wifi network."""
        self.logger.debug("Joining wifi")

        # Get network manager
        app_config = apps.get_app_config(APP_NAME)
        network_manager = app_config.coordinator.network

        # Join wifi
        try:
            message, status = network_manager.join_wifi(request.data.dict())
        except Exception as e:
            message = "Unable to join wifi, unhandled exception: `{}`".format(type(e))
            self.logger.exception(message)
            status = 500

        # Build and return response
        response = {"message": message}
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def joinwifiadvanced(self, request: Request) -> Response:
        """Joins wifi network with advanced config."""
        self.logger.debug("Joining wifi advanced")

        # Get network manager
        app_config = apps.get_app_config(APP_NAME)
        network_manager = app_config.coordinator.network

        # Join wifi advanced
        try:
            message, status = network_manager.join_wifi_advanced(request.data.dict())
        except Exception as e:
            message = "Unable to join wifi advanced, unhandled "
            "exception: `{}`".format(type(e))
            self.logger.exception(message)
            status = 500

        # Build and return response
        response = {"message": message}
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def deletewifis(self, request: Request) -> Response:
        """Deletes stored wifi access points."""
        self.logger.debug("Deleting wifi access points")

        # Get network manager
        app_config = apps.get_app_config(APP_NAME)
        network_manager = app_config.coordinator.network

        # Delete wifis
        try:
            message, status = network_manager.delete_wifis()
        except Exception as e:
            message = "Unable to delete wifis, unhandled "
            "exception: `{}`".format(type(e))
            status = 500

        # Build and return response
        response = {"message": message}
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def disableraspiaccesspoint(self, request: Request) -> Response:
        """Disables raspberry pi access point."""
        self.logger.debug("Disabling raspberry pi access point")

        # Get network manager
        app_config = apps.get_app_config(APP_NAME)
        network_manager = app_config.coordinator.network
        iot_manager = app_config.coordinator.iot

        # Disable raspi access point
        try:
            message, status = network_manager.disable_raspi_access_point()
        except Exception as e:
            message = "Unable to disable raspi access point, unhandled exception: `{}`".format(
                type(e)
            )
            self.logger.exception(message)
            status = 500

        # Build and return response
        response = {"message": message}
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)


class IotViewSet(viewsets.ModelViewSet):
    """View set for iot interactions."""

    # Initialize logger
    logger = logger.Logger("IotViewSet", "app")

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def info(self, request: Request) -> Response:
        """Gets iot info."""
        self.logger.debug("Getting iot info")

        # Get iot manager
        app_config = apps.get_app_config(APP_NAME)
        iot_manager = app_config.coordinator.iot

        # Build response
        response = {
            "message": "Successfully got iot info",
            "is_registered": iot_manager.is_registered,
            "is_connected": iot_manager.is_connected,
            "verification_code": iot_manager.verification_code,
        }

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def register(self, request: Request) -> Response:
        """Registers device with google cloud platform."""
        self.logger.debug("Registering device with iot cloud")

        # Get iot manager
        app_config = apps.get_app_config(APP_NAME)
        iot_manager = app_config.coordinator.iot

        # Register device
        iot_manager.register()

        # Build response
        response = {"message": "Successfully registered"}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def reregister(self, request: Request) -> Response:
        """Unregisters device with google cloud platform."""
        self.logger.debug("Re-registering device with iot cloud")

        # Get iot manager
        app_config = apps.get_app_config(APP_NAME)
        iot_manager = app_config.coordinator.iot

        # Unregister device
        message, status = iot_manager.reregister()

        # Build response
        response = {"message": message}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)


class UpgradeViewSet(viewsets.ModelViewSet):
    """View set for interactions with device upgrades."""

    # Initialize logger
    logger = logger.Logger("UpgradeViewSet", "app")

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def check(self, request: Request) -> Response:
        """Checks for software upgrades."""
        self.logger.debug("Checking for software upgrades")

        # Get upgrade manager
        app_config = apps.get_app_config(APP_NAME)
        upgrade = app_config.coordinator.upgrade

        # Check for upgrades
        message, status = upgrade.check()

        # Build response message
        response = {
            "message": message,
            "status": upgrade.status,
            "upgrade_available": upgrade.upgrade_available,
            "current_version": upgrade.current_version,
            "upgrade_version": upgrade.upgrade_version,
        }

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def upgrade(self, request: Request) -> Response:
        """Upgrades software."""
        self.logger.debug("Upgrading software")

        # Get upgrade manager
        app_config = apps.get_app_config(APP_NAME)
        upgrade = app_config.coordinator.upgrade

        # Upgrade software
        message, status = upgrade.upgrade()

        # Build response message
        response = {
            "message": message,
            "status": upgrade.status,
            "upgrade_available": upgrade.upgrade_available,
            "current_version": upgrade.current_version,
            "upgrade_version": upgrade.upgrade_version,
        }

        # Return response
        self.logger.info("Returning response: {}".format(response))
        return Response(response, status)


def change_password(request: Request) -> render:
    """Changes password."""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Your password was successfully updated!")
            return redirect("change_password")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


# just for MW demo
# ------------------------------------------------------------------------------
class LEDViewSet(viewsets.ModelViewSet):
    # Initialize logger
    logger = logger.Logger("LEDViewSet", "app")

    # --------------------------------------------------------------------------
    def send_event(self, etype: str, value: str = None) -> Response:
        v = ""
        if value is not None and value is not "":
            v = ',"value":"' + value + '"'

        edict = {
            "recipient": '{"type":"Peripheral","name":"LEDPanel-Top"}',
            "request": '{"type":"' + etype + '"' + v + "}",
        }

        event_viewer = viewers.EventViewer()
        message, status = event_viewer.create(edict)

        response = {"message": message}
        return Response(response, status=status)

    # --------------------------------------------------------------------------
    # Send LED peripheral the manual mode command
    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def manual(self, request: Request) -> Response:
        self.logger.debug("Put LED in manual mode via REST API.")
        return self.send_event(etype="Enable Manual Mode")

    # --------------------------------------------------------------------------
    # Send LED peripheral the reset event
    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def reset(self, request: Request) -> Response:
        self.logger.debug("Reset LED.")
        return self.send_event(etype="Reset")

    # --------------------------------------------------------------------------
    # Send LED peripheral the set channel event
    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def set_channel(self, request: Request) -> Response:

        # Get parameters
        try:
            rdict = request.data
        except Exception as e:
            message = "Unable to create request dict: {}".format(e)
            return Response(message, 400)
        self.logger.debug("debubrob rdict={}".format(rdict))

        channel = rdict.get("channel", "B")
        percent = rdict.get("percent", "50")
        self.logger.debug(
            "Set LED channel via REST API, channel={}, percent={}".format(
                channel, percent
            )
        )
        # set channel event: B,50
        val = "{},{}".format(channel, percent)
        return self.send_event(etype="Set Channel", value=val)

    # --------------------------------------------------------------------------
    # Send LED peripheral the Turn On event
    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def turn_on(self, request: Request) -> Response:
        self.logger.debug("Turn On LED.")
        return self.send_event(etype="Turn On")

    # --------------------------------------------------------------------------
    # Send LED peripheral the Turn Off event
    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def turn_off(self, request: Request) -> Response:
        self.logger.debug("Turn Off LED.")
        return self.send_event(etype="Turn Off")

    # --------------------------------------------------------------------------
    # Send LED peripheral the fade event
    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def fade(self, request: Request) -> Response:
        self.logger.debug("Fade LED.")
        return self.send_event(etype="Fade")
