from django.db import models


class Club(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)
    description = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    members = models.ManyToManyField("accounts.User", through="club.ClubMembership", related_name="clubs")
    city = models.ForeignKey(
        "city.City",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="residents",
        help_text="City where the user resides",
    )


class ClubMembership(models.Model):
    club = models.ForeignKey("club.Club", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[("admin", "Admin"), ("member", "Member")],
        default="member",
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("club", "user")
