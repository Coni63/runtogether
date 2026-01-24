from django.http import JsonResponse
from django.shortcuts import render
from unidecode import unidecode  # pip install unidecode
from runtogether.meili_client import client
from .models import City
from django.contrib.postgres.search import TrigramSimilarity
from .services import search_city_by_name


def city_autocomplete(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:  # Minimum 2 caractères
        return JsonResponse({"results": []})

    results = search_city_by_name(query, n=20)
    return render(
        request,
        "city/partials/search_results.html",
        {
            "results": results,
        },
    )
