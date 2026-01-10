from django.db.models import F, QuerySet
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Value, FloatField
from city.models import City
from .models import Race


def get_races_around_position(center: City, radius: int | None = None) -> QuerySet[Race]:
    qs = Race.objects.all()
    if center.location:
        qs = qs.annotate(distance_from_user=Distance("city__location", center.location))
    else:
        qs = qs.annotate(distance_from_user=Value(0.0, output_field=FloatField()))

    if radius:
        qs = qs.filter(distance_from_user__lte=D(km=radius).m)

    return qs.order_by("date_course", "distance_from_user")


def get_all_races() -> QuerySet[Race]:
    return Race.objects.all().annotate(distance_from_user=Value(0.0, output_field=FloatField()))
