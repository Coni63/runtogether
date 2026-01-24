from runtogether.meili_client import client
from .models import City
from django.contrib.postgres.search import TrigramSimilarity
from unidecode import unidecode


def search_city_by_name(name, n: int = 20):
    try:
        index = client.index("cities")

        # Recherche
        search_results = index.search(
            name,
            {
                "limit": n,
                "attributesToRetrieve": ["id", "name", "country"],
            },
        )
        return search_results["hits"]
    except Exception as e:  # In case of issues, fallback to DB search
        print("ERROR in meilisearch:", e)

        clean_query = unidecode(name.lower())

        cities = City.objects.annotate(sim=TrigramSimilarity("name", clean_query)).filter(sim__gt=0.3).order_by("-sim")[:n]

        return cities
