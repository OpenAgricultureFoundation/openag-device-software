# Import rest framework modules
from rest_framework import serializers

# Import app modules
from app.models import State
from app.models import Event
from app.models import RecipeTransition


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = State
        fields = ("device", "recipe", "environment", "peripherals",
        			"controllers")


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ("timestamp", "request", "response")



class RecipeTransitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecipeTransition
        fields = ("minute", "phase", "cycle", "environment_name",
        			"environment_state")