# Import standard python modules
import json

# Import django modules
from django.shortcuts import render

# Import django user management modules
from django.contrib.auth import login
from django.contrib.auth import authenticate

# Import django rest modules
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

# Import app models
from app.models import State
from app.models import Event
from app.models import Recipe
from app.models import RecipeTransition

# Import app serializers
from app.serializers import StateSerializer
from app.serializers import EventSerializer
from app.serializers import RecipeSerializer
from app.serializers import RecipeTransitionSerializer

# Import app viewers
from app.viewers import Recipe as RecipeViewer
from app.viewers import SimpleRecipe as SimpleRecipeViewer

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows state to be viewed. """
    serializer_class = StateSerializer

    def get_queryset(self):
        queryset = State.objects.all()
        return queryset


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows events to be viewed. """
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows recipes to be viewed. """
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return queryset

    def create(self, request):
        """ API endpoint to create a recipe. """
        recipe_viewer = RecipeViewer()
        response, status = recipe_viewer.create(request.data.dict())
        return Response(response, status)

    @detail_route(methods=["post"])
    def start(self, request, pk=None):
        """ API endpoint to start a recipe. """
        recipe_viewer = RecipeViewer()
        response, status = recipe_viewer.start(request.data.dict(), pk)
        return Response(response, status)

    @list_route(methods=["post"])
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
    """ UI page for recipe dashboard. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'dashboard.html'
    
    def get(self, request):
        current_recipe = RecipeViewer()
        recipe_objects = Recipe.objects.all()
        recipes = []
        for recipe_object in recipe_objects:
            recipes.append(SimpleRecipeViewer(recipe_object))

        return Response({'current_recipe': current_recipe, 'recipes': recipes}) 
