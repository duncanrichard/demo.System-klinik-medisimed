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

def frm_reposstock(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_reposstock")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_reposstock", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_reposstock", '1')
		menubarCount = len(menubars)
		response = render(request, 'farmasi/proses_reposstock/proses_reposstock.html', {
            'navbars': navbars,
            'menubars': menubars,
            'menubarsChild': menubarsChild,
            'menubarsType': 1,
            'count_': menubarCount,
            'list_': Globals().getSeparator(menubarCount),
            'user_id': user_privelege
        })
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def Monthlyperiode(request):
	cabang_id = request.session['kdCabang']
	q = "select MTH, YR from PARAMETER WHERE COMPANY=%s "
	result = Globals().getDataQuery(q,[cabang_id])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def Restock002(request):
	cabang_id = request.session['kdCabang']
	Tgl_proses = request.GET['Tgl_proses']
	# pprint('tanggal')
	# print (Tgl_proses)
	q = "exec Restock002 "
	q += "'" + Tgl_proses + "','" + cabang_id + "', ''"
	try:
		result = Globals().getDataSP(q)
		json_data = json.dumps(result, cls=DjangoJSONEncoder)
		return HttpResponse(json_data, content_type="application/json")
	except ValueError:
		print(q)
	return HttpResponse(json_data, content_type="application/json")
