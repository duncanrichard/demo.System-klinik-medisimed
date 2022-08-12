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

def frm_sediaan(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_sediaan")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_sediaan", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_sediaan", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/sediaan/sediaan.html', {
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

def load_sediaan(request):
	
	q = "select a.FMSKODE,a.FMSSEDIAAN FROM SEDIAAN a  "
	q +="order by FMSKODE asc "
	result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")


def getsediaan(request):
	
	kode_sediaan = '%'+request.GET['search_kode_sediaan']+'%'
	nama_sediaan = '%'+request.GET['search_nama_sediaan']+'%'

	q = "SELECT FMSKODE, FMSSEDIAAN "
	q += "FROM SEDIAAN  "
	q += "WHERE (FMSKODE LIKE %s) AND (FMSSEDIAAN LIKE %s) "
	result = Globals().getDataQuery(q, [kode_sediaan,nama_sediaan])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def sediaan_simpan(request):
	kode = request.POST['kode']
	nama = request.POST['nama']
	status_aud = request.POST['status_aud']
	q = "exec FRM_AUD_SEDIAAN  %s, %s, %s "
	result = Globals().getDataSP(q, [kode,nama,status_aud])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_sediaan(request):
	start = request.GET['start']
	finish = request.GET['finish']
	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	# proses cetak
	# print(start) 
	pdf_file = Globals().generateReportDB(
		"sediaan_frm.jrxml", 
		'sediaan_frm', 
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
