from django.contrib import admin

from .models import Club, ClubMembership


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "created_at", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active", "created_at")
    autocomplete_fields = ["city"]


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ("club", "user", "role", "joined_at", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("club__name", "user__email")
    autocomplete_fields = ["club", "user"]
