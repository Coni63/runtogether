import datetime
from accounts.models import User
from city.models import City
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import BooleanField, CharField, FilteredRelation, FloatField, Q, QuerySet, Value
from django.db.models.functions import Coalesce
from django.db.models.expressions import RawSQL
from .models import Race


def get_races_around_position(
    center: City,
    radius: int | None = None,
    *,
    race_types: list[str] | None = None,
    date_after: datetime.date | None = None,
    date_before: datetime.date | None = None,
    min_distance: float | None = None,
    max_distance: float | None = None,
    user: User | None = None,
) -> QuerySet[Race]:
    qs = Race.objects.all()
    if center.location:
        qs = qs.annotate(distance_from_user=Distance("city__location", center.location))
    else:
        qs = qs.annotate(distance_from_user=Value(0.0, output_field=FloatField()))

    if radius:
        qs = qs.filter(distance_from_user__lte=D(km=radius).m)

    if race_types:
        qs = qs.filter(race_type__in=race_types)

    if date_after:
        qs = qs.filter(date_course__gte=date_after)

    if date_before:
        qs = qs.filter(date_course__lte=date_before)

    if min_distance is not None or max_distance is not None:
        effective_min = min_distance if min_distance is not None else 0
        effective_max = max_distance if max_distance is not None else 1000

        qs = qs.annotate(
            has_matching_dist=RawSQL(
                "EXISTS (SELECT 1 FROM unnest(distance) AS d WHERE d BETWEEN %s AND %s)", (effective_min, effective_max)
            )
        ).filter(has_matching_dist=True)

    if not user:
        # On ajoute des valeurs par défaut pour les utilisateurs non connectés
        qs = qs.annotate(
            user_favorited=Value(False, output_field=BooleanField()), user_status=Value("none", output_field=CharField())
        )
    else:
        qs = qs.annotate(
            # On crée une relation filtrée sur l'utilisateur actuel
            user_link=FilteredRelation("user_links", condition=Q(user_links__user=user))
        ).annotate(
            # On récupère les valeurs via cette relation (Coalesce gère le cas où le lien n'existe pas)
            user_favorited=Coalesce("user_link__favorited", Value(False)),
            user_status=Coalesce("user_link__status", Value("none")),
        )

    return qs.order_by("date_course", "distance_from_user")


def get_all_races() -> QuerySet[Race]:
    return Race.objects.all().annotate(
        distance_from_user=Value(0.0, output_field=FloatField()),
        user_favorited=Value(False, output_field=BooleanField()),
        user_status=Value("none", output_field=CharField()),
    )
