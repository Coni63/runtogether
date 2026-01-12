from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models.expressions import RawSQL
from city.models import City
from .models import Race
from .forms import RaceFilterForm
from .service import get_races_around_position, get_all_races


def list_races(request):
    form = RaceFilterForm(request.GET)
    races_qs = Race.objects.none()  # Placeholder

    if form.is_valid():
        data = form.cleaned_data

        # 1. Determine Location Context
        city_id = data.get("city")
        if city_id:
            center_city = City.objects.filter(id=city_id).first()
        elif request.user.is_authenticated and hasattr(request.user, "city") and request.user.city:
            center_city = request.user.city

        radius = int(data["radius"])

        # 2. Get Base QuerySet
        if center_city and center_city.location:
            races_qs = get_races_around_position(
                center_city, radius=radius, user=request.user if request.user.is_authenticated else None
            )
        else:
            races_qs = get_all_races()

        # 3. Apply Filters
        if data.get("race_type"):
            races_qs = races_qs.filter(race_type=data.get("race_type"))

        if data.get("date_after"):
            races_qs = races_qs.filter(date_course__gte=data.get("date_after"))

        if data.get("date_before"):
            races_qs = races_qs.filter(date_course__lte=data.get("date_before"))

        min_dist = data.get("min_distance")
        max_dist = data.get("max_distance")

        # Filter if either is set (and not None)
        if min_dist is not None or max_dist is not None:
            # Default values if one is missing to ensure range validity
            # Assuming realistic bounds if not provided
            effective_min = min_dist if min_dist is not None else 0
            effective_max = max_dist if max_dist is not None else 1000

            # Use RawSQL to check if ANY element in the 'distance' array is BETWEEN min and max
            # Note: The table name 'race_race' and column 'distance' are assumed standard.
            # Using the ORM's field name usually resolves correctly but for RawSQL we should be careful.
            # Ideally, we pass the parameters safely.
            races_qs = races_qs.annotate(
                has_matching_dist=RawSQL(
                    "EXISTS (SELECT 1 FROM unnest(distance) AS d WHERE d BETWEEN %s AND %s)", (effective_min, effective_max)
                )
            ).filter(has_matching_dist=True)

    else:
        # Initial load or invalid form
        if request.user.is_authenticated and hasattr(request.user, "city") and request.user.city and request.user.city.location:
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
        "page_obj": page_obj,  # passing explicitly for convenience
    }

    if request.htmx:
        return render(request, "race/partials/race_list_results.html", context)

    return render(request, "race/races.html", context)
