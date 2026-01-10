from django.db import models
from django.db.models import Q


class RaceUser(models.Model):
    class Status(models.TextChoices):
        NONE = "none", "Aucun lien"
        INTERESTED = "interested", "Intéressé"
        REGISTERED = "registered", "Inscrit"
        SEARCH_BIB = "search_bib", "Cherche un dossard"

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="race_links")
    race = models.ForeignKey("race.Race", on_delete=models.CASCADE, related_name="user_links")
    liked = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NONE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "race"], name="unique_user_race"),
            models.CheckConstraint(check=Q(liked=True) | ~Q(status="none"), name="must_have_like_or_status"),
        ]
