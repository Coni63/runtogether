from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import City


@admin.register(City)
class CityAdmin(GISModelAdmin):
    list_display = ("name", "country", "population", "last_modified")
    list_filter = ("country",)
    search_fields = ("name", "clean_name")
