from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from city.models import City
from runtogether.meili_client import client


class Command(BaseCommand):
    help = "Indexe toutes les villes dans Meilisearch par paquets"

    def handle(self, *args, **kwargs):
        index = client.index("cities", {"primaryKey": "id"})

        # On récupère le QuerySet (pas encore chargé en mémoire)
        villes_queryset = City.objects.values("id", "name", "country").order_by("id")

        # On découpe par paquets de 1000
        paginator = Paginator(villes_queryset, 1000)

        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            # On convertit la page en liste de dictionnaires
            villes_batch = list(page.object_list)

            # Envoi du paquet à Meilisearch
            index.add_documents(villes_batch)

            self.stdout.write(f"Batch {page_num}/{paginator.num_pages} envoyé...")

        self.stdout.write(self.style.SUCCESS(f"Successfully indexed {paginator.count} cities"))
