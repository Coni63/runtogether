from django.db import models
from django.contrib.postgres.indexes import GinIndex


class City(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=60, null=False, blank=False)
    clean_name = models.CharField(max_length=60, null=False, blank=False)
    latitude = models.DecimalField(max_digits=7, decimal_places=5, null=False, blank=False)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, null=False, blank=False)
    country = models.CharField(max_length=2, null=False, blank=False)
    last_modified = models.DateField(null=False, blank=False)

    class Meta:
        indexes = [
            GinIndex(fields=["clean_name"], opclasses=["gin_trgm_ops"], name="city_clean_name_gin_trgm_idx"),
        ]
