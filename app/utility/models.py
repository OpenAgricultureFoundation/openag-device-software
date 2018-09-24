import hashlib
import random
from django.db import models


class GUIDModel(models.Model):

    guid = models.CharField(primary_key=True, max_length=40)

    def save(self, *args, **kwargs):

        if not self.guid:
            self.guid = hashlib.sha1(str(random.random())).hexdigest()

        super(GUIDModel, self).save(*args, **kwargs)
