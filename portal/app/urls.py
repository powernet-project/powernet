from django.contrib import admin
from app.core.views import base
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', base.index, name='Powernet Home'),
    url(r'^admin/', admin.site.urls),
    url(r'^weather/', base.weather, name='Weather Information'),
    url(r'^api/v1/', include('app.api.v1.urls')),
]
