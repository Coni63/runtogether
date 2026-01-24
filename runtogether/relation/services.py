import datetime

from accounts.models import User
from city.models import City
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import QuerySet, Q
from django.db.models.expressions import RawSQL
from race.models import Race

from .models import RaceUser
from race.services import get_races_around_position
from django.db.models import FilteredRelation, Q, F, Value, BooleanField, CharField
from django.db.models.functions import Coalesce


def get_liked_races(user: User) -> QuerySet[RaceUser]:
    qs = RaceUser.objects.filter(favorited=True, user=user)
    return qs


def get_race_for_user(
    user: User,
    date_start: datetime.date,
    date_end: datetime.date,
    city: City | None = None,
    radius: int | None = None,
    race_types: list[str] | None = None,
    min_distance: float | None = None,
    max_distance: float | None = None,
    statuses: list[str] | None = None,
    show_favorites: bool = False,
) -> QuerySet[RaceUser]:
    qs = RaceUser.objects.filter(
        user=user,
        race__date_course__gte=date_start,
        race__date_course__lt=date_end,
        race__date_validated=True,
    ).select_related("race")

    # Status & Favorites Logic
    q_filter = Q()
    if statuses:
        q_filter |= Q(status__in=statuses)

    if show_favorites:
        q_filter |= Q(favorited=True)

    if not statuses and not show_favorites:
        # Default behavior: exclude status="none" (so favorites with no status are hidden unless requested)
        qs = qs.exclude(status="none")
    else:
        qs = qs.filter(q_filter)

    # Race Type
    if race_types:
        qs = qs.filter(race__race_type__in=race_types)

    # City & Radius
    if city and city.location:
        qs = qs.annotate(distance_from_center=Distance("race__city__location", city.location))
        if radius:
            qs = qs.filter(distance_from_center__lte=D(km=radius).m)

    # Distance (Race length)
    if min_distance is not None or max_distance is not None:
        effective_min = min_distance if min_distance is not None else 0
        effective_max = max_distance if max_distance is not None else 1000

        race_qs = Race.objects.annotate(
            has_matching_dist=RawSQL(
                "EXISTS (SELECT 1 FROM unnest(distance) AS d WHERE d BETWEEN %s AND %s)", (effective_min, effective_max)
            )
        ).filter(has_matching_dist=True)

        qs = qs.filter(race__in=race_qs)

    return qs


def get_race(
    user: User,
    date_start: datetime.date,
    date_end: datetime.date,
    city: City | None = None,
    radius: int | None = None,
    race_types: list[str] | None = None,
    min_distance: float | None = None,
    max_distance: float | None = None,
    statuses: list[str] | None = None,
    show_favorites: bool = False,
) -> QuerySet[RaceUser]:
    qs = get_races_around_position(
        center=city,
        radius=radius,
        race_types=race_types,
        date_after=date_start,
        date_before=date_end,
        min_distance=min_distance,
        max_distance=max_distance,
        user=user,
    )

    # 2. On ajoute la jointure "Outer" filtrée sur l'utilisateur
    qs = qs.annotate(
        # On crée une jointure spécifique pour l'user actuel
        user_interaction=FilteredRelation("user_links", condition=Q(user_links__user=user))
    ).annotate(
        # On "remonte" les champs de RaceUser dans l'objet Race
        user_status=F("user_interaction__status"),
        is_favorited=F("user_interaction__favorited"),
    )

    # 3. Optionnel : Gérer les valeurs NULL (si pas de lien)
    # qs = qs.annotate(
    #     final_status=Coalesce(F("user_interaction__status"), Value("none")),
    #     final_favorited=Coalesce(F("user_interaction__favorited"), Value(False)),
    # )

    # Status & Favorites Logic
    print(statuses, show_favorites)
    q_filter = Q()
    if statuses:
        q_filter |= Q(user_status__in=statuses)

    if show_favorites:
        q_filter |= Q(is_favorited=True)

    qs = qs.filter(q_filter)

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
