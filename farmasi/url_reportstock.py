from django.conf.urls import url
from django.urls import include, path
from . import frm_printstock001
from . import frm_printstock002
urlpatterns = [
    url(r'^frm_printstock001/', include([
        url(r'^$', frm_printstock001.frm_printstock001, name='frm_printstock001'),
        url(r'^getdivisi', frm_printstock001.getdivisi, name='getdivisi'),
        url(r'^getbarang', frm_printstock001.getbarang, name='getbarang'),
        url(r'^KartuStock', frm_printstock001.KartuStock, name='KartuStock'),
    ])),
    url(r'^frm_printstock002/', include([
        url(r'^$', frm_printstock002.frm_printstock002, name='frm_printstock002'),
        url(r'^getdivisi', frm_printstock002.getdivisi, name='getdivisi'),
        url(r'^getbarang', frm_printstock002.getbarang, name='getbarang'),
        url(r'^getjenis_barang', frm_printstock002.getjenis_barang,name='getjenis_barang'),
        url(r'^getgolongan_barang', frm_printstock002.getgolongan_barang,name='getgolongan_barang'),
        url(r'^posisistock', frm_printstock002.posisistock, name='posisistock'),
        url(r'^proses_excel', frm_printstock002.proses_excel, name='proses_excel'),
    ])),

]
