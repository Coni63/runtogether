from django import forms
from .models import RACE_TYPE


class RaceFilterForm(forms.Form):
    city = forms.IntegerField(required=False, label="City", widget=forms.NumberInput(attrs={"type": "hidden"}))
    radius = forms.IntegerField(
        initial=40,
        required=True,
        label="Radius (km)",
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "min": "0",
                "max": "200",
                "value": "40",
                "step": "5",
                "class": "range range-xs range-primary",
                "oninput": "document.getElementById('radius-val').textContent = this.value + ' km'",
            }
        ),
    )
    race_type = forms.ChoiceField(choices=[("", "All Types")] + list(RACE_TYPE), required=False, label="Type")
    date_after = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="After Date")
    date_before = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Before Date")
    min_distance = forms.FloatField(
        required=False, initial=0, widget=forms.NumberInput(attrs={"type": "hidden", "id": "min-distance"})
    )
    max_distance = forms.FloatField(
        required=False, initial=200, widget=forms.NumberInput(attrs={"type": "hidden", "id": "max-distance"})
    )
