from django.contrib.auth import get_user_model
from django.db.models import F, QuerySet
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from .models import Race

User = get_user_model()


def get_races_around_user(user: User, radius: int | None = None) -> QuerySet[Race]:
    """
    Return races around the user city.
    If the user has no city, it returns all races.
    If a radius is provided, it returns races within that radius of the user's city.
    """
    if user.is_authenticated and hasattr(user, "city") and user.city and user.city.location and radius:
        return (
            Race.objects.annotate(distance_from_user=Distance("city__location", user.city.location))
            .filter(distance_from_user__lte=D(km=radius))
            .order_by("distance_from_user")
        )
    return Race.objects.all()
