# Import rest framework modules
from rest_framework import serializers

# Import app modules
from app.models import StateModel
from app.models import EventModel
from app.models import EnvironmentModel
from app.models import DeviceConfigurationModel
from app.models import RecipeModel
from app.models import RecipeTransitionModel


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StateModel
        fields = ("device", "recipe", "environment", "peripherals",
        			"controllers")


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventModel
        fields = ("timestamp", "request", "response")


class EnvironmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnvironmentModel
        fields = ("timestamp", "state")


class DeviceConfigurationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeviceConfigurationModel
        fields = ("uuid", "json")


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecipeModel
        fields = ("uuid", "recipe_json")


class RecipeTransitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecipeTransitionModel
        fields = ("minute", "phase", "cycle", "environment_name",
        			"environment_state")