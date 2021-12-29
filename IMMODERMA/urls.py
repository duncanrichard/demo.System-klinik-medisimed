from django.conf.urls import include,url
from django.contrib import admin
from .globals import Globals
urlpatterns = [
    url(r'^',include('auth.urls')),
    url(r'^',include('dashboard.urls')),
]