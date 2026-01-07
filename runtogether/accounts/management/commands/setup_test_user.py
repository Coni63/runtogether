import csv
import io
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
import requests
from accounts.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create test user if not exists
        test_email = "test@example.com"
        test_user, created = User.objects.get_or_create(
            email=test_email,
            defaults={
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "is_active": True,
                "strava_url": "https://www.strava.com/athletes/testuser",
                "garmin_url": "https://connect.garmin.com/modern/profile/testuser",
                "city_id": 2972811,  # Thionville
            },
        )

        test_user.set_password("password")
        test_user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created test user: {test_email}"))
        else:
            self.stdout.write(self.style.WARNING(f"Test user already exists: {test_email}"))
