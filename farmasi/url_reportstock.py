from django.conf.urls import url
from django.urls import include, path
from . import modul_stock
from . import frm_printstock001
from . import frm_printstock002
from . import frm_printstock005
from . import frm_printinfo001
from . import frm_printinfo002
from . import frm_printinfo003
from . import frm_printinfo010


urlpatterns = [
    url(r'^frm_printstock001/', include([
        url(r'^$', frm_printstock001.frm_printstock001, name='frm_printstock001'),
        url(r'^getdivisi', modul_stock.getdivisi, name='getdivisi'),
        url(r'^getbarang', modul_stock.getbarang, name='getbarang'),
        url(r'^KartuStock', frm_printstock001.KartuStock, name='KartuStock'),
    ])),
    url(r'^frm_printstock002/', include([
        url(r'^$', frm_printstock002.frm_printstock002, name='frm_printstock002'),
        url(r'^getdivisi', modul_stock.getdivisi, name='getdivisi'),
        url(r'^getbarang', modul_stock.getbarang, name='getbarang'),
        url(r'^getjenis_barang', modul_stock.getjenis_barang,name='getjenis_barang'),
        url(r'^getgolongan_barang', modul_stock.getgolongan_barang,name='getgolongan_barang'),
        url(r'^posisistock', frm_printstock002.posisistock, name='posisistock'),
        url(r'^proses_excel', frm_printstock002.proses_excel, name='proses_excel'),
    ])),
    url(r'^frm_printstock005/', include([
        url(r'^$', frm_printstock005.frm_printstock005, name='frm_printstock005'),
        url(r'^getdivisi', modul_stock.getdivisi, name='getdivisi'),
        url(r'^getbarang', modul_stock.getbarang, name='getbarang'),
        url(r'^getjenis_barang', modul_stock.getjenis_barang,name='getjenis_barang'),
        url(r'^persediaanstock', frm_printstock005.persediaanstock, name='persediaanstock'),
        url(r'^proses_excel', frm_printstock005.proses_excel, name='proses_excel'),
    ])),
    url(r'^frm_printinfo001/', include([
        url(r'^$', frm_printinfo001.frm_printinfo001, name='frm_printinfo001'),
        url(r'^getdivisi', modul_stock.getdivisi, name='getdivisi'),
        url(r'^getpabrikan', modul_stock.getpabrikan, name='getpabrikanm'),
        url(r'^proses_lap_limit', frm_printinfo001.proses_lap_limit, name='proses_lap_limit'),
    ])),
    url(r'^frm_printinfo002/', include([
        url(r'^$', frm_printinfo002.frm_printinfo002, name='frm_printinfo002'),
        url(r'^getdivisi', modul_stock.getdivisi, name='getdivisi'),
        url(r'^getbarang', modul_stock.getbarang, name='getbarang'),
        url(r'^getdokter', frm_printinfo002.getdokter, name='getdokter'),
        url(r'^cetak_lap_summary', frm_printinfo002.cetak_lap_summary, name='cetak_lap_summary'),
        url(r'^cetak_lap_rekap', frm_printinfo002.cetak_lap_rekap, name='cetak_lap_rekap'),
        url(r'^cetak_lap_detail', frm_printinfo002.cetak_lap_detail, name='cetak_lap_detail'),
    ])),
    url(r'^frm_printinfo003/', include([
        url(r'^$', frm_printinfo003.frm_printinfo003, name='frm_printinfo003'),
        url(r'^proses_lap_expired', frm_printinfo003.proses_lap_expired, name='proses_lap_expired'),
    ])),
    url(r'^frm_printinfo010/', include([
        url(r'^$', frm_printinfo010.frm_printinfo010, name='frm_printinfo010'),
        url(r'^getdivisi', modul_stock.getdivisi, name='getdivisi'),
        url(r'^proses_lap_umur', frm_printinfo010.proses_lap_umur, name='proses_lap_umur'),
    ])),

]
