from django.conf.urls import url
from django.urls import include, path
from . import master_dokter
from . import master_perawat
from . import master_userpriv
from . import master_voucher
<<<<<<< Updated upstream
from . import master_changeuser
from . import master_cabang
from . import master_poliklinik
from pusdokkes import views_satu_sehat
=======
>>>>>>> Stashed changes

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
    url(r'^master_userpriv/', include ([
        url(r'^$',master_userpriv.master_userpriv, name='master_userpriv'),
        url(r'^open_userpriv', master_userpriv.open_userpriv),
        url(r'^aud_userpriv', master_userpriv.aud_userpriv),
<<<<<<< Updated upstream
        url(r'^getprivelige', master_userpriv.getprivelige),
    ])),
    url(r'^master_changeuser/', include ([
        url(r'^$',master_changeuser.master_changeuser, name='master_changeuser'),
        url(r'^changepassword', master_changeuser.changepassword),
    ])),
    url(
        r"^master_cabang/",
        include(
            [
                url(r"^$", master_cabang.master_cabang, name="master_cabang"),
                url(r"^open_cabang", master_cabang.open_cabang),
                url(r"^aud_cabang", master_cabang.aud_cabang),
                url(r"^getProvinsi", master_cabang.getProvinsi),
                url(r"^getKabupaten", master_cabang.getKabupaten),
                url(r"^getKecamatan", master_cabang.getKecamatan),
                url(r"^getKelurahan", master_cabang.getKelurahan),
                url(r"^saveOrganization", views_satu_sehat.saveOrganization_SrvIndo),
            ]
        ),
    ),
    url(
        r"^master_poliklinik/",
        include(
            [
                url(
                    r"^$", master_poliklinik.master_poliklinik, name="master_poliklinik"
                ),
                url(r"^load_poliklinik", master_poliklinik.load_poliklinik),
                url(r"^getpoliklinik", master_poliklinik.getpoliklinik),
                url(r"^getDatapoliklinik", master_poliklinik.getDatapoliklinik),
            ]
        ),
    ),
=======
    ])),
>>>>>>> Stashed changes
    url(r'^master_voucher/', include ([
        url(r'^$',master_voucher.master_voucher, name='master_voucher'),
        url(r'^buka_voucher', master_voucher.buka_voucher),
        url(r'^open_voucher', master_voucher.open_voucher),
        url(r'^aud_voucher', master_voucher.aud_voucher),
    ])),

]

