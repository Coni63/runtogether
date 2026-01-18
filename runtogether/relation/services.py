import datetime

from accounts.models import User
from django.db.models import QuerySet
from race.models import Race

from .models import RaceUser


def get_liked_races(user: User) -> QuerySet[RaceUser]:
    qs = RaceUser.objects.filter(liked=True, user=user)
    return qs


def get_race_for_user(user: User, date_start: datetime.date, date_end: datetime.date) -> QuerySet[RaceUser]:
    qs = (
        RaceUser.objects.filter(
            user=user,
            race__date_course__gte=date_start,
            race__date_course__lt=date_end,
            race__date_validated=True,
        )
        .exclude(status="none")  # ignore favorited races with no real inscription
        .select_related("race")
    )

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
