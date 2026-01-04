from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "search/",
        views.city_autocomplete,
        name="city_autocomplete",
    ),
]
