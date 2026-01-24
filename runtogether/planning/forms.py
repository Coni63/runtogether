from django import forms
from race.models import RACE_TYPE
from relation.models import RaceUser


class PlanningFilterForm(forms.Form):
    city = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"type": "hidden"}))

    radius = forms.IntegerField(
        initial=40,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "min": "0",
                "max": "200",
                "step": "5",
                "class": "range range-xs range-primary",
                "oninput": "document.getElementById('radius-val').textContent = this.value + ' km'",
            }
        ),
    )

    race_type = forms.MultipleChoiceField(
        choices=RACE_TYPE, required=False, widget=forms.CheckboxSelectMultiple, initial=["trail", "road"]
    )

    min_distance = forms.FloatField(
        required=False, initial=0, widget=forms.NumberInput(attrs={"type": "hidden", "id": "min-distance"})
    )
    max_distance = forms.FloatField(
        required=False, initial=200, widget=forms.NumberInput(attrs={"type": "hidden", "id": "max-distance"})
    )

    STATUS_CHOICES = [
        (RaceUser.Status.REGISTERED, "Inscrit"),
        (RaceUser.Status.INTERESTED, "Intéressé"),
        (RaceUser.Status.SEARCH_BIB, "Cherche dossard"),
    ]

    status = forms.MultipleChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.CheckboxSelectMultiple, initial=[])

    show_favorites = forms.BooleanField(
        required=False,
        label="Favoris",
        widget=forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary checkbox-sm"}),
        initial=False,
    )
