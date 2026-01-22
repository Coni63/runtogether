from .models import Club
from city.models import City


def get_club(club_id: int) -> Club | None:
    return Club.objects.filter(id=club_id).first()


def create_club(name: str, city: City):
    return Club.objects.create(
        name=name,
        description={},
        city=city,
    )
