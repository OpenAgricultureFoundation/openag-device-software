# Import django modules
from django.contrib import admin

# Import app models
from app.models import StateModel
from app.models import EventModel
from app.models import RecipeModel
from app.models import EnvironmentModel
from app.models import DeviceConfigModel
from app.models import PeripheralSetupModel
from app.models import RecipeTransitionModel
from app.models import SensorVariableModel
from app.models import ActuatorVariableModel
from app.models import CultivarModel
from app.models import CultivationMethodModel
from app.models import IoTConfigModel


class StateAdmin(admin.ModelAdmin):
    list_display = (
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


admin.site.register(StateModel, StateAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "recipient", "request", "response")


admin.site.register(EventModel, EventAdmin)


class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "state")


admin.site.register(EnvironmentModel, EnvironmentAdmin)


class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "json")


admin.site.register(DeviceConfigModel, DeviceConfigAdmin)


class PeripheralSetupAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "json")


admin.site.register(PeripheralSetupModel, PeripheralSetupAdmin)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "version", "json")


admin.site.register(RecipeModel, RecipeAdmin)


class RecipeTransitionAdmin(admin.ModelAdmin):
    list_display = ("minute", "phase", "cycle", "environment_name", "environment_state")


admin.site.register(RecipeTransitionModel, RecipeTransitionAdmin)


class SensorVariableAdmin(admin.ModelAdmin):
    list_display = ("key", "json")


admin.site.register(SensorVariableModel, SensorVariableAdmin)


class ActuatorVariableAdmin(admin.ModelAdmin):
    list_display = ("key", "json")


admin.site.register(ActuatorVariableModel, ActuatorVariableAdmin)


class CultivarAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "json")


admin.site.register(CultivarModel, CultivarAdmin)


class CultivationMethodAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "json")


admin.site.register(CultivationMethodModel, CultivationMethodAdmin)


class IoTConfigAdmin(admin.ModelAdmin):
    list_display = ["last_config_version"]


admin.site.register(IoTConfigModel, IoTConfigAdmin)
