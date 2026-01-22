from django.db import models
from django_editorjs_fields import EditorJsJSONField


class Club(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)
    description = EditorJsJSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    members = models.ManyToManyField("accounts.User", through="relation.ClubMembership", related_name="clubs")
    city = models.ForeignKey(
        "city.City",
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="clubs",
        help_text="City where the user resides",
    )
