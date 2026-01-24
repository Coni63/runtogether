import csv
from datetime import datetime
from decimal import Decimal

from city.models import City
from django.core.management.base import BaseCommand
from django.db import connection
from race.models import Race
from city.services import search_city_by_name


class Command(BaseCommand):
    help = "Populate the table using a csv manually created"

    label = {
        "Inscriptions non ouvertes": "not_open",
        "Inscriptions en cours": "open",
        "Inscriptions terminées": "closed",
        "Course terminée": "terminated",
    }

    map_race_type = {
        "Trail": "trail",
        "Route": "road",
    }

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force complete refresh of all races")

    def handle(self, *args, **options):
        # Fetch existing races from database
        self.stdout.write("Truncating Table")
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE race_race RESTART IDENTITY CASCADE;")

        to_create = []

        self.stdout.write("Loading data...")
        with open("data/Courses 2026 - Courses.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header line
            for i, line in enumerate(reader):
                try:
                    date_str = line[1]

                    course = line[0]

                    if not course:
                        continue

                    # print(line)
                    date_course = datetime.strptime(date_str, "%d/%m/%Y").date()
                    date_validated = not date_str.startswith("01")
                    inscription_status = self.label[line[2]]
                    date_inscriptions_open = datetime.strptime(line[3], "%d/%m/%Y").date() if line[3] else None
                    city = line[4]
                    race_type = self.map_race_type[line[5]]
                    distance = [Decimal(d.strip().replace(",", ".")) for d in line[6].split("-")] if line[6] else []
                    url_race = line[8]
                    url_inscriptions = line[9]

                    results = search_city_by_name(city, 1)
                    if not results:
                        raise AttributeError

                    city_record = City.objects.get(id=results[0]["id"])

                    obj = Race(
                        id=i,
                        name=course,
                        date_course=date_course,
                        date_validated=date_validated,
                        inscription_status=inscription_status,
                        date_inscriptions_open=date_inscriptions_open,
                        city=city_record,
                        latitude=city_record.latitude,
                        longitude=city_record.longitude,
                        location=city_record.location,
                        race_type=race_type,
                        private=False,
                        club_owner=None,
                        url_race=url_race,
                        url_inscriptions=url_inscriptions,
                        distance=distance,
                    )

                    to_create.append(obj)
                except (IndexError, ValueError):
                    continue
                except AttributeError:
                    self.stdout.write(self.style.WARNING(f"City '{city}' not found in database."))

            # Bulk Create
            if to_create:
                self.stdout.write(f"Creating {len(to_create)} new cities...")
                Race.objects.bulk_create(to_create, batch_size=5000)

            self.stdout.write(self.style.SUCCESS(f"Done! Created: {len(to_create)}"))
