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

def frm_printstock005(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_printstock005")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printstock005", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printstock005", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/printstock004/printstock004.html', {
			'navbars': navbars,
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			'user_id': user_privelege,
			'title': 'Persediaan Stock',
		})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')



def persediaanstock(request):
	kodebarang_dr = request.GET['kodebarang_dari']
	kodebarang_sd = request.GET['kodebarang_sampai']
	kodeproduk_dari = request.GET['kodeproduk_dari']
	kodeproduk_sampai = request.GET['kodeproduk_sampai']
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	tanggal_dr = request.GET['tanggal_dr']

	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pilihcetak=request.GET['pilihcetak']

	pdf_file = Globals().generateReportDB(
		"FIFOINVDISTRIBUTOR.jrxml", 
		'FIFOINVDISTRIBUTOR', 
		user,
		{
			'kodebarang_dari':kodebarang_dr,
			'kodebarang_sd':kodebarang_sd,
			'kodeproduk_dari':kodeproduk_dari,
			'kodeproduk_sampai':kodeproduk_sampai,
			'cetak_dari':cetak_dari,
			'cetak_sampai':cetak_sampai,
			'start': tanggal_dr,
			'nama_rs': request.session['nama_cabang'],
		},
		list_format=[pilihcetak]
	)

	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def proses_excel(request):
	kodebarang_dr = request.GET['kodebarang_dari']
	kodebarang_sd = request.GET['kodebarang_sampai']
	kodeproduk_dari = request.GET['kodeproduk_dari']
	kodeproduk_sampai = request.GET['kodeproduk_sampai']
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	tanggal_dr = request.GET['tanggal_dr']
	q = "SELECT  ROW_NUMBER() OVER (PARTITION BY e.NAME_WH,d.NAME_SUPPL,C.NAME_PRD ORDER BY e.NAME_WH,d.NAME_SUPPL,C.NAME_PRD,b.NAME_BRG) AS NO, a.FFONOM, a.FFOBRG_ID as id_barang, a.FFODATE, a.FFOSUPP_ID, a.FFOQTY_SAWAL, "
	q +="(a.FFOQTY_BELI+a.FFOQTY_RETURJ+a.FFOQTY_CLMMASUK) as Masuk,(a.FFOQTY_RETURB+ a.FFOQTY_CLMKELUAR+a.FFOQTY_JUALKOTA+ a.FFOQTY_JUALLKOTA) as Keluar,  "
	q += "a.FFOQTY_HPOKOK as hargapokok,  a.FFOWH_ID AS id_gudang, b.NAME_BRG as nama_barang,b.SATSTAND as satuan, b.TTYPEC, c.NAME_PRD AS nama_produk, d.NAME_SUPPL, e.NAME_WH AS Gudang "
	q += "FROM FIFO AS a INNER JOIN "
	q += "BARANG AS b ON a.FFOBRG_ID = b.BARANGC INNER JOIN "
	q += "WAREHOUSE AS e ON a.FFOWH_ID = e.WH_ID INNER JOIN "
	q += "SUPPLIER AS d ON a.FFOSUPP_ID = d.SUPPLIERC INNER JOIN "
	q += "PRODUKOBAT AS c ON b.TTYPEC = C.PRD_ID "
	q += "WHERE  (b.TTYPEC >=%s) AND (b.TTYPEC <=%s)  "
	q += "AND (a.FFOBRG_ID >=%s) AND (a.FFOBRG_ID <=%s)  "
	q += "AND (a.FFOWH_ID >=%s) AND (a.FFOWH_ID <=%s) "
	q += "AND a.FFODATE = %s "
	q += "ORDER BY Gudang asc,d.NAME_SUPPL asc, nama_produk asc,  b.NAME_BRG asc "
	result = Globals().getDataQuery(q,[kodeproduk_dari,kodeproduk_sampai,kodebarang_dr,kodebarang_sd,cetak_dari,cetak_sampai,tanggal_dr])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")
