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


def exit(request):
	return redirect('/')

def frm_pabrikan(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_pabrikan")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_pabrikan", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_pabrikan", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/pabrikan/pabrikan.html', {
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

def load_pabrikan(request):
	q = "SELECT FMPSUPPLIERC, FMPNAME_SUPPL, FMPADDRESS1, FMPADDRESS2, FMPCITYC, FMPPOSTC, FMPTELP, FMPFAX, FMPCONTACT, [USER], [UPDATE]  "
	q +="FROM PABRIKAN AS A ORDER BY FMPSUPPLIERC ASC"
	result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getpabrikan(request):
	kode_pabrikan = '%'+request.GET['search_kode_pabrikan']+'%'
	nama_pabrikan = '%'+request.GET['search_nama_pabrikan']+'%'
	q = "SELECT FMPSUPPLIERC, FMPNAME_SUPPL, FMPADDRESS1, FMPADDRESS2, FMPCITYC, FMPPOSTC, FMPTELP, FMPFAX, FMPCONTACT, [USER], [UPDATE]  "
	q += "FROM PABRIKAN AS A  "
	q += "WHERE (FMPSUPPLIERC LIKE %s) AND (FMPNAME_SUPPL LIKE %s) order by FMPNAME_SUPPL "
	result = Globals().getDataQuery(q, [kode_pabrikan,nama_pabrikan])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")


def getDatapabrikan(request):
	kode_pabrikan = request.GET['kode_pabrikan']

	q = "A.SELECT FMPSUPPLIERC, FMPNAME_SUPPL, FMPADDRESS1, FMPADDRESS2, FMPCITYC, FMPPOSTC, FMPTELP, FMPFAX, FMPCONTACT, [USER], [UPDATE] "
	q += "FROM PABRIKAN AS A  "
	q += "WHERE (FMPSUPPLIERC = %s) "

	result = Globals().getDataQuery(q, [kode_pabrikan])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def pabrikan_simpan(request):
	kode = request.POST['kode']
	nama = request.POST['nama']
	alamat = request.POST['alamat']
	kota = request.POST['kota']
	kodepos = request.POST['kodepos']
	telepon = request.POST['telepon']
	fax = request.POST['fax']
	contact = request.POST['contact']
	status_aud = request.POST['status_aud']
	OutputNoBukti = request.POST['OutputNoBukti']
    # dgn Store procedure
	q = "exec FRM_AUD_PABRIKAN  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
	result = Globals().getDataSP(q, [kode, nama, alamat, kota, kodepos, telepon, fax, contact,status_aud,OutputNoBukti])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_pabrikan(request):
	start = request.GET['start']
	finish = request.GET['finish']
	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pdf_file = Globals().generateReportDB(
		"pabrikan_frm.jrxml", 
		'pabrikan_frm', 
		user,
		{
			'start': start,
			'finish': finish,
			'nama_rs':  request.session['nama_cabang'],
			'alamat_rs':  request.session['alamat_cabang'],
			'tanggal': Globals().tanggalIndo(tanggal),
			'jam': jam,
		}
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")
