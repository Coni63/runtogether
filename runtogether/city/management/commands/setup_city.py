import csv
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from city.models import City


class Command(BaseCommand):
    """
    URL of csv zipped: https://download.geonames.org/export/dump/cities500.zip

    The main 'geoname' table has the following fields :
    ---------------------------------------------------
    geonameid         : integer id of record in geonames database
    name              : name of geographical point (utf8) varchar(200)
    asciiname         : name of geographical point in plain ascii characters, varchar(200)
    alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
    latitude          : latitude in decimal degrees (wgs84)
    longitude         : longitude in decimal degrees (wgs84)
    feature class     : see http://www.geonames.org/export/codes.html, char(1)
    feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
    country code      : ISO-3166 2-letter country code, 2 characters
    cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
    admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
    admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80)
    admin3 code       : code for third level administrative division, varchar(20)
    admin4 code       : code for fourth level administrative division, varchar(20)
    population        : bigint (8 byte int)
    elevation         : in meters, integer
    dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
    timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
    modification date : date of last modification in yyyy-MM-dd format
    """

    help = "Populate the table using GeoNames dataset"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)

    def handle(self, *args, **options):
        filepath = Path(options["path"])
        if not filepath.exists():
            self.stdout.write(self.style.ERROR(f'File not found "{filepath}"'))
            return

        # 1. On récupère l'existant en RAM pour comparer
        # On stocke {id: last_modified}
        self.stdout.write("Fetching existing cities from database...")
        existing_cities = {c.id: c.last_modified for c in City.objects.all()}

        to_create = []
        to_update = []

        self.stdout.write("Parsing CSV and comparing data...")
        with open(filepath, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")

            for line in reader:
                try:
                    geonameid = int(line[0])
                    name = line[1]
                    clean_name = line[2]
                    latitude = line[4]
                    longitude = line[5]
                    country = line[8]
                    last_modified = datetime.strptime(line[18], "%Y-%m-%d").date()

                    if len(name) > 60 or len(clean_name) > 60:
                        print(f"Skip: {name}")
                        continue

                    city_obj = City(
                        id=geonameid,
                        name=name,
                        clean_name=clean_name,
                        latitude=latitude,
                        longitude=longitude,
                        country=country,
                        last_modified=last_modified,
                    )

                    if geonameid not in existing_cities:
                        to_create.append(city_obj)
                    elif last_modified > existing_cities[geonameid]:
                        to_update.append(city_obj)
                except (IndexError, ValueError):
                    continue

        # 2. Bulk Create (par lots de 5000 pour ne pas saturer la RAM/SQL)
        if to_create:
            self.stdout.write(f"Creating {len(to_create)} new cities...")
            City.objects.bulk_create(to_create, batch_size=5000)

        # 3. Bulk Update
        if to_update:
            self.stdout.write(f"Updating {len(to_update)} cities...")
            City.objects.bulk_update(
                to_update, ["name", "clean_name", "latitude", "longitude", "country", "last_modified"], batch_size=5000
            )

        self.stdout.write(self.style.SUCCESS(f"Done! Created: {len(to_create)}, Updated: {len(to_update)}"))
