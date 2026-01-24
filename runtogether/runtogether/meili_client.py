import meilisearch
from django.conf import settings

client = meilisearch.Client(settings.MEILI_URL, settings.MEILI_MASTER_KEY)
