from django.urls import path
from . import views

app_name = "map"

urlpatterns = [
    path("", views.map_view, name="map"),
    path("api/points/", views.get_points, name="get_points"),
]
