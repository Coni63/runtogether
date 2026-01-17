from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("", views.my_profile, name="profile"),
]
