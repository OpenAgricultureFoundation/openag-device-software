# Import standard python modules
import hashlib, random

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
    guid = models.CharField(primary_key=True, max_length=40, blank=True)
    json = JSONField()


    # def save(self, *args, **kwargs):
    #     """ Checks if guid already exists in recipe json. If not creates guid,
    #         appends to json, adds to model guid field, then saves model. """

    #     # Ensure all recipes stored in database have guids
    #     if "guid" in self.json and self.json["guid"] != None:
    #         self.guid = self.json["guid"]
    #     else:
    #         self.guid = hashlib.sha1(str(random.random())).hexdigest()
    #         self.json["guid"] = self.guid
    #     super(Recipe, self).save(*args, **kwargs)



class RecipeTransition(models.Model):
    minute = models.IntegerField()
    phase = models.TextField()
    cycle = models.TextField()
    environment_name = models.TextField()
    environment_state = JSONField()

    class Meta:
        verbose_name = "Recipe Transition"
        verbose_name_plural = "Recipe Transitions"