from django.contrib import admin
from .models import Race
from django.contrib.gis.admin import GISModelAdmin


@admin.register(Race)
class RaceAdmin(GISModelAdmin):
    list_display = (
        "name",
        "date_course",
        "city",
        "race_type",
        "inscription_status",
        "private",
    )
    list_filter = (
        "race_type",
        "inscription_status",
        "private",
        "date_course",
        "date_validated",
    )
    search_fields = ("name", "city__name")
    autocomplete_fields = ["city", "club_owner"]
