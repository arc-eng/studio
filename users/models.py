from django.contrib.auth.models import AbstractUser
from django.db import models


class StudioUser(AbstractUser):
    api_key = models.CharField(null=True, blank=False, max_length=255)