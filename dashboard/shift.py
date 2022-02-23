from django.shortcuts import render,redirect
from django.http import HttpResponse
# from django.db import connection
# from django.db import connections
import json
from django.core.serializers.json import DjangoJSONEncoder
from urllib.parse import unquote
from inspect import getmembers
from pprint import pprint
from IMMODERMA.globals import Globals
from IMMODERMA.environment import env
from datetime import datetime

def setShift(request):
	request.session['shift_isset'] = '1'
	json_data = json.dumps({"pesan": "Berhasil Disimpan"}, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def tutupShift(request):
	user_priv = request.session['user_priv']

	q = "select SHIFT_AKTIF from PRIVILEGE where USER_PRIV = %s"
	result = Globals().getDataQuery(q, [user_priv])
	shift_aktif = result[0]['SHIFT_AKTIF'].strip()

	q = "select COUNTER, SHIFT_NEW from SHIFT where SHFUSER_PRIV = %s and KD_SHIFT = %s"
	result = Globals().getDataQuery(q, [user_priv, shift_aktif])
	shift_counter = result[0]['COUNTER']
	shift_next = result[0]['SHIFT_NEW'].strip()

	q = "update PRIVILEGE set SHIFT_AKTIF = %s where USER_PRIV = %s; "
	if shift_counter == 1:
		q += "update SHIFT set TGL_SHIFT = DATEADD(d, 1, TGL_SHIFT) where SHFUSER_PRIV = %s; "
		Globals().executeQuery(q, [shift_next, user_priv, user_priv])
	else:
		Globals().executeQuery(q, [shift_next, user_priv])

	qprivilege = 'SELECT TOP 1 * FROM PRIVILEGE WHERE USER_PRIV = %s'
	dataprivilege = Globals().getDataQuery(qprivilege, [request.session['user_priv']])
	request.session['shift_cek'] = dataprivilege[0]['AKTIF']
	request.session['shift_isset'] = '1'
	
	if dataprivilege[0]['SHIFT_AKTIF'] == None:
		request.session['shift_aktif'] = '1'
	else:
		request.session['shift_aktif'] = dataprivilege[0]['SHIFT_AKTIF'].strip()

	qshift = 'SELECT * FROM SHIFT WHERE SHFUSER_PRIV = %s'
	datashift = Globals().getDataQuery(qshift, [request.session['user_priv']])
	request.session['shift_jumlah'] = len(datashift)

	for x in datashift:
		if x['KD_SHIFT'].strip() == dataprivilege[0]['SHIFT_AKTIF'].strip():
			request.session['shift_kode'] = x['KD_SHIFT'].strip()
			request.session['shift_nama'] = x['NAMA_SHIFT'].strip()
			shift_tanggal = str(x['TGL_SHIFT'])
			request.session['shift_tanggal'] = shift_tanggal[0:10].strip()
			request.session['shift_counter'] = x['COUNTER']
			request.session['shift_next'] = x['SHIFT_NEW'].strip()

	json_data = json.dumps({
		'shift_tanggal' : request.session['shift_tanggal'],
		'shift_aktif' : request.session['shift_aktif'],
	}, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def editShift(request):
	# Check Session
	if 'userauth' in request.session:
		is_login = request.session['userauth']
		user_priv = request.session['user_priv']
	else:
		is_login = False

	# Code
	if(is_login):
		if(not Globals().check_access(user_priv, 'DAS018', 'DASHBOARD', None)):
			return redirect('/login')

		# qnavbar = "SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+user_priv+"' AND B.modul = 'DASHBOARD' AND B.submodul IS NULL;"
		# navbars = Globals().getData(qnavbar)
		navbars = Globals().getNavbars(user_priv, 'DASHBOARD', None)

		response = render(request, 'dashboard/edit_shift.html', {
			'navbars': navbars
		})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def updateShift(request):
	user_priv = request.POST['user_priv']
	shift_aktif = request.POST['shift_aktif']
	shift_tanggal = request.POST['shift_tanggal']

	q = "update PRIVILEGE set SHIFT_AKTIF = %s where USER_PRIV = %s"
	Globals().executeQuery(q, [shift_aktif, user_priv])

	q = "update SHIFT set TGL_SHIFT = %s where SHFUSER_PRIV = %s"
	Globals().executeQuery(q, [shift_tanggal, user_priv])

	json_data = json.dumps({"pesan": "Berhasil Diperbarui"}, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getShiftList(request):
	q = "select a.USER_PRIV, RTRIM(a.SHIFT_AKTIF) as SHIFT_AKTIF, dbo.tanggalIndo(convert(varchar, b.TGL_SHIFT, 23)) as TGL_AKTIF from PRIVILEGE a inner join SHIFT b "
	q += "on a.USER_PRIV = b.SHFUSER_PRIV and RTRIM(a.SHIFT_AKTIF) = b.KD_SHIFT where a.AKTIF = 1 order by USER_PRIV "
	result = Globals().getDataQuery(q)

	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getShift(request):
	user_priv = request.GET['user_priv']
	qshift = 'SELECT *, convert(varchar, TGL_SHIFT, 23) as TANGGAL FROM SHIFT WHERE SHFUSER_PRIV = %s'
	datashift = Globals().getDataQuery(qshift, [user_priv])
	shift_jumlah = len(datashift)
	shift_tanggal = datashift[0]['TANGGAL'].strip()

	qprivilege = 'SELECT TOP 1 SHIFT_AKTIF FROM PRIVILEGE WHERE USER_PRIV = %s'
	dataprivilege = Globals().getDataQuery(qprivilege, [user_priv])
	shift_aktif = dataprivilege[0]['SHIFT_AKTIF'].strip()

	data = {
		'shift_jumlah': shift_jumlah,
		'shift_aktif': shift_aktif,
		'shift_tanggal': shift_tanggal
	}

	json_data = json.dumps(data, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")