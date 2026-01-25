from django.urls import path

from . import views

app_name = "race"

urlpatterns = [
    path(
        "",
        views.list_races,
        name="list",
    ),
    path("create/", views.publish_new_race, name="create_race"),
]
