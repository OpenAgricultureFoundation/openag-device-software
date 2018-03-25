from django.contrib import admin

from app.models import RecipeTransition
from app.models import Device


class RecipeTransitionAdmin(admin.ModelAdmin):
	list_display = ("minute", "phase", "cycle", "environment_name", 
		"environment_state")
admin.site.register(RecipeTransition, RecipeTransitionAdmin)


class DeviceAdmin(admin.ModelAdmin):
	list_display = ("log_summary", "configuration_json", "recipe_json", "system_state", 
		"recipe_state", "peripheral_state", "controller_state")
admin.site.register(Device, DeviceAdmin)