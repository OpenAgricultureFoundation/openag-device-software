# Import standard python modules
import json
import uuid as uuid_module

# Import django modules
from django.db import models
from django.contrib.postgres.fields import JSONField


class StateModel(models.Model):
    id = models.IntegerField(primary_key=True)
    device = JSONField()
    recipe = JSONField()
    environment = JSONField()
    peripherals = JSONField()
    controllers = JSONField()

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "State"


class EventModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    request = JSONField()
    response = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        get_latest_by="timestamp"


class EnvironmentModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    state = JSONField()

    class Meta:
        verbose_name = "Environment"
        verbose_name_plural = "Environments"
        get_latest_by="timestamp"


class DeviceConfigModel(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, unique=True)
    name = models.TextField()
    version = models.TextField()
    json = JSONField()

    class Meta:
        verbose_name = "Device Configuration"
        verbose_name_plural = "Device Configurations"

    def save(self, *args, **kwargs):
        """ Extracts uuid, name, and version from json on save. """
        dict_ = json.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        self.version = dict_["version"]
        super(DeviceConfigModel, self).save(*args, **kwargs)


class PeripheralSetupModel(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, unique=True)
    name = models.TextField()
    json = JSONField()

    class Meta:
        verbose_name = "Peripheral Setup"
        verbose_name_plural = "Peripheral Setups"

    def save(self, *args, **kwargs):
        """ Extracts uuid and name from json on save. """
        dict_ = json.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        super(PeripheralSetupModel, self).save(*args, **kwargs)


class RecipeModel(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    recipe_json = JSONField()

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"


    def save(self, *args, **kwargs):
        """ Checks if uuid already exists in recipe json. If not creates uuid,
            appends to json, adds to model uuid field, then saves model. """
        recipe_dict = json.loads(self.recipe_json)

        if "uuid" in recipe_dict and recipe_dict["uuid"] != None:
            self.uuid = recipe_dict["uuid"]
        else:
            self.uuid = uuid_module.uuid4()
            recipe_dict["uuid"] = str(self.uuid)
            self.recipe_json = json.dumps(recipe_dict)

        super(RecipeModel, self).save(*args, **kwargs)


class RecipeTransitionModel(models.Model):
    minute = models.IntegerField()
    phase = models.TextField()
    cycle = models.TextField()
    environment_name = models.TextField()
    environment_state = JSONField()

    class Meta:
        verbose_name = "Recipe Transition"
        verbose_name_plural = "Recipe Transitions"