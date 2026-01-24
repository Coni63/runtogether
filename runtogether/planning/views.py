import contextlib
import datetime
import json

from city.models import City
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from race.models import Race
from relation.services import get_race_for_user, get_race

from .forms import PlanningFilterForm
from .services import get_absences, remove_absences, set_or_update_absences


def __to_date(dt: str) -> datetime.date:
    if not dt:
        return None

    with contextlib.suppress(Exception):
        return datetime.datetime.strptime(dt[:10], "%Y-%m-%d").date()

    return None


@login_required
def load_calendar_page(request):
    initial_data = {}
    selected_city = None
    if request.user.is_authenticated and hasattr(request.user, "city") and request.user.city:
        initial_data["city"] = request.user.city.id
        selected_city = request.user.city

    form = PlanningFilterForm(initial=initial_data)

    context = {"form": form, "selected_city": selected_city}
    return render(request, "planning/planning.html", context)


@login_required
@require_POST
def set_absences_view(request):
    """
    Set user absences or update reason if existing

    body should be

    {
        dateStart: "2026-05-21"
        dateStart: "2026-05-25"  // not included, calendar will set 20 to 24 included
        reason: "Sick"
    }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return []

    date_start = __to_date(data.get("dateStart"))
    date_end = __to_date(data.get("dateEnd"))
    reason = data.get("reason", "Indisponible")

    added_count = set_or_update_absences(request.user, date_start, date_end, reason)

    return JsonResponse({"status": "ok", "added_count": added_count})


@login_required
@require_POST
def remove_absences_view(request):
    """
    Remove user absences if existing

    body should be

    {
        dateStart: "2026-05-20"
        dateStart: "2026-05-25"  // not included, calendar will set 20 to 24 included
    }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return []

    date_start = __to_date(data.get("dateStart"))
    date_end = __to_date(data.get("dateEnd"))

    removed_count = remove_absences(request.user, date_start, date_end)

    return JsonResponse({"status": "ok", "removed_count": removed_count})


@login_required
def get_user_calendar_events(request):
    user = request.user

    data = request.GET.copy()

    race_types = data.getlist("race_type")
    if len(race_types) == 1 and "," in race_types[0]:
        # On le transforme en vraie liste ['trail', 'road']
        data.setlist("race_type", race_types[0].split(","))

    status = data.getlist("status")
    if len(status) == 1 and "," in status[0]:
        # On le transforme en vraie liste ['trail', 'road']
        data.setlist("status", status[0].split(","))

    print("GET:", request.GET)

    start_param = request.GET.get("start")
    end_param = request.GET.get("end")

    if start_param:
        start = __to_date(start_param)
    else:
        start = datetime.date.today()

    if end_param:
        end = __to_date(end_param)
    else:
        # Maximum is 6 weeks
        end = start + datetime.timedelta(days=42)

    result = []

    # Parse Filters
    form = PlanningFilterForm(data)

    city = None
    radius = None
    race_types = None
    min_distance = None
    max_distance = None
    statuses = None
    show_favorites = True  # Default
    print(form.is_valid())
    from pprint import pprint

    pprint(form.errors.as_json())
    if form.is_valid():
        print("Form is valid")
        data = form.cleaned_data

        city_id = data.get("city")
        if city_id:
            city = City.objects.filter(id=city_id).first()
        elif (
            not request.GET.get("city")
            and request.user.is_authenticated
            and hasattr(request.user, "city")
            and request.user.city
        ):
            # If city not in GET (not just empty, but missing key), implies initial load or reset?
            # But if the form is in the UI, it should send the value (empty or not).
            # If we rely on JS to gather form data, empty value means empty value.
            # We only use user city if the form logic intends to default to it.
            # The form initial=user.city. So the UI should have it selected.
            # If user clears it, it sends empty. We should respect "empty".
            pass

        if data.get("radius"):
            radius = data.get("radius")

        race_types = data.get("race_type")
        min_distance = data.get("min_distance")
        max_distance = data.get("max_distance")
        statuses = data.get("status")

        print(race_types, min_distance, max_distance, statuses)

        # BooleanField False if unchecked or missing.
        # But if missing (not in GET), we might want default?
        # If 'show_favorites' key is missing from GET, form.cleaned_data['show_favorites'] is False.
        # If the user UNCHECKS it, it is also missing from GET (standard HTML checkbox).
        # So we can't distinguish "unchecked" from "missing" easily without a hidden field or JS.
        # However, `FullCalendar` requests usually won't include form fields unless we add them.
        # On first load, `show_favorites` is missing. We want it TRUE.
        # On subsequent loads (triggered by form), if unchecked, it is missing. We want it FALSE.
        # This is ambiguous.
        # Solution: Use JS to serialize the form. JS should serialize unchecked checkboxes as false?
        # Standard form submission doesn't send unchecked boxes.
        # If we use `new FormData(form)`, it doesn't include unchecked.
        # We can add a hidden input with same name="show_favorites" value="False" before the checkbox?
        # Django doesn't automatically handle that well for BooleanField (it expects one value).
        # Actually, `initial` in form is used for rendering.
        # I'll rely on the frontend sending the parameter.
        # If I strictly follow `form.cleaned_data`, missing = False.
        # So on first load (no params), it will be False.
        # I can check `if not request.GET:` (start/end are in GET though).
        # `if 'show_favorites' not in request.GET`:
        #    if it's an "initial" load (no form data at all), maybe default True?
        #    How to detect initial load? Check for presence of ANY form field?
        #    If `radius` is missing, likely initial load.

        if "radius" not in request.GET:
            # Likely initial load, force defaults
            show_favorites = True
            # Maybe default city too?
            if request.user.is_authenticated and hasattr(request.user, "city") and request.user.city:
                city = request.user.city
        else:
            show_favorites = data.get("show_favorites")

    absences = get_absences(user, start, end)
    for absence in absences:
        result.append(
            {
                "id": f"absence_{absence.id}",
                "title": absence.reason,
                "start": absence.date.strftime("%Y-%m-%d"),
                "backgroundColor": "#c5c5c5",
                "display": "background",
            }
        )

    races = get_race(
        user,
        start,
        end,
        city=city,
        radius=radius,
        race_types=race_types,
        min_distance=min_distance,
        max_distance=max_distance,
        statuses=statuses,
        show_favorites=show_favorites,
    )

    for race in races:
        result.append(
            {
                "id": f"race_{race.id}",
                "title": race.name,
                "start": race.date_course,
                "backgroundColor": "#059669" if race.race_type == "trail" else "#2563eb",
                "borderColor": "#047857" if race.race_type == "trail" else "#1d4ed8",
                "extendedProps": {},
            }
        )

    return JsonResponse(result, safe=False)
