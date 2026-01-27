from datetime import date
import json

from django.http import JsonResponse
from city.models import City
from django.core.paginator import Paginator
from django.db.models.expressions import RawSQL
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .decorators import api_key_required
from .forms import RaceFilterForm
from .models import Race
from .services import get_races_around_position
from relation.services import get_race_for_user, get_race

from dateutil.relativedelta import relativedelta


@login_required
def get_races_page(request):
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

        races_qs = get_race(
            request.user,
            data.get("date_after"),
            data.get("date_before"),
            city=center_city,
            radius=radius,
            race_types=data.get("race_type"),
            min_distance=data.get("min_distance"),
            max_distance=data.get("max_distance"),
            statuses=data.get("status"),
            show_favorites=data.get("show_favorites"),
        )

    # Pagination
    paginator = Paginator(races_qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    geodata = {
        "points": [
            {
                "position": [float(race.latitude), float(race.longitude)],
                "title": race.name,
                "draggable": False,
            }
            for race in page_obj
        ],
    }

    if center_city:
        geodata["center"] = {"position": [float(center_city.latitude), float(center_city.longitude)]}

    context = {
        "races": page_obj,
        "form": form,
        "selected_city": center_city,  # Pass the actual city object being used
        "geodata": json.dumps(geodata),
        "oob": False,
    }
    if request.htmx:
        context["oob"] = True
        return render(request, "race/partials/race_list_results.html", context)
    return render(request, "race/races.html", context)


@api_key_required
def publish_new_race(request):
    return JsonResponse({"data": "succès"})
