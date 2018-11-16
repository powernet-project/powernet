from django.db import models
from enumfields import EnumField
from django.utils import timezone
from enumfields import Enum  # Uses Ethan Furman's "enum34" backport
from django.contrib.auth.models import User
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
    CHARGE = 'CHARGE'
    UNKNOWN = 'UNKNOWN'
    DISCHARGE = 'DISCHARGE'


class DeviceType(Enum):
    PV = 'PV'
    SDF = 'SDF'
    STORAGE = 'STORAGE'
    MICROWAVE = 'MICROWAVE'
    STOVE_OVEN = 'STOVE_OVEN'
    DISH_WASHER = 'DISH_WASHER'
    REFRIGERATOR = 'REFRIGERATOR'
    WATER_HEATER = 'WATER_HEATER'
    CLOTHES_DRYER = 'CLOTHES_DRYER'
    CLOTHES_WASHER = 'CLOTHES_WASHER'
    AIR_CONDITIONER = 'AIR_CONDITIONER'
    STOVE_OVEN_EXHAUST = 'STOVE_OVEN_EXHAUST'


class ApplianceJsonData(models.Model):

    class Meta:
        db_table = 'appliance_data'

    devices_json = JSONField(null=True, blank=True)


class HueStatesType(Enum):
    ON = 'ON'
    OFF = 'OFF'
    BASE = 'BASE'
    UNKNOWN = 'UNKNOWN'
    VIOLATION = 'VIOLATION'
    COORDINATED = 'COORDINATED'


class HueStates(models.Model):

    class Meta:
        db_table = 'hue_states'

    state = EnumField(HueStatesType, default=HueStatesType.UNKNOWN, max_length=40)


class PowernetUser(models.Model):

    def __unicode__(self):
        return unicode(self.user.username)

    class Meta:
        db_table = 'powernet_user'

    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_access_dt_stamp = models.DateTimeField(default=timezone.now)


class HomeType(Enum):
    REAL = 'REAL'
    UNKNOWN = 'UNKNOWN'
    SIMULATED = 'SIMULATED'


class Home(models.Model):

    class Meta:
        db_table = 'home'

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=1000)
    type = EnumField(HomeType, default=HomeType.UNKNOWN, max_length=20)
    owner = models.ForeignKey(PowernetUser)


class HomeData(models.Model):

    class Meta:
        db_table = 'home_data'

    home = models.ForeignKey(Home)
    reactive_power = models.FloatField(default=0)
    real_power = models.FloatField(default=0)
    state_of_charge = models.FloatField(default=0)
    dt_stamp = models.DateTimeField(default=timezone.now)


class Device(models.Model):

    class Meta:
        db_table = 'device'

    home = models.ForeignKey(Home)
    name = models.CharField(max_length=200)
    type = EnumField(DeviceType, max_length=40)
    status = EnumField(DeviceStatus, default=DeviceStatus.UNKNOWN, max_length=40)
    value = models.IntegerField(default=0)
    cosphi = models.FloatField(default=1.0)


class DeviceState(models.Model):

    class Meta:
        db_table = 'device_state'

    device = models.ForeignKey(Device)
    watt_consumption = models.FloatField()
    measurement_timestamp = models.DateTimeField(null=False, blank=False)
    additional_information = JSONField(null=True, blank=True)


class MatlabFiles(models.Model):

    class Meta:
        db_table = 'matlab_files'

    filename = models.CharField(max_length=200)
    content = JSONField(null=True, blank=True)
