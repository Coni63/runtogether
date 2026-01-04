from django.shortcuts import render


def list_clubs(request):
    return render(request, "club/clubs.html")
