# Import standard python modules
import json

# Import django modules
from django.shortcuts import render

# Import django user management modules
from django.contrib.auth import login
from django.contrib.auth import authenticate

# Import django rest permissions modules
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser

# Import standard django rest modules
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer

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


# Import app viewers
from app.viewers import DeviceViewer
from app.viewers import EventViewer
from app.viewers import RecipeViewer
from app.viewers import SimpleRecipeViewer
from app.viewers import EnvironmentViewer
from app.viewers import CultivarsViewer
from app.viewers import CultivationMethodsViewer
from app.viewers import IoTViewer
from app.viewers import ResourceViewer


# TODO: Clean up views. See https://github.com/phildini/api-driven-django/blob/master/votes/views.py


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows state to be viewed. """
    serializer_class = StateSerializer

    def get_queryset(self):
        queryset = StateModel.objects.all()
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows events to be viewed and created. """
    serializer_class = EventSerializer

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

    def get_queryset(self):
        queryset = EnvironmentModel.objects.all()
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows recipes to be viewed. """
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = RecipeModel.objects.all()
        return queryset

    # @permission_classes((IsAuthenticated, IsAdminUser,))
    def create(self, request):
        """ API endpoint to create a recipe. """
        permission_classes = [IsAuthenticated, IsAdminUser]
        recipe_viewer = RecipeViewer()
        response, status = recipe_viewer.create(request.data.dict())
        return Response(response, status)

    # @permission_classes((IsAuthenticated, IsAdminUser,))
    @detail_route(methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def start(self, request, pk=None):
        """ API endpoint to start a recipe. """
        recipe_viewer = RecipeViewer()
        response, status = recipe_viewer.start(request.data.dict(), pk)
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

    def get_queryset(self):
        queryset = RecipeTransitionModel.objects.all()
        return queryset


class CultivarViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows cultivars to be viewed. """
    serializer_class = CultivarSerializer

    def get_queryset(self):
        queryset = CultivarModel.objects.all()
        return queryset


class CultivationMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows cultivation methods to be viewed. """
    serializer_class = CultivationMethodSerializer

    def get_queryset(self):
        queryset = CultivationMethodModel.objects.all()
        return queryset


class SensorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows sensor variables to be viewed. """
    serializer_class = SensorVariableSerializer

    def get_queryset(self):
        queryset = SensorVariableModel.objects.all()
        return queryset


class ActuatorVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows actuator variables to be viewed. """
    serializer_class = ActuatorVariableSerializer

    def get_queryset(self):
        queryset = ActuatorVariableModel.objects.all()
        return queryset


class PeripheralSetupViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows peripheral setups to be viewed. """
    serializer_class = PeripheralSetupSerializer

    def get_queryset(self):
        queryset = PeripheralSetupModel.objects.all()
        return queryset


class Dashboard(APIView):
    """ UI page for dashboard. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "dashboard.html"

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

        # Build and return response
        response = {
            "current_device": current_device,
            "current_environment": current_environment,
            "current_recipe": current_recipe,
            "recipes": recipes,
        }
        return Response(response)


class RecipeBuilder(APIView):
    """ UI page for building recipes. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "recipe_builder.html"

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

    def get(self, request):
        events = EventModel.objects.all().order_by("-timestamp")
        return Response({"events": events})


class Logs(APIView):
    """ UI page for logs. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "logs.html"

    def get(self, request):
        logs = [
            {"name": "SHT25-Top", "entries": ["log line 1", "log line 2"]},
            {"name": "T6713-Top", "entries": ["t6713 line 1", "t6713 line 2"]},
        ]

        # Load in config info
        about = json.load(open("about.json"))
        config_name = about["device_config"]
        device_config = json.load(open("data/devices/{}.json".format(config_name)))

        # Build logs
        logs = []
        for peripheral in device_config["peripherals"]:
            name = peripheral["name"]

            # Load in peripheral log file
            log_file = open("logs/peripherals/{}.log".format(name))
            lines = log_file.readlines()  # As long as file doesn't get too big, readlines is OK

            # Return up to 500 lines
            if len(lines) < 500:
                entries = lines
            else:
                entries = lines[-500:]

            # Append to log
            logs.append({"name": name, "entries": entries})

        # Return response
        return Response({"logs": logs, "logs_json": json.dumps(logs)})


class Peripherals(APIView):
    """ UI page for peripherals. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "peripherals.html"

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

    def get(self, request):
        device_config_objects = DeviceConfignModel.objects.all()
        device_config_viewers = []
        for device_config_object in device_config_objects:
            device_config_viewers.append(DeviceConfigViewer(device_config_object))

        return Response({"device_config_viewers": device_config_viewers})


class Recipes(APIView):
    """ UI page for recipes. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "recipes.html"

    def get(self, request):
        recipe_objects = RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(SimpleRecipeViewer(recipe_object))

        return Response({"recipes": recipes})


class Environments(APIView):
    """ UI page for environments. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "environments.html"

    def get(self, request):
        environments = EnvironmentModel.objects.all().order_by("-timestamp")
        return Response({"environments": environments})


class IoT(APIView):
    """ UI page for IoT. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "iot.html"

    def get(self, request):

        iotv = IoTViewer()

        # Build and return response
        response = {
            "status": iotv.iot_dict["connected"],
            "error": iotv.iot_dict["error"],
            "received_message_count": iotv.iot_dict["received_message_count"],
            "published_message_count": iotv.iot_dict["published_message_count"],
        }
        return Response(response)


class Resource(APIView):
    """ UI page for ResourceManager. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "resource.html"

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


class Manual(APIView):
    """ UI page for manual controls. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "manual.html"

    def get(self, request):
        return Response({"manual": "data"})


class Entry(APIView):
    """ UI page for data entry. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "entry.html"

    def get(self, request):
        return Response({"entry": "data"})


class Scratchpad(APIView):
    """ UI page for scratchpad. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "scratchpad.html"

    def get(self, request):
        return Response()
