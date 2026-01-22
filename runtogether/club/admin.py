from django.contrib import admin
from .models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "created_at", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active", "created_at")
    autocomplete_fields = ["city"]
