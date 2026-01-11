from django.db import models
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos import Point
from django.contrib.postgres.indexes import GinIndex


class City(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=60, null=False, blank=False)
    clean_name = models.CharField(max_length=60, null=False, blank=False)
    latitude = models.DecimalField(max_digits=7, decimal_places=5, null=False, blank=False)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, null=False, blank=False)
    location = geomodels.PointField(geography=True, srid=4326, null=True, blank=True)  # srid 4326 = WGS84
    country = models.CharField(max_length=2, null=False, blank=False)
    population = models.BigIntegerField(default=0)
    last_modified = models.DateField(null=False, blank=False)

    class Meta:
        indexes = [
            GinIndex(fields=["clean_name"], opclasses=["gin_trgm_ops"], name="city_clean_name_gin_trgm_idx"),
        ]

    def save(self, *args, **kwargs):
        # If location is set, sync longitude and latitude
        if self.location:
            self.longitude = self.location.x
            self.latitude = self.location.y
        # If location is not set but lon/lat are, create location
        elif self.longitude is not None and self.latitude is not None:
            self.location = Point(float(self.longitude), float(self.latitude))
        super().save(*args, **kwargs)

    def __repr__(self):
        return f"<City {self.name} ({self.country})>"

    def __str__(self):
        return self.name
