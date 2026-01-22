from django.urls import path

from . import views

app_name = "club"

urlpatterns = [
    path(
        "",
        views.list_clubs,
        name="list",
    ),
    path(
        "<int:club_id>/",
        views.get_club_details,
        name="details",
    ),
]
