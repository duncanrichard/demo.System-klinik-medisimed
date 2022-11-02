from django.shortcuts import render,redirect
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from urllib.parse import unquote
from inspect import getmembers
from pprint import pprint
from IMMODERMA.globals import Globals
from IMMODERMA.environment import env
from datetime import datetime
from django.conf.urls import url, include


def getDataBarangKeluar(request):
	ID_CABANG = request.session['kdCabang']
	nama = request.GET['nama']+'%'
	gudang = request.GET['gudang']
	if nama == 'nullnone0':
		result = []
	else:
		q = "select a.BARANGC, a.NAME_BRG, a.SATSTAND, a.TTYPEC, "
		q += "a.HPOKOK , HJUAL,f.STATUSPRODUK, "
		q += "CAST(((isnull(b.FSBSALDO_AWAL,0)+isnull(b.FSBPEMBELIAN,0)+isnull(b.FSBRPENJUALAN,0)+isnull(b.FSBLAIN_MASUK,0)) - "
		q += "(isnull(b.FSBPENJUALAN,0)+isnull(b.FSBRPEMBELIAN,0)+isnull(b.FSBLAIN_KELUAR,0))) AS INT) AS STOK "
		q += "from BARANG a left join SALDOBARANG b on a.BARANGC = b.FSBBRG_ID  and b.FSBWH_ID=%s "
		q += "left join WAREHOUSE c on b.FSBWH_ID=c.WH_ID and c.BRANCH=%s "
		q += "inner join PRODUKOBAT f ON  A.TTYPEC=f.PRD_ID  "
		q += "where a.NAME_BRG like %s and a.AKTIF<>1  order by NAME_BRG "
		result = Globals().getDataQuery(q, [gudang,ID_CABANG,nama])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cekStokBarangFarmasi(request):
	ID_CABANG = request.session['kdCabang']
	kode = request.GET['kode']
	gudang = request.GET['kode_gudang']
	q = "select a.BARANGC, a.NAME_BRG, a.SATSTAND, a.TTYPEC, "
	q += "CAST(((isnull(b.FSBSALDO_AWAL,0)+isnull(b.FSBRPENJUALAN,0)+isnull(b.FSBPEMBELIAN,0)+isnull(b.FSBLAIN_MASUK,0)+isnull(b.FSBRKANVAS,0)) - "
	q += "(isnull(b.FSBPENJUALAN,0)+isnull(b.FSBRPEMBELIAN,0)+isnull(b.FSBLAIN_KELUAR,0)+isnull(b.FSBKANVAS,0))) AS INT) AS STOK "
	q += "from BARANG a left join SALDOBARANG b on "
	q += "a.BARANGC = b.FSBBRG_ID left join WAREHOUSE c on "
	q += "b.FSBWH_ID=c.wh_id and c.BRANCH=%s "
	q += "where a.BARANGC = %s and b.FSBWH_ID=%s "
	result = Globals().getDataQuery(q, [ID_CABANG,kode,gudang])
	
	if(len(result) == 0):
		data = {
			'status':'gagal',
			'pesan':'Data Barang Tidak Tersedia',
			'item': None,
		}
	else:
		data = {
			'status':'ok',
			'pesan':'Data Barang Tersedia',
			'item': result[0],
		}

	json_data = json.dumps(data, cls=DjangoJSONEncoder)
	
	return HttpResponse(json_data, content_type="application/json")

def getHistoryBarang(request):
	ID_CABANG = request.session['kdCabang']
	kode_barang = request.GET['kode_barang']
	gudang = request.GET['gudang']
	tanggal = datetime.now().strftime('%Y-%m-%d')
	q = "select c.NAME_WH,a.BARANGC, a.NAME_BRG, a.SATSTAND, "
	q += "CAST(((isnull(b.FSBSALDO_AWAL,0)+isnull(b.FSBRPENJUALAN,0)+isnull(b.FSBPEMBELIAN,0)+isnull(b.FSBLAIN_MASUK,0)+isnull(b.FSBRKANVAS,0)) - "
	q += "(isnull(b.FSBPENJUALAN,0)+isnull(b.FSBRPEMBELIAN,0)+isnull(b.FSBLAIN_KELUAR,0)+isnull(b.FSBKANVAS,0))) AS INT) AS STOK "
	q += "from BARANG a left join SALDOBARANG b on "
	q += "a.BARANGC = b.FSBBRG_ID  left join WAREHOUSE c on "
	# q += "a.BARANGC = b.FSBBRG_ID and b.FSBWH_ID =  %s left join WAREHOUSE c on "
	q += "b.FSBWH_ID=c.WH_ID and c.BRANCH=%s where a.BARANGC =  %s   "
	# result = Globals().getDataQuery(q,[gudang,kode_barang])
	result = Globals().getDataQuery(q,[ID_CABANG,kode_barang])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getHistoryBeliBarang(request):
    ID_CABANG = request.session['kdCabang']
    kode_barang = request.GET['kode_barang']
    q = "select a.FHFBBUKTI_ID as NO_FAKTUR, CONVERT(varchar, a.FHFBDATE, 23) as TANGGAL_FAKTUR, "
    q += "b.FDFBBRGN as NAMA_BARANG, b.FDFBSATUAN as SATUAN, b.FDFBQTYT as QTY, b.FDFBHPOKOK as HARGA_POKOK, "
    q += "b.FDFBDISC1 as DISC1, b.FDFBDISC2 as DISC2, b.FDFBDISC3 as DISC_RUPIAH, b.FDFBKONVERSI as KONVERSI, "
    q += "c.NAME_WH as GUDANG, d.NAME_SUPPL as SUPPLIER, "
    q += "IIF(CONVERT(varchar, b.FDFBTGL_EXPIRED, 23) = '1900-01-01', '', CONVERT(varchar, b.FDFBTGL_EXPIRED, 23)) as TANGGAL_EXPIRED "
    q += "from FBELI a inner join FBELID b on a.FHFBBUKTI_ID = b.FDFBBUKTI_ID "
    q += "inner join WAREHOUSE c on a.FHFBWH_ID =c.WH_ID "
    q += "inner join SUPPLIER d on a.FHFBSUPPL_ID = d.SUPPLIERC "
    q += "where b.FDFBBRG_ID = %s and a.FHFBBRANCH= %s order by a.FHFBDATE desc"
    result = Globals().getDataQuery(q, [kode_barang,ID_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

