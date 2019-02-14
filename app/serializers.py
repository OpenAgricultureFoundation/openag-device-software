# Import rest framework modules
from rest_framework import serializers

# Import app modules
from app.models import StateModel
from app.models import EventModel
from app.models import EnvironmentModel
from app.models import DeviceConfigModel
from app.models import PeripheralSetupModel
from app.models import RecipeModel
from app.models import RecipeTransitionModel
from app.models import CultivarModel
from app.models import CultivationMethodModel
from app.models import SensorVariableModel
from app.models import ActuatorVariableModel
from app.models import ConnectModel


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StateModel
        fields = (
            "device",
            "recipe",
            "environment",
            "peripherals",
            "controllers",
            "iot",
            "resource",
            "connect",
            "upgrade",
        )


class EnvironmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnvironmentModel
        fields = ("timestamp", "state")


class DeviceConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeviceConfigModel
        fields = ("uuid", "json")


class PeripheralSetupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PeripheralSetupModel
        fields = ("uuid", "name", "json")


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecipeModel
        fields = ("uuid", "name", "version", "json")


class RecipeTransitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecipeTransitionModel
        fields = ("minute", "phase", "cycle", "environment_name", "environment_state")


class CultivarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecipeModel
        fields = ("uuid", "name", "json")


class CultivationMethodSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecipeModel
        fields = ("uuid", "name", "json")


class SensorVariableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SensorVariableModel
        fields = ("key", "json")


class ActuatorVariableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ActuatorVariableModel
        fields = ("key", "json")


class ConnectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ConnectModel
        fields = "__all__"
