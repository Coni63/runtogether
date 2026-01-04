import logging

from core.exceptions import InvalidParameterError, RecordNotFoundError

# from core.mixins import ProjectAdminRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.base import View
from django_htmx.http import reswap

from .forms import BasicRegisterForm, UserEditForm
# from .services import AccountService

User = get_user_model()
logger = logging.getLogger(__name__)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home:homepage")

    if request.method == "GET":
        form = AuthenticationForm()
        return render(request, "accounts/login.html", {"form": form})
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home:homepage")
        else:
            return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home:homepage")

    if request.method == "POST":
        form = BasicRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home:homepage")
        else:
            return render(request, "accounts/register.html", {"form": form})
    else:
        form = BasicRegisterForm()
        return render(request, "accounts/register.html", {"form": form})


@login_required  # Ensures only logged-in users can access this view
def my_profile(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Update saved !")
            return redirect("accounts:profile")
        else:
            messages.warning(request, "Invalid form")
            # If the form is NOT valid, fall through to render the template with errors

    else:  # This handles the initial GET request
        form = UserEditForm(instance=request.user)

    # 4. Render the correct template with the current user and the form
    return render(request, "accounts/profile.html", {"user": request.user, "form": form})
