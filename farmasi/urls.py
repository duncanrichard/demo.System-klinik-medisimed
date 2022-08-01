from django.conf.urls import url
from django.urls import include, path
from . import frm_suplier

urlpatterns = [
url(r'^frm_suplier/', include([
        url(r'^$', frm_suplier.frm_suplier, name='frm_suplier'),
        url(r'^exit', frm_suplier.exit, name='exitsuplier'),
        # url(r'^load_barang', frm_barang.load_barang, name='load_barang'),
        url(r'^load_suplierDisc', frm_suplier.load_suplierDisc, name='load_suplierDisc'),
        url(r'^load_suplier', frm_suplier.load_suplier, name='load_suplier'),
        url(r'^suplier_simpan', frm_suplier.suplier_simpan, name='suplier_simpan'),
        url(r'^suplier_hapus', frm_suplier.suplier_hapus, name='suplier_hapus'),
        url(r'^getsuplier', frm_suplier.getsuplier, name='getsuplier'),
        url(r'^getCoa2', frm_suplier.getCoa2, name='getCoa2'),
        url(r'^getcoa', frm_suplier.getcoa, name='getcoa'),
        url(r'^cetak_suplier', frm_suplier.cetak_suplier, name='cetak_suplier'),
        url(r'^getTpay', frm_suplier.getTpay, name='getTpay'),
        url(r'^barangdiscsup_simpan', frm_suplier.barangdiscsup_simpan, name='barangdiscsup_simpan'),
    ])),
]