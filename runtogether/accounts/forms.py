from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserEditForm(forms.ModelForm):
    """
    Form used to update an existing Django User instance's profile information.
    Defines the fields, widgets, labels, and help_texts for the form,
    focusing on basic user details like name and email.
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "city", "strava_url", "garmin_url"]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your first name",
                    "autofocus": True,
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your last name",
                }
            ),
            "city": forms.HiddenInput(),
            "strava_url": forms.URLInput(
                attrs={
                    "placeholder": "Enter your Strava profile URL",
                }
            ),
            "garmin_url": forms.URLInput(
                attrs={
                    "placeholder": "Enter your Garmin profile URL",
                }
            ),
        }

        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "city": "City",
            "strava_url": "Strava Profile URL",
            "garmin_url": "Garmin Profile URL",
        }

        help_texts = {
            "first_name": None,
            "last_name": None,
            "strava_url": None,
            "garmin_url": None,
        }
