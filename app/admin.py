from django.contrib import admin

from app.models import State
from app.models import Event
from app.models import RecipeTransition


class StateAdmin(admin.ModelAdmin):
	list_display = ("device", "recipe", "environment", "peripherals", "controllers")
admin.site.register(State, StateAdmin)


class EventAdmin(admin.ModelAdmin):
	list_display = ("request", "response")
admin.site.register(Event, EventAdmin)


class RecipeTransitionAdmin(admin.ModelAdmin):
	list_display = ("minute", "phase", "cycle", "environment_name", 
		"environment_state")
admin.site.register(RecipeTransition, RecipeTransitionAdmin)