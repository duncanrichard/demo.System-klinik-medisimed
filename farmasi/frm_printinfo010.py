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

def frm_printinfo010(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_printinfo001")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/printsales009/printsales009.html', {
			'navbars': navbars,
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			'user_id': user_privelege,
			'title': 'Umur Stock',
		})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')


def proses_lap_umur(request):
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	tanggal_dr = request.GET['tanggal_dr']
	tanggal_sd = request.GET['tanggal_sd']

	q = "SELECT a.FSBWH_ID, b.NAME_WH, a.FSBBRG_ID, dbo.BARANG.NAME_BRG, (ISNULL(a.FSBSALDO_AWAL, 0) + ISNULL(a.FSBRPENJUALAN, 0) + ISNULL(a.FSBPEMBELIAN, 0) + ISNULL(a.FSBLAIN_MASUK, 0)  "
	q += "+ ISNULL(a.FSBRKANVAS, 0)) - (ISNULL(a.FSBPENJUALAN, 0) + ISNULL(a.FSBRPEMBELIAN, 0) + ISNULL(a.FSBLAIN_KELUAR, 0) + ISNULL(a.FSBKANVAS, 0)) AS AVL_QTY "
	q += "FROM dbo.SALDOBARANG AS a INNER JOIN "
	q += "dbo.WAREHOUSE AS b ON a.FSBWH_ID = b.WH_ID INNER JOIN "
	q += "dbo.BARANG ON a.FSBBRG_ID = dbo.BARANG.BARANGC "
	q += "WHERE ((ISNULL(a.FSBSALDO_AWAL, 0) + ISNULL(a.FSBRPENJUALAN, 0) + ISNULL(a.FSBPEMBELIAN, 0) + ISNULL(a.FSBLAIN_MASUK, 0) + ISNULL(a.FSBRKANVAS, 0)) - (ISNULL(a.FSBPENJUALAN, 0) + ISNULL(a.FSBRPEMBELIAN, 0)  "
	q += "+ ISNULL(a.FSBLAIN_KELUAR, 0) + ISNULL(a.FSBKANVAS, 0)) <> 0) "
	q += "AND fsbbrg_id not in (select b.FDFJBRG_ID from fjinkota a INNER JOIN fjinkotaD b ON a.FHFJBUKTI_ID=b.FDFJBUKTI_ID "
	q += "WHERE FHFJDATE>= %s  AND FHFJDATE<= %s) "
	q += "AND A.FSBWH_ID>= %s AND A.FSBWH_ID<= %s "

	result = Globals().getDataQuery(q, [tanggal_dr,tanggal_sd,cetak_dari,cetak_sampai])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")