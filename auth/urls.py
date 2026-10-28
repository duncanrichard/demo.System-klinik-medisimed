from django.urls import include, re_path as url
from . import views

urlpatterns = [
    url(r'^login', views.login, name='login'),
    url(r'^getCabang', views.getCabang, name='getCabang'),
    url(r'^logout', views.logout, name='logout'),
]