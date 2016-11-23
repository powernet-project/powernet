from django.conf.urls import url
from django.contrib import admin
from app.core.views import base

urlpatterns = [
    url(r'^$', base.index, name='Powernet Home'),
    url(r'^admin/', admin.site.urls),
]
