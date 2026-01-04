from django.http import JsonResponse
from django.db.models import Q
from unidecode import unidecode  # pip install unidecode
from .models import City


def city_autocomplete(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:  # Minimum 2 caractères
        return JsonResponse({"results": []})

    # Nettoyer l'input utilisateur
    clean_query = unidecode(query.lower())

    # Recherche optimisée avec LIMIT
    cities = City.objects.filter(
        clean_name__istartswith=clean_query  # istartswith est plus rapide que icontains
    ).values("id", "name")[:20]  # Limiter à 20 résultats

    results = [{"id": c["id"], "text": c["name"]} for c in cities]
    return JsonResponse({"results": results})
