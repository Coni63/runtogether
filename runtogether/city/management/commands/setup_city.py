import csv
import io
import zipfile
from datetime import datetime

import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from city.models import City


class Command(BaseCommand):
    """
    Automatically downloads and processes GeoNames cities500.zip dataset.

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

    help = "Populate the table using GeoNames dataset (auto-downloads from GeoNames.org)"

    GEONAMES_URL = "https://download.geonames.org/export/dump/cities500.zip"
    EXPECTED_FILENAME = "cities500.txt"
    ALLOWED_COUNTRIES = ["FR", "LU", "BE", "DE", "CH", "IT", "ES"]

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force complete refresh of all cities")

    def handle(self, *args, **options):
        # Download the ZIP file
        self.stdout.write("Downloading GeoNames dataset...")
        try:
            response = requests.get(self.GEONAMES_URL, stream=True, timeout=60)
            response.raise_for_status()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Failed to download file: {e}"))
            return

        # Extract the txt file from ZIP in memory
        self.stdout.write("Extracting data from ZIP...")
        try:
            zip_content = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_content, "r") as zip_ref:
                # Read the cities500.txt file directly from the ZIP
                if self.EXPECTED_FILENAME not in zip_ref.namelist():
                    self.stdout.write(self.style.ERROR(f'Expected file "{self.EXPECTED_FILENAME}" not found in ZIP'))
                    return

                txt_content = zip_ref.read(self.EXPECTED_FILENAME).decode("utf-8")
        except (zipfile.BadZipFile, KeyError, UnicodeDecodeError) as e:
            self.stdout.write(self.style.ERROR(f"Failed to extract file: {e}"))
            return

        # Fetch existing cities from database
        self.stdout.write("Fetching existing cities from database...")
        existing_cities = {c.id: c.last_modified for c in City.objects.all()}

        to_create = []
        to_update = []

        # Parse CSV data from memory
        self.stdout.write("Parsing CSV and comparing data...")
        csv_file = io.StringIO(txt_content)
        reader = csv.reader(csv_file, delimiter="\t")

        for line in reader:
            try:
                geonameid = int(line[0])
                name = line[1]
                clean_name = line[2]
                latitude = line[4]
                longitude = line[5]
                country = line[8]
                population = int(line[14])
                last_modified = datetime.strptime(line[18], "%Y-%m-%d").date()

                if len(name) > 60 or len(clean_name) > 60:
                    print(f"Skip: {name}")
                    continue

                if country not in self.ALLOWED_COUNTRIES:
                    continue

                city_obj = City(
                    id=geonameid,
                    name=name,
                    clean_name=clean_name,
                    latitude=latitude,
                    longitude=longitude,
                    location=Point(float(longitude), float(latitude)),
                    country=country,
                    last_modified=last_modified,
                    population=population,
                )

                if geonameid not in existing_cities:
                    to_create.append(city_obj)
                elif last_modified > existing_cities[geonameid] or options["force"]:
                    to_update.append(city_obj)
            except (IndexError, ValueError):
                continue

        # Bulk Create
        if to_create:
            self.stdout.write(f"Creating {len(to_create)} new cities...")
            City.objects.bulk_create(to_create, batch_size=5000)

        # Bulk Update
        if to_update:
            self.stdout.write(f"Updating {len(to_update)} cities...")
            City.objects.bulk_update(
                to_update,
                ["name", "clean_name", "latitude", "longitude", "country", "last_modified", "population"],
                batch_size=5000,
            )

        self.stdout.write(self.style.SUCCESS(f"Done! Created: {len(to_create)}, Updated: {len(to_update)}"))
