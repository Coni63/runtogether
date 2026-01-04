from django.shortcuts import render


# Create your views here.
def list_races(request):
    return render(request, "race/races.html")
