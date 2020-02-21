from django.contrib import admin
from models import PowernetUser, Home, Device, FarmDevice, EcobeeDevice


@admin.register(FarmDevice)
class FarmDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_uid', 'type', 'home')


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'type', 'owner')


@admin.register(PowernetUser)
class PowernetUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'first_name', 'last_name', 'email')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'home', 'status', 'value', 'cosphi')

@admin.register(EcobeeDevice)
class EcobeeDeviceAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'access_token', 'refresh_token')
