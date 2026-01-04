from django.http import JsonResponse
from django.db.models import Q
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

    results = [{"id": c["id"], "name": c["name"], "country": c["country"]} for c in cities]
    return JsonResponse({"results": results})
