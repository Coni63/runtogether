from django.shortcuts import render


def load_calendar(request):
    return render(request, "planning/planning.html")


from django.http import JsonResponse


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
