from django.conf.urls import url
from django.urls import include, path
from . import master_dokter
from . import master_perawat
from . import master_userpriv
from . import master_voucher
from . import master_changeuser

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
    ])),
    url(r'^master_changeuser/', include ([
        url(r'^$',master_changeuser.master_changeuser, name='master_changeuser'),
        url(r'^changepassword', master_changeuser.changepassword),
    ])),
    url(r'^master_voucher/', include ([
        url(r'^$',master_voucher.master_voucher, name='master_voucher'),
        url(r'^buka_voucher', master_voucher.buka_voucher),
        url(r'^open_voucher', master_voucher.open_voucher),
        url(r'^aud_voucher', master_voucher.aud_voucher),
    ])),

]

