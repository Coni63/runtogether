from django.db.models import F, QuerySet
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Value, FloatField
from city.models import City
from .models import RaceUser
from accounts.models import User
from race.models import Race


def get_liked_races(user: User) -> QuerySet[RaceUser]:
    qs = RaceUser.objects.filter(liked=True, user=user)
    return qs


def set_favorited(user: User, race: Race) -> RaceUser:
    obj, _ = RaceUser.objects.update_or_create(user=user, race=race, defaults={"favorited": True})
    return obj


def set_status(user: User, race: Race, status: str) -> RaceUser | None:
    if status == "none":
        record = RaceUser.objects.filter(user=user, race=race).first()
        if record:
            if not record.favorited:
                record.delete()
                return None
            else:
                record.status = "none"
                record.save()
                return record

    obj = RaceUser.objects.update_or_create(user=user, race=race, defaults={"status": status})
    return obj


def remove_favorited(user: User, race: Race):
    record = RaceUser.objects.filter(race=race, user=user, favorited=True).first()
    if record:
        if record.status == "none":
            record.delete()
        else:
            record.favorited = False
            record.save()
            return record
