from django.urls import path

from . import views

app_name = "planning"

urlpatterns = [
    path(
        "",
        views.load_calendar_page,
        name="planning",
    ),
    path(
        "events/",
        views.get_calendar_events,
        name="events",
    ),
    path("set_absences", views.set_absences_view, name="set_absences"),
    path("remove_absences", views.remove_absences_view, name="remove_absences"),
]
