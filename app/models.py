# Import standard python modules
import json as json_
import uuid as uuid_module

# Import python types
from typing import Any

# Import django modules
from django.db import models

# from django.contrib.postgres.fields import JSONField
from jsonfield import JSONField


class StateModel(models.Model):
    id = models.IntegerField(primary_key=True)
    device = JSONField()
    recipe = JSONField()
    environment = JSONField()
    peripherals = JSONField()
    controllers = JSONField()
    iot = JSONField()
    resource = JSONField()
    connect = JSONField()
    upgrade = JSONField()

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"


class EventModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = JSONField()
    request = JSONField()
    response = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        get_latest_by = "timestamp"


class EnvironmentModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    state = JSONField()

    class Meta:
        verbose_name = "Environment"
        verbose_name_plural = "Environments"
        get_latest_by = "timestamp"


class DeviceConfigModel(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True)
    name = models.TextField()
    json = JSONField()

    class Meta:
        verbose_name = "Device Configuration"
        verbose_name_plural = "Device Configurations"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts uuid, name, and version from json on save. """
        dict_ = json_.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        super(DeviceConfigModel, self).save(*args, **kwargs)


class PeripheralSetupModel(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True)
    name = models.TextField()
    json = JSONField()

    class Meta:
        verbose_name = "Peripheral Setup"
        verbose_name_plural = "Peripheral Setups"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts uuid and name from json on save. """
        dict_ = json_.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        super(PeripheralSetupModel, self).save(*args, **kwargs)


class ControllerSetupModel(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True)
    name = models.TextField()
    json = JSONField()

    class Meta:
        verbose_name = "Controller Setup"
        verbose_name_plural = "Controller Setups"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts uuid and name from json on save. """
        dict_ = json_.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        super(ControllerSetupModel, self).save(*args, **kwargs)


class SensorVariableModel(models.Model):
    key = models.TextField(unique=True)
    json = JSONField()

    class Meta:
        verbose_name = "Sensor Variable"
        verbose_name_plural = "Sensor Variables"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts key from json on save. """
        dict_ = json_.loads(self.json)
        self.key = dict_["key"]
        super(SensorVariableModel, self).save(*args, **kwargs)


class ActuatorVariableModel(models.Model):
    key = models.TextField(unique=True)
    json = JSONField()

    class Meta:
        verbose_name = "Actuator Variable"
        verbose_name_plural = "Actuator Variables"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts key from json on save. """
        dict_ = json_.loads(self.json)
        self.key = dict_["key"]
        super(ActuatorVariableModel, self).save(*args, **kwargs)


class CultivarModel(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True)
    name = models.TextField()
    json = JSONField()

    class Meta:
        verbose_name = "Cultivar"
        verbose_name_plural = "Cultivars"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts uuid and name from json on save. """
        dict_ = json_.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        super(CultivarModel, self).save(*args, **kwargs)


class CultivationMethodModel(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True)
    name = models.TextField()
    json = JSONField()

    class Meta:
        verbose_name = "Cultivation Method"
        verbose_name_plural = "Cultivation Methods"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts uuid and name from json on save. """
        dict_ = json_.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        super(CultivationMethodModel, self).save(*args, **kwargs)


class RecipeModel(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True)
    json = JSONField()
    name = models.TextField()
    version = models.TextField()

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """ Extracts uuid and name from json on save. """
        dict_ = json_.loads(self.json)
        self.uuid = dict_["uuid"]
        self.name = dict_["name"]
        self.version = dict_["version"]

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


class IoTConfigModel(models.Model):
    last_config_version = models.IntegerField()

    class Meta:
        verbose_name = "IoTConfig"
        verbose_name_plural = "IoTConfigs"
        get_latest_by = "last_config_version"


class ConnectModel(models.Model):
    json = JSONField()

    class Meta:
        verbose_name = "Connect"
        verbose_name_plural = "Connects"
