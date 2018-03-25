from django.contrib import admin
from app.models import RecipeTransition


class RecipeTransitionAdmin(admin.ModelAdmin):
	list_display = ("minute", "phase", "cycle", "environment_name", 
		"environment_state")
admin.site.register(RecipeTransition, RecipeTransitionAdmin)