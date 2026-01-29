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
        "absences/",
        views.get_user_absences,
        name="absences",
    ),
    path("set_absences", views.set_absences_view, name="set_absences"),
    path("remove_absences", views.remove_absences_view, name="remove_absences"),
]
