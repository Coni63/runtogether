from django.shortcuts import render
from .service import get_races_around_position, get_all_races


def list_races(request):
    user = request.user
    print(user.city)
    if user.is_authenticated and hasattr(user, "city") and user.city and user.city.location:
        races = get_races_around_position(user.city, radius=40)
    else:
        races = get_all_races()
    return render(request, "race/races.html", {"races": races})
