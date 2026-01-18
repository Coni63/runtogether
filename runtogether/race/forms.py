from datetime import date

from dateutil.relativedelta import relativedelta  # pip install python-dateutil
from django import forms

from .models import RACE_TYPE


class RaceFilterForm(forms.Form):
    city = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"type": "hidden"}))

    radius = forms.IntegerField(
        initial=40,
        required=True,
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

    date_after = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    date_before = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    min_distance = forms.FloatField(
        required=False, initial=0, widget=forms.NumberInput(attrs={"type": "hidden", "id": "min-distance"})
    )
    max_distance = forms.FloatField(
        required=False, initial=200, widget=forms.NumberInput(attrs={"type": "hidden", "id": "max-distance"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()
        six_months = today + relativedelta(months=6)

        # N'appliquer les defaults que si le champ n’est PAS déjà dans la requête
        if not self.is_bound:
            self.initial["date_after"] = today
            self.initial["date_before"] = six_months
