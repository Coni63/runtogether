from django.db import models
from django.contrib.gis.db import models as geomodels
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.geos import Point

RACE_TYPE = (
    ("trail", "Trail"),
    ("road", "Road"),
)

INSCRIPTION_TYPE = (
    ("not_open", "Inscriptions non ouvertes"),
    ("open", "Inscriptions en cours"),
    ("closed", "Inscriptions terminées"),
    ("terminated", "Course terminée"),
)


class Race(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False, help_text="Name of the race")
    date_course = models.DateField(null=False, blank=False, help_text="Date of the race")
    date_validated = models.BooleanField(default=False, help_text="Indicates if the race date is confirmed")
    inscription_status = models.CharField(max_length=10, null=True, blank=True, choices=INSCRIPTION_TYPE)
    date_inscriptions_open = models.DateField(null=True, blank=True, help_text="Date when inscriptions open")
    city = models.ForeignKey(
        "city.City",
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        help_text="City where the race takes place",
        related_name="races",
    )
    longitude = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
    latitude = models.DecimalField(max_digits=7, decimal_places=5, null=True, blank=True)
    location = geomodels.PointField(geography=True, srid=4326, null=True, blank=True)  # srid 4326 = WGS84
    race_type = models.CharField(max_length=5, null=True, blank=True, choices=RACE_TYPE)
    private = models.BooleanField(default=False, help_text="Indicates if the race is limited to a specific club")
    club_owner = models.ForeignKey(
        "club.Club", null=True, blank=True, on_delete=models.SET_NULL, related_name="races", help_text="Club that owns the race"
    )
    url_race = models.URLField(max_length=500, null=True, blank=True, help_text="URL of the race")
    url_inscriptions = models.URLField(max_length=500, null=True, blank=True, help_text="URL of the inscriptions")
    distance = ArrayField(
        base_field=models.FloatField(),
        size=None,  # or a fixed size like 128
        default=list,
        blank=True,
        help_text="List of distances in kilometers",
    )

    def save(self, *args, **kwargs):
        # If location is set, sync longitude and latitude
        if self.location:
            self.longitude = self.location.x
            self.latitude = self.location.y
        # If location is not set but lon/lat are, create location
        elif self.longitude is not None and self.latitude is not None:
            self.location = Point(float(self.longitude), float(self.latitude))
        super().save(*args, **kwargs)
