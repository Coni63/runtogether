from django.http import JsonResponse
from django.shortcuts import render
from unidecode import unidecode  # pip install unidecode

from .models import City


def city_autocomplete(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:  # Minimum 2 caractères
        return JsonResponse({"results": []})

    clean_query = unidecode(query.lower())

    cities = (
        City.objects.filter(clean_name__istartswith=clean_query).order_by("-population").values("id", "name", "country")[:20]
    )

    return render(
        request,
        "city/partials/search_results.html",
        {
            "results": cities,
        },
    )
