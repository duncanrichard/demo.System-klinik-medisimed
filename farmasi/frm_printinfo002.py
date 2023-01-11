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


def frm_printinfo002(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_printinfo001")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/printsales010/printsales010.html', {
			'navbars': navbars,
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			'user_id': user_privelege,
			'title': 'Laporan stock Limit',
		})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

	

def getdokter(request):
	kode_dokter = '%'+request.GET['search_kode_dokter']+'%'
	nama_dokter = '%'+request.GET['search_nama_dokter']+'%'
	q = "SELECT A.FMDDOKTER_ID,A.FMDDOKTERN FROM DOKTER A "
	q += "WHERE (FMDDOKTER_ID LIKE %s) AND (FMDDOKTERN LIKE %s) ORDER BY  FMDDOKTERN "
	result = Globals().getDataQuery(q, [kode_dokter,nama_dokter])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap(request):
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	kodebarang_dari = request.GET['kodebarang_dari']
	kodebarang_sampai = request.GET['kodebarang_sampai']
	kodedokter_dari = request.GET['kodedokter_dari']
	kodedokter_sampai = request.GET['kodedokter_sampai']
	tanggal_dr = request.GET['tanggal_dr']
	tanggal_sd = request.GET['tanggal_sd']

	q="select * from( "
	q += "SELECT A.FHFJWHN AS GUDANG,FHFJDOKTERN AS DOKTER,b.FDFJBRGN as NAMA_BARANG,  sum(B.FDFJQTY) AS QTY,FDFJSATUAN AS SATUAN "
	q += "FROM  FJINKOTA A INNER JOIN FJINKOTAD B ON A.FHFJBUKTI_ID=B.FDFJBUKTI_ID "
	q += "WHERE  A.FHFJDATE>=%s AND   A.FHFJDATE<=%s "
	q += "AND B.FDFJBRG_ID>=%s AND  FDFJBRG_ID<=%s "
	q += "AND A.FHFJDOKTER_ID>=%s AND  A.FHFJDOKTER_ID<=%s "
	q += "AND A.FHFJWH_ID>=%s AND  A.FHFJWH_ID<=%s "
	q += "group by A.FHFJWHN,FHFJDOKTERN,b.FDFJBRGN ,FDFJSATUAN  "
	q += "UNION  SELECT A.FHRJWHN AS GUDANG,FHRJDOKTERN AS DOKTER,B.FDRJBRGN AS NAMA_BARANG,  sum(B.FDRJQTYT*-1) AS QTY,FDRJSATUAN AS SATUAN "
	q += "FROM  RETURJIN A INNER JOIN RETURJIND B  ON A.FHRJBUKTI_ID=B.FDRJBUKTI_ID "
	q += "WHERE  A.FHRJDATE>=%s AND   A.FHRJDATE<=%s "
	q += "AND  FDRJBRG_ID>=%s  AND  FDRJBRG_ID<=%s  "
	q += "AND A.FHRJDOKTER_ID>=%s AND  A.FHRJDOKTER_ID<=%s "
	q += "AND A.FHRJWH_ID>=%s AND  A.FHRJWH_ID<=%s "
	q += "group by A.FHRJWHN,FHRJDOKTERN,FDRJBRGN ,FDRJSATUAN ) tmp  "
	q += "ORDER BY GUDANG,NAMA_BARANG,DOKTER ASC "
	
	result = Globals().getDataQuery(q, [tanggal_dr,tanggal_sd,kodebarang_dari,kodebarang_sampai,kodedokter_dari,kodedokter_sampai,cetak_dari,cetak_sampai,tanggal_dr,tanggal_sd,kodebarang_dari,kodebarang_sampai,kodedokter_dari,kodedokter_sampai,cetak_dari,cetak_sampai])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")
def cetak_lap_detail(request):
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	kodebarang_dari = request.GET['kodebarang_dari']
	kodebarang_sampai = request.GET['kodebarang_sampai']
	kodedokter_dari = request.GET['kodedokter_dari']
	kodedokter_sampai = request.GET['kodedokter_sampai']
	tanggal_dr = request.GET['tanggal_dr']
	tanggal_sd = request.GET['tanggal_sd']

	q="select * from( "
	q += "SELECT A.FHFJWHN AS GUDANG,b.FDFJBRGN as NAMA_BARANG,FHFJDATE AS TANGGAL,FHFJBUKTI_ID AS BUKTI,FHFJCUSTN AS PASIEN,FHFJPOLYN AS POLY,FHFJDOKTERN AS DOKTER,  B.FDFJQTY AS QTY,FDFJSATUAN AS SATUAN "
	q += "FROM  FJINKOTA A INNER JOIN FJINKOTAD B ON A.FHFJBUKTI_ID=B.FDFJBUKTI_ID "
	q += "WHERE  A.FHFJDATE>=%s AND   A.FHFJDATE<=%s "
	q += "AND B.FDFJBRG_ID>=%s AND  FDFJBRG_ID<=%s "
	q += "AND A.FHFJDOKTER_ID>=%s AND  A.FHFJDOKTER_ID<=%s "
	q += "AND A.FHFJWH_ID>=%s AND  A.FHFJWH_ID<=%s "
	q += "UNION  SELECT A.FHRJWHN AS GUDANG,B.FDRJBRGN AS NAMA_BARANG,FHRJDATE AS TANGGAL,FHRJBUKTI_ID AS BUKTI,FHRJJENISCUSTN AS PASIEN,FHRJPOLYN AS POLY,FHRJDOKTERN AS DOKTER,  B.FDRJQTYT*-1 AS QTY,FDRJSATUAN AS SATUAN "
	q += "FROM  RETURJIN A INNER JOIN RETURJIND B  ON A.FHRJBUKTI_ID=B.FDRJBUKTI_ID "
	q += "WHERE  A.FHRJDATE>=%s AND   A.FHRJDATE<=%s "
	q += "AND  FDRJBRG_ID>=%s  AND  FDRJBRG_ID<=%s  "
	q += "AND A.FHRJDOKTER_ID>=%s AND  A.FHRJDOKTER_ID<=%s "
	q += "AND A.FHRJWH_ID>=%s AND  A.FHRJWH_ID<=%s  ) tmp "
	q += "ORDER BY GUDANG,NAMA_BARANG,DOKTER ASC "

	result = Globals().getDataQuery(q, [tanggal_dr,tanggal_sd,kodebarang_dari,kodebarang_sampai,kodedokter_dari,kodedokter_sampai,cetak_dari,cetak_sampai,tanggal_dr,tanggal_sd,kodebarang_dari,kodebarang_sampai,kodedokter_dari,kodedokter_sampai,cetak_dari,cetak_sampai])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_lap_summary(request):
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	kodebarang_dari = request.GET['kodebarang_dari']
	kodebarang_sampai = request.GET['kodebarang_sampai']
	kodedokter_dari = request.GET['kodedokter_dari']
	kodedokter_sampai = request.GET['kodedokter_sampai']
	tanggal_dr = request.GET['tanggal_dr']
	tanggal_sd = request.GET['tanggal_sd']

	q="select * from( "
	q += "SELECT A.FHFJWHN AS GUDANG,D.NAME_PRD,b.FDFJBRGN as NAMA_BARANG,  sum(B.FDFJQTY) AS QTY,FDFJSATUAN AS SATUAN "
	q += "FROM  FJINKOTA A INNER JOIN FJINKOTAD B ON A.FHFJBUKTI_ID=B.FDFJBUKTI_ID "
	q += "INNER JOIN BARANG C ON B.FDFJBRG_ID=C.BARANGC "
	q += "LEFT JOIN PRODUKOBAT D ON C.TTYPEC=D.PRD_ID "
	q += "WHERE  A.FHFJDATE>=%s AND   A.FHFJDATE<=%s "
	q += "AND B.FDFJBRG_ID>=%s AND  FDFJBRG_ID<=%s "
	q += "AND A.FHFJDOKTER_ID>=%s AND  A.FHFJDOKTER_ID<=%s "
	q += "AND A.FHFJWH_ID>=%s AND  A.FHFJWH_ID<=%s "
	q += "group by A.FHFJWHN,D.NAME_PRD,b.FDFJBRGN ,FDFJSATUAN  "
	q += "UNION  SELECT A.FHRJWHN AS GUDANG,D.NAME_PRD,B.FDRJBRGN AS NAMA_BARANG,  sum(B.FDRJQTYT*-1) AS QTY,FDRJSATUAN AS SATUAN "
	q += "FROM  RETURJIN A INNER JOIN RETURJIND B  ON A.FHRJBUKTI_ID=B.FDRJBUKTI_ID "
	q += "INNER JOIN BARANG C ON B.FDRJBRG_ID=C.BARANGC "
	q += "LEFT JOIN PRODUKOBAT D ON C.TTYPEC=D.PRD_ID "
	q += "WHERE  A.FHRJDATE>=%s AND   A.FHRJDATE<=%s "
	q += "AND  FDRJBRG_ID>=%s  AND  FDRJBRG_ID<=%s  "
	q += "AND A.FHRJDOKTER_ID>=%s AND  A.FHRJDOKTER_ID<=%s "
	q += "AND A.FHRJWH_ID>=%s AND  A.FHRJWH_ID<=%s "
	q += "group by A.FHRJWHN,D.NAME_PRD,FDRJBRGN ,FDRJSATUAN ) tmp  "
	q += "ORDER BY GUDANG,NAME_PRD,NAMA_BARANG ASC "
	result = Globals().getDataQuery(q, [tanggal_dr,tanggal_sd,kodebarang_dari,kodebarang_sampai,kodedokter_dari,kodedokter_sampai,cetak_dari,cetak_sampai,tanggal_dr,tanggal_sd,kodebarang_dari,kodebarang_sampai,kodedokter_dari,kodedokter_sampai,cetak_dari,cetak_sampai])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")