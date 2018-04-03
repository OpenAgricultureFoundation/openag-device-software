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
from app.models import DeviceConfigurationModel
from app.models import EnvironmentModel
from app.models import RecipeModel
from app.models import RecipeTransitionModel

# Import app serializers
from app.serializers import StateSerializer
from app.serializers import EventSerializer
from app.serializers import EnvironmentSerializer
from app.serializers import RecipeSerializer
from app.serializers import RecipeTransitionSerializer

# Import app viewers
from app.viewers import DeviceViewer
from app.viewers import RecipeViewer
from app.viewers import SimpleRecipeViewer
from app.viewers import EnvironmentViewer


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows state to be viewed. """
    serializer_class = StateSerializer

    def get_queryset(self):
        queryset = StateModel.objects.all()
        return queryset


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows events to be viewed. """
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = EventModel.objects.all()
        return queryset


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

    @permission_classes((IsAuthenticated, IsAdminUser,))
    def create(self, request):
        """ API endpoint to create a recipe. """
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
        queryset = RecipeTransition.objects.all()
        return queryset


class Dashboard(APIView):
    """ UI page for dashboard. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'dashboard.html'

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
            "recipes": recipes}
        return Response(response)


class Events(APIView):
    """ UI page for events. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'events.html'
    
    def get(self, request):
        events = EventModel.objects.all().order_by("-timestamp")
        return Response({'events': events})


class DeviceConfigurationList(APIView):
    """ UI page for device configurations. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "device_configuration_list.html"
    
    def get(self, request):
        device_configuration_objects = DeviceConfigurationModel.objects.all()
        device_configuration_viewers = []
        for device_configuration_object in device_configuration_objects:
            device_configuration_viewers.append(DeviceConfigurationViewer(device_configuration_object))

        return Response({"device_configuration_viewers": device_configuration_viewers})


class Recipes(APIView):
    """ UI page for recipes. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'recipes.html'
    
    def get(self, request):
        recipe_objects = RecipeModel.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(SimpleRecipeViewer(recipe_object))

        return Response({'recipes': recipes})


class Environments(APIView):
    """ UI page for environments. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'environments.html'
    
    def get(self, request):
        environments = EnvironmentModel.objects.all().order_by("-timestamp")
        return Response({'environments': environments})


class Manual(APIView):
    """ UI page for manual controls. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'manual.html'
    
    def get(self, request):
        return Response({'manual': 'data'})


class Entry(APIView):
    """ UI page for data entry. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'entry.html'
    
    def get(self, request):
        return Response({'entry': 'data'})