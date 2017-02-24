from django.contrib import admin

# Register your models here.
from .models import ResInterval60, LocalWeather

admin.site.register(ResInterval60)
admin.site.register(LocalWeather)