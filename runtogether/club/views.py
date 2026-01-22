from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from city.models import City
from .services import get_club, create_club
from .forms import ClubForm


def list_clubs(request):
    # result = email_users.delay(
    #     emails=["user@example.com"],
    #     subject="You have a message",
    #     message="Hello there!",
    # )

    # print(result.status)

    # from core.tasks import addition_lente

    # result = addition_lente.delay(10, 20)
    # print(result.status)  # Devrait être 'PENDING' ou 'SUCCESS'

    return render(request, "club/clubs.html")


@login_required
def get_club_details(request, club_id):
    club = get_club(club_id)
    if not club:
        city = City.objects.filter(clean_name="Thionville").first()
        club = create_club("Test", city)

    form = ClubForm(request.POST or None, instance=club)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("club:details", club_id=club.id)

    return render(request, "club/clubs.html", context={"club": club, "form": form})
