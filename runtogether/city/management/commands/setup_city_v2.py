import csv
import io
import zipfile
from datetime import datetime
import pickle
import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import connection
from city.models import City


class Command(BaseCommand):
    """
    Uses a preprocess dataset from OpenStreetmap.

    Data is

    [
        {
            'name': 'Charleroi',
            'type': 'city',
            'lat': 50.4116233,
            'lon': 4.444528,
            'country': 'Belgium',
            'id': 1234567
        }, {
            'name': 'Raidelbach',
            'type': 'village',
            'lat': 49.709349,
            'lon': 8.7352499,
            'country': 'Germany',
            'id': 987654
        }
    ]
    """

    help = "Populate the table using GeoNames dataset (auto-downloads from GeoNames.org)"
    ALLOWED_COUNTRIES = ["Germany", "Luxembourg", "Belgium", "France", "Switzerland", "Netherlands"]

    def add_arguments(self, parser):
        parser.add_argument("--file", help="Path of the preprocess file")

    def handle(self, *args, **options):
        with open(options["file"], "rb") as f:
            data = pickle.load(f)

        self.stdout.write("Truncating Table")
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE city_city RESTART IDENTITY CASCADE;")

        # Fetch existing cities from database
        self.stdout.write("Creating cities")

        to_create = []
        for city in data:
            try:
                if len(city["name"]) > 60:
                    print(f"Skip: {city['name']}")
                    continue

                if city.get("country") not in self.ALLOWED_COUNTRIES:
                    continue

                city_obj = City(
                    id=city["id"],
                    name=city["name"],
                    latitude=city["lat"],
                    longitude=city["lon"],
                    location=Point(city["lon"], city["lat"]),
                    country=city["country"],
                )

                to_create.append(city_obj)
            except (IndexError, ValueError):
                continue

        # Bulk Create
        if to_create:
            self.stdout.write(f"Creating {len(to_create)} new cities...")
            City.objects.bulk_create(to_create, batch_size=5000)

        self.stdout.write(self.style.SUCCESS(f"Done! Created: {len(to_create)}"))
