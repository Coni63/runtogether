from django.urls import path

from . import views

app_name = "race"

urlpatterns = [
    path(
        "",
        views.get_races_page,
        name="list",
    ),
    path("create/", views.publish_new_race, name="create_race"),
]
