# Import django modules
from django.contrib import admin

# Import app models
from app.models import State
from app.models import Event
from app.models import Recipe
from app.models import RecipeTransition


class StateAdmin(admin.ModelAdmin):
	list_display = ("device", "recipe", "environment", "peripherals", "controllers")
admin.site.register(State, StateAdmin)


class EventAdmin(admin.ModelAdmin):
	list_display = ("timestamp", "request", "response")
admin.site.register(Event, EventAdmin)


class RecipeAdmin(admin.ModelAdmin):
	list_display = ("uuid", "recipe_json")
admin.site.register(Recipe, RecipeAdmin)


class RecipeTransitionAdmin(admin.ModelAdmin):
	list_display = ("minute", "phase", "cycle", "environment_name", 
		"environment_state")
admin.site.register(RecipeTransition, RecipeTransitionAdmin)