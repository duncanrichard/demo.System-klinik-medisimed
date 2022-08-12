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

def frm_produk(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_produk")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_produk", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_produk", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/produk_barang/produk_barang.html', {
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
def load_produk_barang(request):
	
	q = "select a. PRD_ID,a.NAME_PRD,STATUSPRODUK,PROFITMARGIN,PROFITMARGINRI FROM   PRODUKOBAT a  "
	q +="order by  PRD_ID asc "
	result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")


def getproduk_barang(request):
	kode_produk_barang = '%'+request.GET['search_kode_produk_barang']+'%'
	nama_produk_barang = '%'+request.GET['search_nama_produk_barang']+'%'
	q = "SELECT  PRD_ID,NAME_PRD,STATUSPRODUK,PROFITMARGIN,PROFITMARGINRI "
	q += "FROM   PRODUKOBAT  "
	q += "WHERE ( PRD_ID LIKE %s) AND (  NAME_PRD LIKE %s) "
	result = Globals().getDataQuery(q, [kode_produk_barang,nama_produk_barang])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def produk_barang_simpan(request):
	kode = request.POST['kode']
	NAME_PRD = request.POST['nama']
	statusproduk = request.POST['statusproduk']
	pmjual_rj= request.POST['pmjual_rj']
	pmjual_ri= request.POST['pmjual_ri']
	status_aud = request.POST['status_aud']
	q = "exec FRM_AUD_PRODUK  %s, %s, %s,%s, %s, %s "
	result = Globals().getDataSP(q, [kode,NAME_PRD,statusproduk,pmjual_rj,pmjual_ri,status_aud])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_produk_barang(request):
	start = request.GET['start']
	finish = request.GET['finish']
	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	# proses cetak
	# print(start) 
	pdf_file = Globals().generateReportDB(
		"produk_barang_frm.jrxml", 
		'produk_barang_frm', 
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
