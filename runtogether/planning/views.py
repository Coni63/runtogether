import datetime
import json
from django.db import IntegrityError
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Absence


def __to_date(dt: str) -> datetime.date:
    if not dt:
        return None

    try:
        return datetime.datetime.strptime(dt, "%Y-%m-%d").date()
    except:
        return None


def __generate_list_of_dates(data: dict):
    date_start = __to_date(data.get("dateStart"))
    date_end = __to_date(data.get("dateEnd"))

    if date_start and date_end:
        # the library provides dates sorted but safety
        if date_end < date_start:
            date_start, date_end = date_end, date_start

        numdays = (date_end - date_start).days  # attention, the library return the next day after selection so no need for +1
        return [date_start + datetime.timedelta(days=x) for x in range(numdays)]
    return []


@login_required
def load_calendar_page(request):
    return render(request, "planning/planning.html")


@login_required
@require_POST
def set_absences(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return []

    date_list = __generate_list_of_dates(data)
    reason = data.get("reason")

    if date_list:
        absences_to_create = [Absence(user=request.user, date=d, reason=reason) for d in date_list]

        # ignore_conflicts=True permet de sauter les erreurs d'unicité (IntegrityError)
        Absence.objects.bulk_create(
            absences_to_create, update_conflicts=True, update_fields=["reason"], unique_fields=["user", "date"]
        )

    return JsonResponse({"status": "ok", "added_count": len(date_list)})


@login_required
@require_POST
def remove_absences(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return []

    date_list = date_list = __generate_list_of_dates(data)

    if date_list:
        Absence.objects.filter(user=request.user, date__in=date_list).delete()

    return JsonResponse({"status": "ok", "removed_count": len(date_list)})


@login_required
def get_calendar_events(request):
    test = [
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

    return JsonResponse(test, safe=False)
