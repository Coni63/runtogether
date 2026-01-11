from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from race.models import Race
from .models import RaceUser
from .services import set_favorited, remove_favorited, set_status


@login_required
@require_POST
def update_race_status(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    status = request.POST.get("status")

    if status not in RaceUser.Status.values:
        return HttpResponse("Invalid status", status=400)

    record = set_status(request.user, race, status)

    if record:
        return render(request, "relation/partials/race_status_dropdown.html", {"race": {"id": race.id, "user_status": status}})
    else:
        return render(request, "relation/partials/race_status_dropdown.html", {"race": {"id": race.id, "user_status": "none"}})


@login_required
@require_POST
def toggle_race_favorite(request, race_id):
    # favorited is the state we expect. If the race is favoritd, send false. In that case, remove the favorite
    favorited = request.POST.get("favorited") == "true"
    race = get_object_or_404(Race, id=race_id)

    if favorited:
        set_favorited(request.user, race)
    else:
        remove_favorited(request.user, race)

    return render(request, "relation/partials/favorite_star.html", {"race": {"id": race.id, "user_favorited": favorited}})
