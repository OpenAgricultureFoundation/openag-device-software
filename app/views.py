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

# Import app models and serializers
from app.models import State
from app.serializers import StateSerializer
from app.models import Event
from app.serializers import EventSerializer
from app.models import RecipeTransition
from app.serializers import RecipeTransitionSerializer


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


class RecipeTransitionViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows recipe transitions to be viewed. """
    serializer_class = RecipeTransitionSerializer

    def get_queryset(self):
        queryset = RecipeTransition.objects.all()
        return queryset


class Home(APIView):
    """ UI home page. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home.html'

    def get(self, request):
        return Response({'data': None})


class RecipeDashboard(APIView):
    """ UI page for recipe dashboard. """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'recipe_dashboard.html'  

    def get(self, request):
        state = State.objects.filter(pk=1).first()
        return Response({'recipe': state.recipe})   