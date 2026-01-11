from django.db.models import F, QuerySet, FilteredRelation, Q, Value, CharField, BooleanField
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Value, FloatField
from city.models import City
from .models import Race
from accounts.models import User
from django.db.models.functions import Coalesce


def get_races_around_position(center: City, radius: int | None = None, user: User | None = None) -> QuerySet[Race]:
    qs = Race.objects.all()
    if center.location:
        qs = qs.annotate(distance_from_user=Distance("city__location", center.location))
    else:
        qs = qs.annotate(distance_from_user=Value(0.0, output_field=FloatField()))

    if radius:
        qs = qs.filter(distance_from_user__lte=D(km=radius).m)

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
