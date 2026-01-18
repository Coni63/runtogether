import os

from celery import Celery

# Définit le module de réglages par défaut de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "runtogether.settings")

celery = Celery("runtogether")

# Utilise les réglages de Django, les clés de config Celery commencent par CELERY_
celery.config_from_object("django.conf:settings", namespace="CELERY")

# Découvre automatiquement les tâches dans vos apps (tasks.py)
celery.autodiscover_tasks()
