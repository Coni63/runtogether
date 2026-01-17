import logging

# from core.mixins import ProjectAdminRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserEditForm

User = get_user_model()
logger = logging.getLogger(__name__)


@login_required  # Ensures only logged-in users can access this view
def my_profile(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Update saved !")
            return redirect("user:profile")
        else:
            messages.warning(request, "Invalid form")
            # If the form is NOT valid, fall through to render the template with errors

    else:  # This handles the initial GET request
        form = UserEditForm(instance=request.user)

    # 4. Render the correct template with the current user and the form
    return render(request, "accounts/profile.html", {"user": request.user, "form": form})
