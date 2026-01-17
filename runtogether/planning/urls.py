from django.urls import path

from . import views

app_name = "planning"

urlpatterns = [
    path(
        "",
        views.load_calendar,
        name="planning",
    ),
    path(
        "events/",
        views.get_calendar_events,
        name="events",
    ),
]
