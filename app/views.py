# Import standard python modules
import os, json, logging, shutil
from operator import itemgetter

# Import django modules
from django.shortcuts import render, redirect

# Import django user management modules
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# Import django rest permissions modules
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Import standard django rest modules
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer

# Import app common
from app.common import Common

# Import app forms
from app import forms

# Import app models
from app.models import StateModel
from app.models import EventModel
from app.models import RecipeModel
from app.models import EnvironmentModel
from app.models import DeviceConfigModel
from app.models import PeripheralSetupModel
from app.models import RecipeTransitionModel
from app.models import CultivarModel
from app.models import CultivationMethodModel
from app.models import SensorVariableModel
from app.models import ActuatorVariableModel

# Import app serializers
from app.serializers import StateSerializer
from app.serializers import EventSerializer
from app.serializers import EnvironmentSerializer
from app.serializers import RecipeSerializer
from app.serializers import RecipeTransitionSerializer
from app.serializers import CultivarSerializer
from app.serializers import CultivationMethodSerializer
from app.serializers import PeripheralSetupSerializer
from app.serializers import SensorVariableSerializer
from app.serializers import ActuatorVariableSerializer
from app.serializers import DeviceConfigSerializer

# Import app viewers
from app.viewers import DeviceViewer
from app.viewers import EventViewer
from app.viewers import RecipeViewer
from app.viewers import SimpleRecipeViewer
from app.viewers import DeviceConfigViewer
from app.viewers import EnvironmentViewer
from app.viewers import CultivarsViewer
from app.viewers import CultivationMethodsViewer
from app.viewers import IoTViewer
from app.viewers import ResourceViewer

from device.connect.utilities import ConnectUtilities
from device.upgrade.utilities import UpgradeUtilities

# TODO: Clean up views. See https://github.com/phildini/api-driven-django/blob/master/votes/views.py


LOG_DIR = "data/logs/"
IMAGE_DIR = "data/images/"


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


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows state to be viewed."""

    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StateModel.objects.all()
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    """API endpoint that allows events to be viewed and created."""

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EventModel.objects.all()
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
        event_viewer = EventViewer()
        message, status = event_viewer.create(request_dict)
        response_dict = {"message": message}
        return Response(response_dict, status=status)


class EnvironmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows events to be viewed. """

    serializer_class = EnvironmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EnvironmentModel.objects.all()
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """API endpoints that allow recipes to be started, stopped, created, and viewed."""

    serializer_class = RecipeSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RecipeModel.objects.all().order_by("name")
        return queryset

    def create(self, request):
        """ API endpoint to create a recipe. """
        permission_classes = [IsAuthenticated, IsAdminUser]
        recipe_viewer = RecipeViewer()
        response, status = recipe_viewer.create(request.data)  # was data.dict()
        return Response(response, status)

    @detail_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def start(self, request, uuid):
        """API endpoint to start a recipe."""
        recipe_viewer = RecipeViewer()
        response, status = recipe_viewer.start(uuid, request.data)  # was data.dict()
        return Response(response, status)

    @list_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def stop(self, request):
        """ API endpoint to stop a recipe. """
        recipe_viewer = RecipeViewer()
        response, status = recipe_viewer.stop()
        return Response(response, status)


class RecipeTransitionViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows recipe transitions to be viewed. """

    serializer_class = RecipeTransitionSerializer

    @method_decorator(login_required)
    def get_queryset(self):
        queryset = RecipeTransitionModel.objects.all()
        return queryset


class CultivarViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows cultivars to be viewed. """

    serializer_class = CultivarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CultivarModel.objects.all()
        return queryset


class CultivationMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows cultivation methods to be viewed. """

    serializer_class = CultivationMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CultivationMethodModel.objects.all()
        return queryset


class SensorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows sensor variables to be viewed. """

    serializer_class = SensorVariableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SensorVariableModel.objects.all()
        return queryset


class ActuatorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows actuator variables to be viewed. """

    serializer_class = ActuatorVariableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ActuatorVariableModel.objects.all()
        return queryset


class PeripheralSetupViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows peripheral setups to be viewed. """

    serializer_class = PeripheralSetupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PeripheralSetupModel.objects.all()
        return queryset


class Home(APIView):
    """UI page for home."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "home.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get internet connectivity. TODO: This should access connect manager through
        # coordinator manager. See viewers.py for example implementation
        valid_internet_connection = ConnectUtilities.valid_internet_connection()

        from django.shortcuts import redirect, reverse

        if valid_internet_connection:
            return redirect(reverse("dashboard"))
        else:
            return redirect(reverse("connect"))

        # Build and return response
        response = {"valid_internet_connection": valid_internet_connection}
        return Response()


class Dashboard(APIView):
    """UI page for dashboard."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "dashboard.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get current device state object
        current_device = DeviceViewer()

        # Get current environment state object
        current_environment = EnvironmentViewer()

        # Get current recipe state object
        current_recipe = RecipeViewer()

        # Get stored recipe objects
        recipe_objects = RecipeModel.objects.all().order_by("name")
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(SimpleRecipeViewer(recipe_object))

        # Get datetime picker form
        datetime_form = forms.DateTimeForm()

        # Get resource viewer: TODO: This should access connect manager through
        # coordinator manager. See viewers.py for example implementation
        valid_internet_connection = ConnectUtilities.valid_internet_connection()

        # Build and return response
        response = {
            "current_device": current_device,
            "current_environment": current_environment,
            "current_recipe": current_recipe,
            "recipes": recipes,
            "datetime_form": datetime_form,
            "valid_internet_connection": valid_internet_connection,
        }
        return Response(response)


class DeviceConfig(APIView):
    """UI page for managing device config."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "device_config.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get stored device config objects
        config_objects = DeviceConfigModel.objects.all()
        configs = []
        for config_object in config_objects:
            config = DeviceConfigViewer()
            config.parse(config_object)
            configs.append(config)

        # Sort configs by name
        configs.sort(key=lambda x: x.name)

        # Get current config
        current_config = Common.get_device_state_value("config_uuid")

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

    serializer_class = DeviceConfigSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DeviceConfigModel.objects.all()
        return queryset

    @detail_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def load(self, request, uuid):
        """API endpoint to load a device config."""

        device_config_viewer = DeviceConfigViewer()
        response, status = device_config_viewer.load(uuid, request.data)
        return Response(response, status)


class RecipeBuilder(APIView):
    """ UI page for building recipes. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "recipe_builder.html"

    @method_decorator(login_required)
    def get(self, request):
        # Get recipes
        recipe_objects = RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(SimpleRecipeViewer(recipe_object))

        # Get cultivars
        cultivars_viewer = CultivarsViewer()
        cultivars = cultivars_viewer.json

        # Get cultivation methods
        cultivation_methods_viewer = CultivationMethodsViewer()
        cultivation_methods = cultivation_methods_viewer.json

        return Response(
            {
                "recipes": recipes,
                "cultivars": cultivars,
                "cultivation_methods": cultivation_methods,
            }
        )


class Events(APIView):
    """ UI page for events. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "events.html"

    @method_decorator(login_required)
    def get(self, request):
        events = EventModel.objects.all().order_by("-timestamp")
        return Response({"events": events})


class Logs(APIView):
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


class Peripherals(APIView):
    """ UI page for peripherals. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "peripherals.html"

    @method_decorator(login_required)
    def get(self, request):

        # Get current device state object
        current_device = DeviceViewer()

        # Get current environment state object
        current_environment = EnvironmentViewer()

        # Get current recipe state object
        current_recipe = RecipeViewer()

        # Get stored recipe objects
        recipe_objects = RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(SimpleRecipeViewer(recipe_object))

        # Get stored peripheral setups
        peripheral_setups = PeripheralSetupModel.objects.all()
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


class DeviceConfigList(APIView):
    """ UI page for device configurations. """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "device_config_list.html"

    @method_decorator(login_required)
    def get(self, request):
        device_config_objects = DeviceConfignModel.objects.all()
        device_config_viewers = []
        for device_config_object in device_config_objects:
            device_config_viewer = DeviceConfigViewer()
            device_config_viewer.parse(device_config_object)
            device_config_viewers.append(device_config_viewer)

        return Response({"device_config_viewers": device_config_viewers})


class Recipes(APIView):
    """UI page for recipes."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "recipes.html"

    @method_decorator(login_required)
    def get(self, request):
        recipe_objects = RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(SimpleRecipeViewer(recipe_object))

        return Response({"recipes": recipes})


class Environments(APIView):
    """UI page for environments."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "environments.html"

    @method_decorator(login_required)
    def get(self, request):
        environments = EnvironmentModel.objects.all().order_by("-timestamp")
        return Response({"environments": environments})


class IoT(APIView):
    """UI page for IoT."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "iot.html"

    @method_decorator(login_required)
    def get(self, request):

        iotv = IoTViewer()

        # Build and return response
        response = {
            "status": iotv.iot_dict["connected"],
            "error": iotv.iot_dict["error"],
            "received_message_count": iotv.iot_dict["received_message_count"],
            "published_message_count": iotv.iot_dict["published_message_count"],
            "device_id": os.environ.get("DEVICE_ID"),
        }
        return Response(response)


class Images(APIView):
    """UI page for ImageManager."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "images.html"

    @method_decorator(login_required)
    def get(self, request):
        stored_path = IMAGE_DIR + "stored/"
        stored_files = os.listdir(stored_path)
        stored_files.sort()
        files = []
        for f in stored_files:
            # Clean up any place holder images
            if f.startswith("This_"):
                os.remove(stored_path + f)
                continue
            if f.endswith(".png"):
                files.append({"name": f})

        if 0 == len(files):
            if not os.path.isdir(stored_path):
                os.mkdir(stored_path)
            s = "device/peripherals/modules/usb_camera/tests/simulation_image.png"
            place_holder = (
                "This_is_just_a_sample_image_until_your_EDU_takes_its_own_picture.png"
            )
            shutil.copy(s, stored_path + place_holder)
            files.append({"name": place_holder})

        response = {"files_json": json.dumps(files)}
        return Response(response)


class Resource(APIView):
    """UI page for ResourceManager."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "resource.html"

    @method_decorator(login_required)
    def get(self, request):

        rv = ResourceViewer()

        # Build and return response
        response = {
            "status": rv.resource_dict["status"],
            "error": rv.resource_dict["error"],
            "available_disk_space": rv.resource_dict["available_disk_space"],
            "free_memory": rv.resource_dict["free_memory"],
            "database_size": rv.resource_dict["database_size"],
            "internet_connection": rv.resource_dict["internet_connection"],
        }
        return Response(response)


class ConnectAdvanced(APIView):
    """UI page fields the advanced wireless connection page."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "connect_advanced.html"

    @method_decorator(login_required)
    def get(self, request):
        extra = {"console_name": "views.ConnectAdvanced"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        response = ConnectUtilities.get_status()
        logger.info("ConnectAdvanced response={}".format(response))
        return Response(response)


class Connect(APIView):
    """UI page fields for ConnectManager."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "connect.html"

    @method_decorator(login_required)
    def get(self, request):
        extra = {"console_name": "views.Connect"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        response = ConnectUtilities.get_status()
        logger.info("Connect response={}".format(response))
        return Response(response)


class ConnectGetStatus(viewsets.ViewSet):
    """REST API to get all connect status fields shown.
    This class extends the ViewSet (not ModelViewSet) because it
    dynamically gets its data and the Model gets data from the DB."""

    @method_decorator(login_required)
    def list(self, request):
        extra = {"console_name": "views.ConnectGetStatus"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        response = ConnectUtilities.get_status()
        logger.info("ConnectGetStatus response={}".format(response))
        return Response(response)


class ConnectJoinWifi(viewsets.ViewSet):
    """REST API to join a wifi. Request is POSTed with wifi and pass.
    This class extends the ViewSet (not ModelViewSet) because it
    dynamically gets its data and the Model gets data from the DB."""

    @method_decorator(login_required)
    def create(self, request):
        extra = {"console_name": "views.ConnectJoinWifi"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        # Get req parameters
        try:
            reqd = request.data.dict()
        except Exception as e:
            response = {"message": "Internal error: {}".format(e)}
            return Response(response, 400)

        wifi = reqd["wifi"]
        password = reqd["password"]

        logger.info("ConnectJoinWifi wifi={} pass={}".format(wifi, password))
        result = ConnectUtilities.join_wifi(wifi, password)
        response = {"success": result}
        logger.info("ConnectJoinWifi response={}".format(response))
        if not result:
            return Response(response, 400)
        return Response(response)


class ConnectJoinWifiAdvanced(viewsets.ViewSet):
    """REST API to join a wifi. Request is POSTed with wifi and pass.
    This class extends the ViewSet (not ModelViewSet) because it
    dynamically gets its data and the Model gets data from the DB."""

    @method_decorator(login_required)
    def create(self, request):
        extra = {"console_name": "views.ConnectJoinWifiAdvanced"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        # Get req parameters
        try:
            reqd = request.data.dict()
        except Exception as e:
            response = {"message": "Internal error: {}".format(e)}
            return Response(response, 400)

        ssid_name = reqd["ssid_name"]
        passphrase = reqd["passphrase"]
        hiddenSSID = reqd["hiddenSSID"]
        security = reqd["security"]
        eap = reqd["eap"]
        identity = reqd["identity"]
        phase2 = reqd["phase2"]

        logger.info("ConnectJoinWifiAdvanced reqd={}".format(reqd))
        result = ConnectUtilities.join_wifi_advanced(ssid_name, passphrase, hiddenSSID, security, eap, identity, phase2)
        response = {"success": result}
        logger.info("ConnectJoinWifiAdvanced response={}".format(response))
        if not result:
            return Response(response, 400)
        return Response(response)


class ConnectDeleteWifis(viewsets.ViewSet):
    """REST API to disconnect any active network connections and delete all
    wifi configurations made by the user. Called with GET."""

    @method_decorator(login_required)
    def list(self, request):
        extra = {"console_name": "views.ConnectDeleteWifis"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        response = ConnectUtilities.delete_wifi_connections()
        logger.info("ConnectDeleteWifis response={}".format(response))
        return Response(response)


class ConnectRegisterIoT(viewsets.ViewSet):
    """REST API to register this machine with the IoT backend.
    Called with GET."""

    @method_decorator(login_required)
    def list(self, request):
        extra = {"console_name": "views.ConnectRegisterIoT"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        response = ConnectUtilities.register_iot()
        logger.info("ConnectRegisterIoT response={}".format(response))
        return Response(response)


class ConnectDeleteIoTreg(viewsets.ViewSet):
    """REST API to delete the current IoT registration (directory).
    Called with GET."""

    @method_decorator(login_required)
    def list(self, request):
        extra = {"console_name": "views.ConnectDeleteIoTreg"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        response = ConnectUtilities.delete_iot_registration()
        logger.info("ConnectDeleteIoTreg response={}".format(response))
        return Response(response)


class Upgrade(APIView):
    """UI page fields for ConnectManager."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "upgrade.html"

    @method_decorator(login_required)
    def get(self, request):
        extra = {"console_name": "views.Update"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)

        response = UpgradeUtilities.get_status()
        logger.info("Upgrade status response={}".format(response))
        return Response(response)


class UpgradeNow(viewsets.ViewSet):
    """REST API to upgrade our debian package.
    This class extends the ViewSet (not ModelViewSet) because it
    dynamically gets its data and the Model gets data from the DB."""

    @method_decorator(login_required)
    def list(self, request):
        extra = {"console_name": "views.UpgradeNow"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)
        response = UpgradeUtilities.update_software()
        logger.info("UpgradeNow response={}".format(response))
        return Response(response)


class UpgradeCheck(viewsets.ViewSet):
    """REST API to check for upgrades to our debian package. """

    @method_decorator(login_required)
    def list(self, request):
        extra = {"console_name": "views.UpgradeCheck"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)
        response = UpgradeUtilities.check()
        logger.info("UpgradeCheck response={}".format(response))
        return Response(response)


class UpgradeStatus(viewsets.ViewSet):
    """REST API to get the current software version status. """

    @method_decorator(login_required)
    def list(self, request):
        extra = {"console_name": "views.UpgradeStatus"}
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, extra)
        response = UpgradeUtilities.get_status()
        logger.info("UpgradeStatus response={}".format(response))
        return Response(response)


class Manual(APIView):
    """UI page for manual controls."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "manual.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response({"manual": "data"})


class Entry(APIView):
    """UI page for data entry."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "entry.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response({"entry": "data"})


class Scratchpad(APIView):
    """UI page for scratchpad."""

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "scratchpad.html"

    @method_decorator(login_required)
    def get(self, request):
        return Response()
