from django.db.models import F, QuerySet
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Value, FloatField
from city.models import City
from .models import RaceUser
from accounts.models import User


def get_liked_races(user: User) -> QuerySet[RaceUser]:
    qs = RaceUser.objects.filter(liked=True, user=user)
    return qs
