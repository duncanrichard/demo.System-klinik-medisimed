from django.conf.urls import url
from django.urls import include, path
from . import frm_suplier
from . import frm_barang
from . import frm_pabrikan
from . import frm_jenis
from . import frm_produk
from . import frm_sediaan
from . import frm_lokasi

urlpatterns = [
    url(r'^frm_suplier/', include([
        url(r'^$', frm_suplier.frm_suplier, name='frm_suplier'),
        url(r'^exit', frm_suplier.exit, name='exitsuplier'),
        url(r'^load_barang', frm_barang.load_barang, name='load_barang'),
        url(r'^load_suplierDisc', frm_suplier.load_suplierDisc, name='load_suplierDisc'),
        url(r'^load_suplier', frm_suplier.load_suplier, name='load_suplier'),
        url(r'^suplier_simpan', frm_suplier.suplier_simpan, name='suplier_simpan'),
        url(r'^getsuplier', frm_suplier.getsuplier, name='getsuplier'),
        url(r'^getCoa2', frm_suplier.getCoa2, name='getCoa2'),
        url(r'^getcoa', frm_suplier.getcoa, name='getcoa'),
        url(r'^cetak_suplier', frm_suplier.cetak_suplier, name='cetak_suplier'),
        url(r'^getTpay', frm_suplier.getTpay, name='getTpay'),
        url(r'^barangdiscsup_simpan', frm_suplier.barangdiscsup_simpan, name='barangdiscsup_simpan'),
    ])),
    url(r'^frm_pabrikan/', include([
        url(r'^$', frm_pabrikan.frm_pabrikan, name='frm_pabrikan'),
        url(r'^exit', frm_pabrikan.exit, name='exitpabrikan'),
        url(r'^load_pabrikan', frm_pabrikan.load_pabrikan, name='load_pabrikan'),
        url(r'^pabrikan_simpan', frm_pabrikan.pabrikan_simpan, name='suplier_simpan'),
        url(r'^getpabrikan', frm_pabrikan.getpabrikan, name='getpabrikan'),
        url(r'^cetak_pabrikan', frm_pabrikan.cetak_pabrikan, name='cetak_pabrikan'),
    ])),
    url(r'^frm_jenis/', include([
        url(r'^$', frm_jenis.frm_jenis, name='frm_jenis'),
        url(r'^exit', frm_jenis.exit, name='exitjenis_barang'),
        url(r'^load_jenis_barang', frm_jenis.load_jenis_barang,name='load_jenis_barang'),
        url(r'^jenis_barang_simpan', frm_jenis.jenis_barang_simpan,name='jenis_barang_simpan'),
        url(r'^getjenis_barang', frm_jenis.getjenis_barang, name='getjenis_barang'),
        url(r'^cetak_jenis_barang', frm_jenis.cetak_jenis_barang,name='cetak_jenis_barang'),
    ])),
    url(r'^frm_produk/', include([
        url(r'^$', frm_produk.frm_produk, name='frm_produk'),
        url(r'^exit', frm_produk.exit, name='exitfrm_produk'),
        url(r'^load_produk_barang', frm_produk.load_produk_barang,name='load_produk_barang'),
        url(r'^produk_barang_simpan', frm_produk.produk_barang_simpan,name='produk_barang_simpan'),
        url(r'^getproduk_barang', frm_produk.getproduk_barang, name='getproduk_barang'),
        url(r'^cetak_produk_barang', frm_produk.cetak_produk_barang,name='cetak_produk_barang'),
    ])),
    url(r'^frm_sediaan/', include([
        url(r'^$', frm_sediaan.frm_sediaan, name='frm_sediaan'),
        url(r'^exit', frm_sediaan.exit, name='exitsediaan'),
        url(r'^load_sediaan', frm_sediaan.load_sediaan,name='load_sediaan'),
        url(r'^sediaan_simpan', frm_sediaan.sediaan_simpan,name='sediaan_simpan'),
        url(r'^getsediaan', frm_sediaan.getsediaan, name='getsediaan'),
        url(r'^cetak_sediaan', frm_sediaan.cetak_sediaan,name='cetak_sediaan'),
    ])),
    url(r'^frm_lokasi/', include([
        url(r'^$', frm_lokasi.frm_lokasi, name='frm_lokasi'),
        url(r'^exit', frm_lokasi.exit, name='exitlokasi'),
        url(r'^load_lokasi', frm_lokasi.load_lokasi,name='load_lokasi'),
        url(r'^lokasi_simpan', frm_lokasi.lokasi_simpan,name='lokasi_simpan'),
        url(r'^getlokasi', frm_lokasi.getlokasi, name='getlokasi'),
        url(r'^cetak_lokasi', frm_lokasi.cetak_lokasi,name='cetak_lokasi'),
    ])),
     url(r'^frm_barang/', include([
        url(r'^$', frm_barang.frm_barang, name='frm_barang'),
        url(r'^exit', frm_barang.exit, name='exitbarang'),
        url(r'^load_barang_stokmaxmin', frm_barang.load_barang_stokmaxmin, name='load_barang_stokmaxmin'),
        url(r'^load_barangNon', frm_barang.load_barangNon,name='load_barangNon'),
        url(r'^open_barang', frm_barang.open_barang,name='open_barang'),
        url(r'^load_barang', frm_barang.load_barang, name='load_barang'),
        url(r'^getgudang', frm_barang.getgudang,name='getgudang'),
        url(r'^getDatasuplier', frm_suplier.getDatasuplier, name='getDatasuplier'),
        url(r'^getjenis_barang', frm_jenis.getjenis_barang, name='getjenis_barang'),
        url(r'^getproduk_barang', frm_produk.getproduk_barang, name='getproduk_barang'),
        url(r'^getsediaan', frm_sediaan.getsediaan, name='getsediaan'),
        url(r'^getpabrikan', frm_pabrikan.getpabrikan, name='getpabrikan'),
        url(r'^getlokasi', frm_lokasi.getlokasi, name='getlokasi'),
        url(r'^getsuplier', frm_suplier.getsuplier, name='getsuplier'),
        url(r'^barang_simpan', frm_barang.barang_simpan, name='barang_simpan'),
        url(r'^barang_hapus', frm_barang.suplier_hapus, name='barang_hapus'),
        url(r'^cetak_barangwh', frm_barang.cetak_barangwh, name='cetak_barangwh'),
        url(r'^cetak_barang', frm_barang.cetak_barang, name='cetak_barang'),
        url(r'^barangwh_simpan', frm_barang.barangwh_simpan, name='barangwh_simpan'),
    ])),
]