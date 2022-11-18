from django.conf.urls import url
from django.urls import include, path
from . import master_dokter
from . import master_perawat
urlpatterns = [
    url(r'^master_dokter/', include ([
        url(r'^$',master_dokter.master_dokter, name='master_dokter'),
        url(r'^open_dokter', master_dokter.open_dokter),
        url(r'^aud_dokter', master_dokter.aud_dokter),
    ])),
    url(r'^master_perawat/', include ([
        url(r'^$',master_perawat.master_perawat, name='master_perawat'),
        url(r'^open_perawat', master_perawat.open_perawat),
        url(r'^aud_perawat', master_perawat.aud_perawat),
    ])),

]

