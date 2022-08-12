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

#-------------------INV JENIS-----------------------
def exit(request):
	return redirect('/')

def frm_lokasi(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_sediaan")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_sediaan", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_sediaan", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/lokasi/lokasi.html', {
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
	
def load_lokasi(request):
	q = "select a.FMLFKODE,a.FMLFKETERAGAN FROM LOKASI a  "
	q +="order by FMLFKODE asc "
	result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getlokasi(request):
	kode_lokasi = '%'+request.GET['search_kode_lokasi']+'%'
	nama_lokasi = '%'+request.GET['search_nama_lokasi']+'%'
	q = "SELECT FMLFKODE, FMLFKETERAGAN "
	q += "FROM LOKASI  "
	q += "WHERE (FMLFKODE LIKE %s) AND (FMLFKETERAGAN LIKE %s) "
	result = Globals().getDataQuery(q, [kode_lokasi,nama_lokasi])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def lokasi_simpan(request):
	kode = request.POST['kode']
	nama = request.POST['nama']
	status_aud = request.POST['status_aud']
	q = "exec FRM_AUD_LOKASI  %s, %s, %s "
	result = Globals().getDataSP(q, [kode,nama,status_aud])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")
	
def cetak_lokasi(request):
	start = request.GET['start']
	finish = request.GET['finish']
	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	# proses cetak
	# print(start) 
	pdf_file = Globals().generateReportDB(
		"lokasi_frm.jrxml", 
		'lokasi_frm', 
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
