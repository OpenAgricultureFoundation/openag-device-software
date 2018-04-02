# Import standard python modules
import json
import uuid as uuid_module

# Import django modules
from django.db import models
from django.contrib.postgres.fields import JSONField


class State(models.Model):
    id = models.IntegerField(primary_key=True)
    device = JSONField()
    recipe = JSONField()
    environment = JSONField()
    peripherals = JSONField()
    controllers = JSONField()

    class Meta:
        verbose_name_plural = "State"


class Event(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    request = JSONField()
    response = JSONField(blank=True, null=True)

    class Meta:
        get_latest_by="timestamp"


class Recipe(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    recipe_json = JSONField()


    def save(self, *args, **kwargs):
        """ Checks if uuid already exists in recipe json. If not creates guid,
            appends to json, adds to model guid field, then saves model. """
        recipe_dict = json.loads(self.recipe_json)

        if "uuid" in recipe_dict and recipe_dict["uuid"] != None:
            self.uuid = recipe_dict["uuid"]
        else:
            self.uuid = uuid_module.uuid4()
            recipe_dict["uuid"] = str(self.uuid)
            self.recipe_json = json.dumps(recipe_dict)

        super(Recipe, self).save(*args, **kwargs)


class RecipeTransition(models.Model):
    minute = models.IntegerField()
    phase = models.TextField()
    cycle = models.TextField()
    environment_name = models.TextField()
    environment_state = JSONField()

    class Meta:
        verbose_name = "Recipe Transition"
        verbose_name_plural = "Recipe Transitions"