from django.db import models
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class Club(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)
    description = StreamField([
        ('heading', blocks.CharBlock(form_classname="title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ], use_json_field=True, blank=True, null=True)
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
