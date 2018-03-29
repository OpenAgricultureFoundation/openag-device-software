# Import django modules
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User, Group

# Import django rest modules
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

# Import app models
from app.models import Event

# Import app serializers
from app.serializers import EventSerializer
from app.serializers import UserSerializer
from app.serializers import GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited. """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class EventViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows events to be viewed or edited. """
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()
        return queryset


class EventList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'event_list.html'

    def get(self, request):
        queryset = Event.objects.all()
        return Response({'events': queryset})


def home(request):
    """ Renders home page. """
    return render(request, 'home.html')

