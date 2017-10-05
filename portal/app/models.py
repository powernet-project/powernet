from django.db import models
from enumfields import Enum  # Uses Ethan Furman's "enum34" backport
from enumfields import EnumField
from django.contrib.postgres.fields import JSONField


class UtilityEnergyPrice(models.Model):

    class Meta:
        db_table = 'energy_price'

    name = models.CharField(max_length=200)
    price = models.FloatField()
    timestamp_in_utc_millis = models.CharField(max_length=30)


class DeviceStatus(Enum):
    ON = 'ON'
    OFF = 'OFF'
    UNKNOWN = 'UNKNOWN'


class DeviceType(Enum):
    PV = 'PV'
    STORAGE = 'STORAGE'
    MICROWAVE = 'MICROWAVE'
    STOVE_OVEN = 'STOVE_OVEN'
    DISH_WASHER = 'DISH_WASHER'
    REFRIGERATOR = 'REFRIGERATOR'
    WATER_HEATER = 'WATER_HEATER'
    CLOTHES_DRYER = 'CLOTHES_DRYER'
    CLOTHES_WASHER = 'CLOTHES_WASHER'
    AIR_CONDITIONER = 'AIR_CONDITIONER'


class Device(models.Model):

    class Meta:
        db_table = 'device'

    name = models.CharField(max_length=200)
    type = EnumField(DeviceType)
    status = EnumField(DeviceStatus, default=DeviceStatus.UNKNOWN)


class DeviceState(models.Model):

    class Meta:
        db_table = 'device_state'

    device = models.ForeignKey(Device)
    watt_consumption = models.FloatField()
    measurement_timestamp = models.DateTimeField(null=False, blank=False)
    additional_information = JSONField(null=True, blank=True)
