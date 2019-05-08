from django.contrib import admin
from django.contrib.auth import views as auth_views
from app.core.views import base, auth
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', base.index, name='Powernet Home'),
    url(r'^admin/', admin.site.urls),

    # REST API
    url(r'^api/v1/', include('app.api.v1.urls')),

    # Authentication / Authorization / Onboarding
    url(r'^signup/', auth.signup, name='Powernet Signup'),
    url(r'^login/', auth_views.login, {'template_name': 'auth/login.html'}, name='Powernet Login'),
    url(r'^logout/', auth.logout, name='Powernet Logout'),

    # View for demo/lab account only
    url(r'^weather/', base.weather, name='Weather Information'),
    url(r'^pv/', base.pv, name='Enphase PV status'),
    url(r'^charts/', base.charts, name='Algorithm Charts/Plots'),
    url(r'^charts_no_control/', base.charts_no_control, name='No Control Algo Charts'),
    url(r'^electricity/', base.electricity, name='ComEd Energy Price Information'),
    url(r'^home/one/', base.home_one, name='Home One'),
    url(r'^home/two/', base.home_two, name='Home Two'),
    url(r'^cost-min/', base.opf, name='OPF'),

    # Powernet Application Views
    url(r'^settings/', base.settings, name='Home Settings'),
    url(r'^devices/', base.devices, name='Home Devices'),
    url(r'^consumption/', base.consumption, name='Home Consumption'),
]

handler404 = 'app.core.views.base.handler404'