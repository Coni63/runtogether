from city.models import City
from django.core.paginator import Paginator
from django.db.models.expressions import RawSQL
from django.shortcuts import render

from .forms import RaceFilterForm
from .models import Race
from .service import get_all_races, get_races_around_position


def list_races(request):
    # Determine initial city for the form
    initial_data = {}
    if request.user.is_authenticated and hasattr(request.user, "city") and request.user.city:
        initial_data["city"] = request.user.city.id

    # Create form with initial data if no GET parameters, otherwise use GET data
    if request.GET:
        form = RaceFilterForm(request.GET)
    else:
        form = RaceFilterForm(initial=initial_data)

    races_qs = Race.objects.none()
    center_city = None

    if form.is_valid():
        data = form.cleaned_data
        # 1. Determine Location Context
        city_id = data.get("city")
        if city_id:
            center_city = City.objects.filter(id=city_id).first()
        elif request.user.is_authenticated and hasattr(request.user, "city") and request.user.city:
            center_city = request.user.city
        else:
            center_city = None

        radius = int(data["radius"])

        # 2. Get Base QuerySet
        if center_city and center_city.location:
            races_qs = get_races_around_position(
                center_city, radius=radius, user=request.user if request.user.is_authenticated else None
            )
        else:
            races_qs = get_all_races()

        # 3. Apply Filters
        race_types = data.get("race_type")
        if race_types:
            races_qs = races_qs.filter(race_type__in=race_types)

        if data.get("date_after"):
            races_qs = races_qs.filter(date_course__gte=data.get("date_after"))

        if data.get("date_before"):
            races_qs = races_qs.filter(date_course__lte=data.get("date_before"))

        min_dist = data.get("min_distance")
        max_dist = data.get("max_distance")

        if min_dist is not None or max_dist is not None:
            effective_min = min_dist if min_dist is not None else 0
            effective_max = max_dist if max_dist is not None else 1000

            races_qs = races_qs.annotate(
                has_matching_dist=RawSQL(
                    "EXISTS (SELECT 1 FROM unnest(distance) AS d WHERE d BETWEEN %s AND %s)", (effective_min, effective_max)
                )
            ).filter(has_matching_dist=True)
    else:
        # Initial load or invalid form
        if request.user.is_authenticated and hasattr(request.user, "city") and request.user.city and request.user.city.location:
            center_city = request.user.city
            races_qs = get_races_around_position(request.user.city, radius=40, user=request.user)
        else:
            races_qs = get_all_races()

    # Ensure ordering
    races_qs = races_qs.order_by("date_course")

    # Pagination
    paginator = Paginator(races_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "races": page_obj,
        "form": form,
        "page_obj": page_obj,
        "selected_city": center_city,  # Pass the actual city object being used
    }

    if request.htmx:
        return render(request, "race/partials/race_list_results.html", context)
    return render(request, "race/races.html", context)
