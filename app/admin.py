from django.contrib import admin

from app.models import RecipeTransition
from app.models import State


class RecipeTransitionAdmin(admin.ModelAdmin):
	list_display = ("minute", "phase", "cycle", "environment_name", 
		"environment_state")
admin.site.register(RecipeTransition, RecipeTransitionAdmin)


class StateAdmin(admin.ModelAdmin):
	list_display = ("device", "recipe", "environment", "peripherals", "controllers")
admin.site.register(State, StateAdmin)