# Import rest framework modules
from rest_framework import serializers

# Import django modules
from django.contrib.auth.models import User, Group

# Import app modules
from app.models import Event


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ("timestamp", "request", "response")