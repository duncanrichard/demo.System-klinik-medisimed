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

def frm_printinfo003(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_printinfo001")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printinfo001", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/printsales008/printsales008.html', {
			'navbars': navbars,
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			'user_id': user_privelege,
			'title': 'Stock expired',
		})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def proses_lap_expired(request):
	tanggal_dr = request.GET['tanggal_dr']
	q = "Select  a.FDFBBRG_ID, FDFBBRGN, FDFBSATUAN,FDFBBATHNO, FDFBHPOKOK, FDFBQTYT, FDFBDISC1, FDFBDISC2, FDFBDISC3, FDFBTOTAL,  FDFBBUKTI_ID, FDFBSUPPL_ID,d.NAME_SUPPL, a.FDFBTGL_EXPIRED,  "
	q += "SUM((isnull(C.FSBSALDO_AWAL,0)-isnull(C.FSBPENJUALAN,0)+isnull(C.FSBRPENJUALAN,0)+  isnull(C.FSBPEMBELIAN,0)-isnull(C.FSBRPEMBELIAN,0)+isnull(C.FSBLAIN_MASUK,0)-  isnull(C.FSBLAIN_KELUAR,0)-isnull(C.FSBKANVAS,0)+isnull(C.FSBRKANVAS,0))) AS AVL_QTY  "
	q += "from FBELID a INNER JOIN Saldobarang c ON a.FDFBBRG_ID=c.FSBBRG_ID "
	q += "INNER JOIN SUPPLIER d ON a.FDFBSUPPL_ID=d.SUPPLIERC  "
	q += "where  (a.FDFBTGL_EXPIRED IS NOT NULL)  and FDFBTGL_EXPIRED<= %s and FDFBTGL_EXPIRED<>'1900-01-01' "
	q += "AND  ((isnull(C.FSBSALDO_AWAL,0)-isnull(C.FSBPENJUALAN,0)+isnull(C.FSBRPENJUALAN,0)+  isnull(C.FSBPEMBELIAN,0)-isnull(C.FSBRPEMBELIAN,0)+isnull(C.FSBLAIN_MASUK,0)-  isnull(C.FSBLAIN_KELUAR,0)-isnull(C.FSBKANVAS,0)+isnull(C.FSBRKANVAS,0)))<>0  "
	q += "and  FDFBBRG_ID NOT in (select Y.FDFBBRG_ID from FBELI Z INNER JOIN FBELID Y ON Z.FHFBBUKTI_ID=Y.FDFBBUKTI_ID where    FDFBTGL_EXPIRED> %s )  "
	q += "GROUP BY a.FDFBBRG_ID, FDFBBRGN, FDFBSATUAN,FDFBBATHNO, FDFBHPOKOK, FDFBQTYT, FDFBDISC1, FDFBDISC2, FDFBDISC3, FDFBTOTAL,  FDFBBUKTI_ID, FDFBSUPPL_ID,d.NAME_SUPPL, a.FDFBTGL_EXPIRED  order by NAME_SUPPL,a.FDFBBRGN  "

	result = Globals().getDataQuery(q, [tanggal_dr,tanggal_dr])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")