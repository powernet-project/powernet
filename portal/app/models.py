from django.db import models


class UtilityEnergyPrice(models.Model):

    class Meta:
        db_table = 'energy_price'

    name = models.CharField(max_length=200)
    price = models.FloatField()
    timestamp_in_utc_millis = models.CharField(max_length=30)



