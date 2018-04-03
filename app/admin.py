# Import django modules
from django.contrib import admin

# Import app models
from app.models import StateModel
from app.models import EventModel
from app.models import EnvironmentModel
from app.models import DeviceConfigurationModel
from app.models import RecipeModel
from app.models import RecipeTransitionModel


class StateAdmin(admin.ModelAdmin):
	list_display = ("device", "recipe", "environment", "peripherals", "controllers")
admin.site.register(StateModel, StateAdmin)


class EventAdmin(admin.ModelAdmin):
	list_display = ("timestamp", "request", "response")
admin.site.register(EventModel, EventAdmin)


class EnvironmentAdmin(admin.ModelAdmin):
	list_display = ("timestamp", "state")
admin.site.register(EnvironmentModel, EnvironmentAdmin)


class DeviceConfigurationAdmin(admin.ModelAdmin):
	list_display = ("uuid", "json")
admin.site.register(DeviceConfigurationModel, DeviceConfigurationAdmin)


class RecipeAdmin(admin.ModelAdmin):
	list_display = ("uuid", "recipe_json")
admin.site.register(RecipeModel, RecipeAdmin)


class RecipeTransitionAdmin(admin.ModelAdmin):
	list_display = ("minute", "phase", "cycle", "environment_name", 
		"environment_state")
admin.site.register(RecipeTransitionModel, RecipeTransitionAdmin)