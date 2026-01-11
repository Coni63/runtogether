from django.contrib import admin
from .models import RaceUser


@admin.register(RaceUser)
class RaceUserAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "status", "favorited", "created_at", "updated_at")
    list_filter = ("status", "favorited", "created_at")
    search_fields = ("user__email", "user__username", "race__name")
    autocomplete_fields = ["user", "race"]