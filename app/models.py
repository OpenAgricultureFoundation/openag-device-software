from django.db import models
from django.contrib.postgres.fields import JSONField


class RecipeTransition(models.Model):
    minute = models.IntegerField()
    phase = models.TextField()
    cycle = models.TextField()
    environment_name = models.TextField()
    environment_state = JSONField()

    class Meta:
        verbose_name = "Recipe Transition"
        verbose_name_plural = "Recipe Transitions"


class Device(models.Model):
	id = models.IntegerField(primary_key=True)
	configuration_json = JSONField()
	recipe_json = JSONField()
	system_state = JSONField()
	recipe_state = JSONField()
	peripheral_state = JSONField()
	controller_state = JSONField()
	log_summary = models.TextField()