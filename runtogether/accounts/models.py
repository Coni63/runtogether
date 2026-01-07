from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    strava_url = models.URLField(max_length=500, null=True, blank=True, help_text="URL of the user's Strava profile")
    garmin_url = models.URLField(max_length=500, null=True, blank=True, help_text="URL of the user's Garmin profile")
    city = models.ForeignKey(
        "city.City",
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="users",
        help_text="City where the user resides",
    )
