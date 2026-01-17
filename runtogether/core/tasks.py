import logging
from django.core.mail import send_mail
from django.tasks import task
from celery import shared_task
import time

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def email_users(self, emails, subject, message):
    try:
        logger.info(f"Attempt {self.request.retries} to send user email. Task result id: {self.request.id}.")
        return send_mail(subject=subject, message=message, from_email=None, recipient_list=emails)
    except Exception as e:
        logger.error("exception raised, it would be retry after 5 seconds")
        raise self.retry(exc=e, countdown=5)


@shared_task
def addition_lente(x, y):
    time.sleep(5)  # Simule un travail long
    return x + y
