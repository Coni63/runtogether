import csv
from decimal import Decimal
import io
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
import requests
from race.models import Race
from django.contrib.gis.geos import Point

from city.models import City


class Command(BaseCommand):
    help = "Populate the table using a csv manually created"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force complete refresh of all races")

    def handle(self, *args, **options):
        # Fetch existing races from database
        self.stdout.write("Fetching existing races from database...")
        existing_races = {c.id for c in Race.objects.all()}

        to_create = []
        to_update = []

        self.stdout.write("Loading data...")
        with open("data/Courses 2026 - Courses.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header line
            for i, line in enumerate(reader):
                print(line)
                try:
                    date_str = line[1]

                    course = line[0]

                    if not course:
                        continue

                    date_course = datetime.strptime(date_str, "%d/%m/%Y").date()
                    date_validated = not date_str.startswith("01")
                    inscription_status = line[2]
                    date_inscriptions_open = datetime.strptime(line[3], "%d/%m/%Y").date() if line[3] else None
                    city = line[4]
                    race_type = line[5]
                    private = False
                    distance = [Decimal(d.strip().replace(",", ".")) for d in line[6].split("-")] if line[6] else []
                    url_race = line[7]
                    url_inscriptions = line[8]

                    qs = City.objects.filter(name__istartswith=city)
                    print(qs.first())
                    city_record = qs.first().name if qs.exists() else None
                    if city_record:
                        latitude = city_record.latitude
                        longitude = city_record.longitude
                    else:
                        latitude = None
                        longitude = None

                    obj = Race(
                        id=i,
                        name=course,
                        date_course=date_course,
                        date_validated=date_validated,
                        inscription_status=inscription_status,
                        date_inscriptions_open=date_inscriptions_open,
                        city=city,
                        latitude=latitude,
                        longitude=longitude,
                        location=Point(longitude, latitude),
                        race_type=race_type,
                        private=private,
                        url_race=url_race,
                        url_inscriptions=url_inscriptions,
                        distance=distance,
                    )

                    if i not in existing_races:
                        to_create.append(obj)
                    elif options["force"]:
                        to_update.append(obj)
                except (IndexError, ValueError):
                    continue
                except AttributeError:
                    self.stdout.write(self.style.WARNING(f"City '{city}' not found in database."))

            return

            # Bulk Create
            if to_create:
                self.stdout.write(f"Creating {len(to_create)} new cities...")
                Race.objects.bulk_create(to_create, batch_size=5000)

            # Bulk Update
            if to_update:
                self.stdout.write(f"Updating {len(to_update)} cities...")
                Race.objects.bulk_update(
                    to_update,
                    [
                        "name",
                        "date_course",
                        "date_validated",
                        "inscription_status",
                        "date_inscriptions_open",
                        "city",
                        "latitude",
                        "longitude",
                        "location",
                        "race_type",
                        "private",
                        "url_race",
                        "url_inscriptions",
                    ],
                    batch_size=5000,
                )

            self.stdout.write(self.style.SUCCESS(f"Done! Created: {len(to_create)}, Updated: {len(to_update)}"))
