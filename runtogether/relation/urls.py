from django.urls import path

from . import views

app_name = "relation"

urlpatterns = [
    path("update-status/<int:race_id>/", views.update_race_status, name="update_race_status"),
    path("toggle-favorite/<int:race_id>/", views.toggle_race_favorite, name="toggle_race_favorite"),
]
