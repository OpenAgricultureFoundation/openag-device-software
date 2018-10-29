# Import standard python modules
import os, json, logging, shutil, glob

# Import django modules
from django.apps import apps
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

# Import django rest framework modules
from rest_framework import views, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route, permission_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

# Import app elements
from app import forms, models, serializers, viewers, common

# Import device utilities
from device.utilities import logger, system

# Initialize file paths
APP_NAME = "app"
LOG_DIR = "data/logs/"
IMAGE_DIR = "data/images/"
STORED_IMAGE_DIR = IMAGE_DIR + "stored/"
STORED_IMAGES_PATH = "data/images/stored/*.png"


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows state to be viewed."""

    serializer_class = serializers.StateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.StateModel.objects.all()
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    """API endpoint that allows events to be viewed and created."""

    serializer_class = serializers.EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.EventModel.objects.all()
        return queryset

    def create(self, request):
        """ API endpoint to create an event. """

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
    """ API endpoint that allows events to be viewed. """

    serializer_class = serializers.EnvironmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.EnvironmentModel.objects.all()
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """API endpoints that allow recipes to be started, stopped, created, and viewed."""

    serializer_class = serializers.RecipeSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.RecipeModel.objects.all().order_by("name")
        return queryset

    def create(self, request):
        """ API endpoint to create a recipe. """
        permission_classes = [IsAuthenticated, IsAdminUser]
        recipe_viewer = viewers.RecipeViewer()
        response, status = recipe_viewer.create(request.data)
        return Response(response, status)

    @detail_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def start(self, request, uuid):
        """API endpoint to start a recipe."""
        recipe_viewer = viewers.RecipeViewer()
        response, status = recipe_viewer.start(uuid, request.data)  # was data.dict()
        return Response(response, status)

    @list_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def stop(self, request):
        """ API endpoint to stop a recipe. """
        recipe_viewer = viewers.RecipeViewer()
        response, status = recipe_viewer.stop()
        return Response(response, status)


class RecipeTransitionViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows recipe transitions to be viewed. """

    serializer_class = serializers.RecipeTransitionSerializer

    @method_decorator(login_required)
    def get_queryset(self):
        queryset = models.RecipeTransitionModel.objects.all()
        return queryset


class CultivarViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows cultivars to be viewed. """

    serializer_class = serializers.CultivarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.CultivarModel.objects.all()
        return queryset


class CultivationMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows cultivation methods to be viewed. """

    serializer_class = serializers.CultivationMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.CultivationMethodModel.objects.all()
        return queryset


class SensorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows sensor variables to be viewed. """

    serializer_class = serializers.SensorVariableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.SensorVariableModel.objects.all()
        return queryset


class ActuatorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows actuator variables to be viewed. """

    serializer_class = serializers.ActuatorVariableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.ActuatorVariableModel.objects.all()
        return queryset


class PeripheralSetupViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows peripheral setups to be viewed. """

    serializer_class = serializers.PeripheralSetupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.PeripheralSetupModel.objects.all()
        return queryset


class Home(views.APIView):
    """UI page for home."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "home.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get internet connectivity. TODO: This should access connect manager through
        # coordinator manager. See viewers.py for example implementation
        network_is_connected = network.is_connected()

        from django.shortcuts import redirect, reverse

        if network_is_connected:
            return redirect(reverse("dashboard"))
        else:
            return redirect(reverse("connect"))

        # # Build and return response
        # response = {"valid_internet_connection": network_is_connected}
        # return Response()


class Dashboard(views.APIView):
    """UI page for dashboard."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "dashboard.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get current device state object
        current_device = viewers.DeviceViewer()

        # Get current environment state object
        current_environment = viewers.EnvironmentViewer()

        # Get current recipe state object
        current_recipe = viewers.RecipeViewer()

        # Get stored recipe objects
        recipe_objects = models.RecipeModel.objects.all().order_by("name")
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(viewers.SimpleRecipeViewer(recipe_object))

        # Get datetime picker form
        datetime_form = forms.DateTimeForm()

        # Get network manager
        app_config = apps.get_app_config(APP_NAME)
        network_manager = app_config.coordinator.network

        # Get network connection status
        network_is_connected = network_manager.is_connected

        # Build and return response
        response = {
            "current_device": current_device,
            "current_environment": current_environment,
            "current_recipe": current_recipe,
            "recipes": recipes,
            "datetime_form": datetime_form,
            "valid_internet_connection": network_is_connected,
        }
        return Response(response)


class DeviceConfig(views.APIView):
    """UI page for managing device config."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "device_config.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get stored device config objects
        config_objects = models.DeviceConfigModel.objects.all()
        configs = []
        for config_object in config_objects:
            config = viewers.DeviceConfigViewer()
            config.parse(config_object)
            configs.append(config)

        # Sort configs by name
        configs.sort(key=lambda x: x.name)

        # Get current config
        current_config = common.Common.get_device_state_value("config_uuid")

        # Convert current config uuid to name
        if current_config != None:
            for config in configs:
                if config.uuid == current_config:
                    current_config = config.name
                    break

        # Build and return response
        response = {"configs": configs, "current_config": current_config}
        return Response(response)


class DeviceConfigViewSet(viewsets.ModelViewSet):
    """API endpoint that allows device config to be viewed and loaded."""

    serializer_class = serializers.DeviceConfigSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.DeviceConfigModel.objects.all()
        return queryset

    @detail_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def load(self, request, uuid):
        """API endpoint to load a device config."""

        device_config_viewer = viewers.DeviceConfigViewer()
        response, status = device_config_viewer.load(uuid, request.data)
        return Response(response, status)


class RecipeBuilder(views.APIView):
    """ UI page for building recipes. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "recipe_builder.html"

    @method_decorator(login_required)
    def get(self, request):
        # Get recipes
        recipe_objects = models.RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(viewers.SimpleRecipeViewer(recipe_object))

        # Get cultivars
        cultivars_viewer = viewers.CultivarsViewer()
        cultivars = cultivars_viewer.json

        # Get cultivation methods
        cultivation_methods_viewer = viewers.CultivationMethodsViewer()
        cultivation_methods = cultivation_methods_viewer.json

        # Build and return response
        response = {
            "recipes": recipes,
            "cultivars": cultivars,
            "cultivation_methods": cultivation_methods,
        }
        return Response(response)


class Events(views.APIView):
    """ UI page for events. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "events.html"

    @method_decorator(login_required)
    def get(self, request):
        events = models.EventModel.objects.all().order_by("-timestamp")
        return Response({"events": events})


class Logs(views.APIView):
    """ UI page for logs. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "logs.html"

    @method_decorator(login_required)
    def get(self, request):

        # Load device config
        DEVICE_CONFIG_PATH = "data/config/device.txt"
        if os.path.exists(DEVICE_CONFIG_PATH):
            with open(DEVICE_CONFIG_PATH) as f:
                config_name = f.readline().strip()
        else:
            config_name = "unspecified"
        device_config = json.load(open("data/devices/{}.json".format(config_name)))

        # Build peripheral logs
        logs = []
        for peripheral in device_config["peripherals"]:

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
    """ UI page for peripherals. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "peripherals.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get current device state object
        current_device = viewers.DeviceViewer()

        # Get current environment state object
        current_environment = viewers.EnvironmentViewer()

        # Get current recipe state object
        current_recipe = viewers.RecipeViewer()

        # Get stored recipe objects
        recipe_objects = models.RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(viewers.SimpleRecipeViewer(recipe_object))

        # Get stored peripheral setups
        peripheral_setups = models.PeripheralSetupModel.objects.all()
        peripheral_setups = []
        for periheral_setup in peripheral_setups:
            peripheral_setups.append(json.loads(peripheral_setups.json))

        # Build and return response
        response = {
            "current_device": current_device,
            "current_environment": current_environment,
            "current_recipe": current_recipe,
            "recipes": recipes,
            "peripheral_setups": peripheral_setups,
        }
        return Response(response)


class DeviceConfigList(views.APIView):
    """ UI page for device configurations. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "device_config_list.html"

    @method_decorator(login_required)
    def get(self, request):
        device_config_objects = DeviceConfignModel.objects.all()
        device_config_viewers = []
        for device_config_object in device_config_objects:
            device_config_viewer = viewers.DeviceConfigViewer()
            device_config_viewer.parse(device_config_object)
            device_config_viewers.append(device_config_viewer)

        return Response({"device_config_viewers": device_config_viewers})


class Recipes(views.APIView):
    """UI page for recipes."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "recipes.html"

    @method_decorator(login_required)
    def get(self, request):
        recipe_objects = models.RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(viewers.SimpleRecipeViewer(recipe_object))

        return Response({"recipes": recipes})


class Environments(views.APIView):
    """UI page for environments."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "environments.html"

    @method_decorator(login_required)
    def get(self, request):
        environments = models.EnvironmentModel.objects.all().order_by("-timestamp")
        return Response({"environments": environments})


class Images(views.APIView):
    """UI page for ImageManager."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "images.html"

    # Initialize logger
    logger = logger.Logger("ImagesView", "app")

    @method_decorator(login_required)
    def get(self, request):
        self.logger.debug("Getting image view")

        # Get stored image filepaths
        filepaths = glob.glob(STORED_IMAGES_PATH)
        self.logger.debug("filepaths = {}".format(filepaths))

        # Build response
        filepaths_json = json.dumps(filepaths)
        response = {"filepaths_json": filepaths_json}

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)


class Resource(views.APIView):
    """UI page for ResourceManager."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "resource.html"

    # Initialize logger
    logger = logger.Logger("ResourceView", "app")

    @method_decorator(login_required)
    def get(self, request):
        self.logger.debug("Getting resource view")

        # Get resource manager
        app_config = apps.get_app_config(APP_NAME)
        resource_manager = app_config.coordinator.resource

        # Build response
        response = {
            "status": resource_manager.status,
            "free_disk": resource_manager.free_disk,
            "free_memory": resource_manager.free_memory,
            "database_size": resource_manager.database_size,
        }

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)


class Connect(views.APIView):
    """UI page fields for ConnectManager."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "connect.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response({})


class ConnectAdvanced(views.APIView):
    """UI page fields the advanced wireless connection page."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "connect_advanced.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response({})


class IoT(views.APIView):
    """UI page for IoT."""

    # Initialize view parameters
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "iot.html"

    # Initialize logger
    logger = logger.Logger("IotView", "app")

    @method_decorator(login_required)
    def get(self, request):
        self.logger.debug("Getting view")

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


class SystemViewSet(viewsets.ModelViewSet):
    """View set for system interactions."""

    # Initialize logger
    logger = logger.Logger("SystemViewSet", "app")

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def info(self, request):
        """Gets system info."""
        self.logger.debug("Getting system info")

        try:
            response = {
                "message": "Successfully got system info",
                "is_beaglebone": system.is_beaglebone(),
                "is_wifi_beaglebone": system.is_wifi_beaglebone(),
                "beaglebone_serial_number": system.beaglebone_serial_number(),
                "remote_device_ui_url": system.remote_device_ui_url(),
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
    def info(self, request):
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
            "wifi_access_points": network_manager.wifi_access_points,
        }

        # Return response
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, 200)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def joinwifi(self, request):
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
    def joinwifiadvanced(self, request):
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
            logger.exception(message)
            status = 500

        # Build and return response
        response = {"message": message}
        self.logger.debug("Returning response: {}".format(response))
        return Response(response, status)

    @list_route(methods=["POST"], permission_classes=[IsAuthenticated, IsAdminUser])
    def deletewifis(self, request):
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


class IotViewSet(viewsets.ModelViewSet):
    """View set for iot interactions."""

    # Initialize logger
    logger = logger.Logger("IotViewSet", "app")

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def info(self, request):
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
    def register(self, request):
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
    def reregister(self, request):
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


class Upgrade(views.APIView):
    """UI page for device upgrades."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "upgrade.html"

    @method_decorator(login_required)
    def get(self, request):

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
        return Response(response)


class UpgradeViewSet(viewsets.ModelViewSet):
    """View set for interactions with device upgrades."""

    # Initialize logger
    logger = logger.Logger("Upgrade", "app")

    # @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    # def info(self, request):
    #     """Gets for software upgrade info."""
    #     self.logger.debug("Getting software upgrade info")

    #     # Get upgrade manager
    #     app_config = apps.get_app_config(APP_NAME)
    #     upgrade = app_config.coordinator.upgrade

    #     # Get upgrade info
    #     response, status = upgrade.info()

    #     # Return response
    #     self.logger.debug("Returning response: {}".format(response))
    #     return Response(response, status)

    @list_route(methods=["GET"], permission_classes=[IsAuthenticated, IsAdminUser])
    def check(self, request):
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
    def upgrade(self, request):
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


class Manual(views.APIView):
    """UI page for manual controls."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "manual.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response({"manual": "data"})


class Entry(views.APIView):
    """UI page for data entry."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "entry.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response({"entry": "data"})


class Scratchpad(views.APIView):
    """UI page for scratchpad."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "scratchpad.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response()


def change_password(request):
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
