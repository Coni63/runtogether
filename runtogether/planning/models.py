from django.db import models


class Absence(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="absences")
    date = models.DateField()
    reason = models.CharField(max_length=50, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "date"], name="unique_user_absence_date")]
