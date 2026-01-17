from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("", views.my_profile, name="profile"),
]
