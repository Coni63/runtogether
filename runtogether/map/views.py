from datetime import date
from django.shortcuts import render

from django.shortcuts import render
from django.http import JsonResponse
from race.service import get_races_around_position
from django.contrib.auth.decorators import login_required

from race.forms import RaceFilterForm
from race.models import Race
from dateutil.relativedelta import relativedelta

from city.models import City


def map_view(request):
    """Vue qui affiche la carte"""
    return render(request, "map/map.html")


@login_required
def get_points(request):
    # Determine initial city for the form
    initial_data = {}
    if request.user.is_authenticated and hasattr(request.user, "city") and request.user.city:
        initial_data["city"] = request.user.city.id

    # Create form with initial data if no GET parameters, otherwise use GET data
    if request.GET:
        form = RaceFilterForm(request.GET)
    else:
        form = RaceFilterForm(initial=initial_data)  # Reste non lié

    races_qs = Race.objects.none()
    center_city = None

    # Accepter le formulaire valide OU non lié
    if form.is_valid() or not form.is_bound:
        # Récupérer les données
        if form.is_bound:
            data = form.cleaned_data
        else:
            # Utiliser les valeurs initial du formulaire
            data = {
                "city": initial_data.get("city"),
                "radius": 40,
                "race_type": ["trail", "road"],
                "date_after": date.today(),
                "date_before": date.today() + relativedelta(months=6),
                "min_distance": 0,
                "max_distance": 200,
            }

        # 1. Determine Location Context
        city_id = data.get("city")
        if city_id:
            center_city = City.objects.filter(id=city_id).first()
        elif request.user.is_authenticated and hasattr(request.user, "city") and request.user.city:
            center_city = request.user.city
        else:
            center_city = None

        radius = int(data["radius"])

        races_qs = get_races_around_position(
            center_city,
            radius=radius,
            user=request.user,
            race_types=data.get("race_type"),
            date_after=data.get("date_after"),
            date_before=data.get("date_before"),
            min_distance=data.get("min_distance"),
            max_distance=data.get("max_distance"),
        )

    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(race.longitude), float(race.latitude)]},
                "properties": {
                    "id": race.id,
                    # Ajoute d'autres infos si besoin (nom, description, etc.)
                },
            }
            for race in races_qs
        ],
    }
    return JsonResponse(data)
