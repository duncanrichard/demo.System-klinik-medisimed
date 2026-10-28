from django.urls import include, re_path as url

from . import health


urlpatterns = [
    url(r'^health/$', health.health, name='health'),
    url(r'^health/database/$', health.database_health, name='database_health'),
    url(r'^',include('auth.urls')),
    url(r'^',include('dashboard.urls')),
    url(r'^',include('farmasi.urls')),
    url(r'^',include('setupdata.urls')),
    url(r"^", include("emr.urls")),
    url(r"^", include("emrnew.urls")),
    url(r"^", include("pusdokkes.urls")),
]
