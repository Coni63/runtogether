import datetime
import json
from django.db import IntegrityError
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Absence
from .services import set_or_update_absences, get_absences, remove_absences
import contextlib


def __to_date(dt: str) -> datetime.date:
    if not dt:
        return None

    with contextlib.suppress(Exception):
        return datetime.datetime.strptime(dt[:10], "%Y-%m-%d").date()

    return None


@login_required
def load_calendar_page(request):
    return render(request, "planning/planning.html")


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
def get_calendar_events(request):
    user = request.user

    start = __to_date(request.GET.get("start")[:10])
    end = __to_date(request.GET.get("end")[:10])

    result = [
        {
            "id": 1,
            "title": "Indisponible",
            "start": "2026-01-05",
            "end": "2026-01-08",
            "display": "background",
            "color": "#c5c5c5",
        },
        {"id": 2, "title": "Indisponible", "start": "2026-01-20", "display": "background", "color": "#c5c5c5"},
        {
            "id": 3,
            "title": "10km de Paris (Route)",
            "start": "2026-01-11",
            "backgroundColor": "#2563eb",
            "borderColor": "#1d4ed8",
            "extendedProps": {"type": "route", "distance": "10km"},
        },
        {
            "id": 4,
            "title": "Trail des Sapins",
            "start": "2026-01-25",
            "backgroundColor": "#059669",
            "borderColor": "#047857",
            "extendedProps": {"type": "trail", "distance": "25km"},
        },
        {
            "id": 4,
            "title": "Semi du Mans",
            "start": "2026-01-25",
            "backgroundColor": "#2563eb",
            "borderColor": "#1d4ed8",
            "extendedProps": {"type": "route", "distance": "21km"},
        },
    ]

    absences = get_absences(user, start, end)
    for absence in absences:
        result.append(
            {
                "id": 4,
                "title": absence.reason,
                "start": absence.date.strftime("%Y-%m-%d"),
                "backgroundColor": "#c5c5c5",
                "display": "background",
            }
        )

    return JsonResponse(result, safe=False)
