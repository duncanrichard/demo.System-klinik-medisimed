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


def frm_printinfo001(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_printinfo001")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/printsales007/printsales007.html', {
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

def proses_lap_limit(request):
	ID_CABANG = request.session['kdCabang']
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	cetak_sampai2 = request.GET['cetak_sampai2']

	pabrik_dari = request.GET['pabrik_dari']
	pabrik_sampai = request.GET['pabrik_sampai']

	q = "SELECT A.BARANGC,NAME_BRG,D.NAME_SUPPL,B.NAME_PRD,A.MERKN,A.SATKEMAS,(KSTANDART*KKECIL) AS KONVERSI,SATSTAND,QTYMAX,QTYMIN,C.FMPSUPPLIERC,FMPNAME_SUPPL,A.HPOKOK, "
	q += "ISNULL((SELECT  (ISNULL(E.FSBSALDO_AWAL,0)-ISNULL(E.FSBPENJUALAN,0)+ISNULL(E.FSBRPENJUALAN,0)+  ISNULL(E.FSBPEMBELIAN,0)-ISNULL(E.FSBRPEMBELIAN,0)+ISNULL(E.FSBLAIN_MASUK,0)-  ISNULL(E.FSBLAIN_KELUAR,0)-ISNULL(E.FSBKANVAS,0)+ISNULL(E.FSBRKANVAS,0))  FROM SALDOBARANG E WHERE  E.FSBBRG_ID=A.BARANGC AND  E.FSBWH_ID= %s ),0) AS AVL_QTY, "
	q += "ISNULL((SELECT  (ISNULL(E.FSBSALDO_AWAL,0)-ISNULL(E.FSBPENJUALAN,0)+ISNULL(E.FSBRPENJUALAN,0)+  ISNULL(E.FSBPEMBELIAN,0)-ISNULL(E.FSBRPEMBELIAN,0)+ISNULL(E.FSBLAIN_MASUK,0)-  ISNULL(E.FSBLAIN_KELUAR,0)-ISNULL(E.FSBKANVAS,0)+ISNULL(E.FSBRKANVAS,0))  FROM SALDOBARANG E WHERE  E.FSBBRG_ID=A.BARANGC AND  E.FSBWH_ID= %s ),0) AS AVL_QTY2, "
	q += "ISNULL((SELECT  (ISNULL(E.FSBSALDO_AWAL,0)-ISNULL(E.FSBPENJUALAN,0)+ISNULL(E.FSBRPENJUALAN,0)+  ISNULL(E.FSBPEMBELIAN,0)-ISNULL(E.FSBRPEMBELIAN,0)+ISNULL(E.FSBLAIN_MASUK,0)-  ISNULL(E.FSBLAIN_KELUAR,0)-ISNULL(E.FSBKANVAS,0)+ISNULL(E.FSBRKANVAS,0))  FROM SALDOBARANG E WHERE  E.FSBBRG_ID=A.BARANGC AND  E.FSBWH_ID= %s ),0) AS AVL_QTY3,'' AS QTYTHREEMONTH "
	q += "FROM BARANG A LEFT JOIN PRODUKOBAT B ON A.TTYPEC=B.PRD_ID LEFT JOIN SUPPLIER D ON A.SUPPLIER_ID=D.SUPPLIERC "
	q += "LEFT JOIN PABRIKAN C ON A.PABRIKAN=C.FMPSUPPLIERC "
	q += "WHERE   A.AKTIF=0 AND QTYMIN<> 0  "
	q += "AND A.PABRIKAN>= %s AND A.PABRIKAN<= %s AND A.BRANCH= %s "  
	q += "ORDER BY NAME_SUPPL,A.NAME_BRG "
	result = Globals().getDataQuery(q, [cetak_dari,cetak_sampai,cetak_sampai2,pabrik_dari,pabrik_sampai,ID_CABANG])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")