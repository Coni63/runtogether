from django.contrib import admin

from .models import RaceUser, ClubMembership


@admin.register(RaceUser)
class RaceUserAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "status", "favorited", "created_at", "updated_at")
    list_filter = ("status", "favorited", "created_at")
    search_fields = ("user__email", "user__username", "race__name")
    autocomplete_fields = ["user", "race"]


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ("club", "user", "role", "joined_at", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("club__name", "user__email")
    autocomplete_fields = ["club", "user"]
