from django.contrib import admin
from models import PowernetUser, Home, Device, FarmDevice

admin.site.register(PowernetUser)
admin.site.register(Home)
admin.site.register(Device)
admin.site.register(FarmDevice)
