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
    SONNEN = 'SONNEN'
    EGAUGE = 'EGAUGE'
    PICO_BLENDER = 'PICO_BLENDER'
    LORA = 'LORA'


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


def disable_callable(cls):
    cls.do_not_call_in_templates = True
    return cls


@disable_callable
class PowernetUserType(Enum):
    LAB = 'LAB'  # special user type that has more lab like functionality for more  R&D type work
    HOME = 'HOME'
    FARM = 'FARM'


class PowernetUser(models.Model):

    def __unicode__(self):
        return unicode(self.user.username)

    class Meta:
        db_table = 'powernet_user'

    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE,)
    type = EnumField(PowernetUserType, default=PowernetUserType.HOME, max_length=10)
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

    def __unicode__(self):
        return "Home - {0}".format(self.name)

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=1000)
    type = EnumField(HomeType, default=HomeType.UNKNOWN, max_length=20)
    owner = models.ForeignKey(PowernetUser, on_delete=models.deletion.CASCADE)


class HomeData(models.Model):

    class Meta:
        db_table = 'home_data'

    home = models.ForeignKey(Home, on_delete=models.deletion.CASCADE)
    reactive_power = models.FloatField(default=0)
    real_power = models.FloatField(default=0)
    state_of_charge = models.FloatField(default=0)
    dt_stamp = models.DateTimeField(default=timezone.now)


class Device(models.Model):

    class Meta:
        db_table = 'device'

    home = models.ForeignKey(Home, on_delete=models.deletion.CASCADE)
    name = models.CharField(max_length=200)
    type = EnumField(DeviceType, max_length=40)
    status = EnumField(DeviceStatus, default=DeviceStatus.UNKNOWN, max_length=40)
    value = models.IntegerField(default=0)
    cosphi = models.FloatField(default=1.0)


class DeviceState(models.Model):

    class Meta:
        db_table = 'device_state'

    device = models.ForeignKey(Device, on_delete=models.deletion.CASCADE)
    watt_consumption = models.FloatField()
    measurement_timestamp = models.DateTimeField(null=False, blank=False)
    additional_information = JSONField(null=True, blank=True)


class ApplianceJsonData(models.Model):

    class Meta:
        db_table = 'appliance_data'

    home = models.ForeignKey(Home, on_delete=models.deletion.CASCADE)
    devices_json = JSONField(null=True, blank=True)


class FarmDevice(models.Model):

    class Meta:
        db_table = 'farm_device'
        unique_together = ['home', 'device_uid']

    home = models.ForeignKey(Home, on_delete=models.deletion.CASCADE)
    device_uid = models.CharField(max_length=100, blank=False, null=False)
    type = EnumField(DeviceType, max_length=40)
    timestamp = models.DateTimeField(default=timezone.now)


class FarmData(models.Model):

    class Meta:
        db_table = 'farm_device_data'

    farm_device = models.ForeignKey(FarmDevice, null=True, on_delete=models.deletion.CASCADE)
    device_data = JSONField(null=True, blank=True, default=None)
    timestamp = models.DateTimeField(default=timezone.now)


class FarmMaxDemand(models.Model):

    class Meta:
        db_table = 'farm_max_power_demand'

    home = models.ForeignKey(Home, on_delete=models.deletion.CASCADE)
    max_power = models.FloatField(default=0)
    month_pst = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)


class EcobeeDevice(models.Model):

    class Meta:
        db_table = 'ecobee'

    api_key = models.CharField(max_length=100, blank=False, null=False)
    access_token = models.CharField(max_length=100, blank=False, null=False)
    refresh_token = models.CharField(max_length=100, blank=False, null=False)
