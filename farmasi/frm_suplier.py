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

def frm_suplier(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_suplier")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_suplier", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_suplier", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/suplier/suplier.html', {
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

   
def load_suplier(request):
	q = "SELECT SUPPLIERC, NAME_SUPPL, ADDRESS1, ADDRESS2, CITYC, POSTC, TELP, FAX, CONTACT, TOPD, TAXS, NPWP, LIMIT, COAPASIVA, COAPASIVAN, PAYMENT, BRANCH, [USER], [UPDATE],B.NAMA  "
	q +="FROM SUPPLIER AS A LEFT OUTER JOIN TPAY AS B ON A.PAYMENT=B.TPAY_ID ORDER BY SUPPLIERC ASC"
	result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def load_suplierDisc(request):
	kode_suplier = request.GET['kode_suplier']
	q = "SELECT a.FMSDKODESUP, FMSDKODEBRG, FMSDDISC01, FMSDDISC02,USERRS,UPDATERS,b.NAME_BRG,b.HPOKOK FROM  "
	q +="SUPPLIER_DISC a inner join BARANG b on a.FMSDKODEBRG=b.BARANGC where a.FMSDKODESUP=%s "
	result =Globals().getDataQuery(q, [kode_suplier])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getsuplier(request):
	kode_suplier = '%'+request.GET['search_kode_suplier']+'%'
	nama_suplier = '%'+request.GET['search_nama_suplier']+'%'
	q = "SELECT SUPPLIERC, NAME_SUPPL, ADDRESS1, ADDRESS2, CITYC, POSTC, TELP, FAX, CONTACT, TOPD, TAXS, NPWP, LIMIT, COAPASIVA, COAPASIVAN, PAYMENT, BRANCH, [USER], [UPDATE],B.NAMA  "
	q += "FROM SUPPLIER AS A LEFT OUTER JOIN TPAY AS B ON A.PAYMENT=B.TPAY_ID "
	q += "WHERE (SUPPLIERC LIKE %s) AND (NAME_SUPPL LIKE %s) "
	result =Globals().getDataQuery(q, [kode_suplier,nama_suplier])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")


def getDatasuplier(request):
	kode_suplier = request.GET['kode_suplier']
	q = "A.SELECT SUPPLIERC, NAME_SUPPL, ADDRESS1, ADDRESS2, CITYC, POSTC, TELP, FAX, CONTACT, TOPD, TAXS, NPWP, LIMIT, COAPASIVA, COAPASIVAN, PAYMENT, BRANCH, [USER], [UPDATE],B.NAMA "
	q += "FROM SUPPLIER AS A LEFT OUTER JOIN TPAY AS B ON A.PAYMENT=B.TPAY_ID  "
	q += "WHERE (SUPPLIERC = %s) "
	result =Globals().getDataQuery(q, [kode_suplier])
	if len(result)==0:
		data={
			'status':'gagal',
			'pesen':'data tidak ditemukan',
			'data':None
		}
	else:
		data={
			'status':'ok',
			'pesen':'data ditemukan',
			'data':result[0]
		}
	json_data = json.dumps(data, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def suplier_simpan(request):
	kode = request.POST['kode']
	nama = request.POST['nama']
	alamat = request.POST['alamat']
	kota = request.POST['kota']
	kodepos = request.POST['kodepos']
	top = request.POST['top']
	telepon = request.POST['telepon']
	fax = request.POST['fax']
	contact = request.POST['contact']
	npwp = request.POST['npwp']
	coa = request.POST['coa']
	coan = request.POST['coan']
	tpay = request.POST['tpay']
	status_aud = request.POST['status_aud']
	OutputNoBukti = request.POST['OutputNoBukti']
    # dgn Store procedure
	q = "exec FRM_AUD_SUPLIER  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
	result = Globals().getDataSP(q, [kode, nama, alamat, kota, kodepos, telepon, fax, contact, npwp, coa, coan,top,tpay,status_aud,OutputNoBukti])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_suplier(request):
	start = request.GET['start']
	finish = request.GET['finish']
	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	# proses cetak
	# print(start) 
	pdf_file = Globals().generateReportDB(
		"supplier_frm.jrxml", 
		'supplier_frm', 
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

def getcoa(request):
	q = "select a.ACCOUNT,a.DESCRIPTION from ACCOUNT a "
	q += "WHERE POST_FLAG=1 "
	result =Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getCoa2(request):
	kode_Coa = request.GET['search_kode_coa']
	q = "SELECT ACCOUNT, DESCRIPTION "
	q += "FROM ACCOUNT  "
	q += "WHERE   POST_FLAG=1 and (ACCOUNT= %s)  "

	result =Globals().getDataQuery(q, [kode_Coa])
	# json_data = json.dumps(result, cls=DjangoJSONEncoder) jika multi
	json_data = json.dumps(result[0], cls=DjangoJSONEncoder) #jika single
	return HttpResponse(json_data, content_type="application/json")

def getTpay(request):
	q = "select  TPAY_ID,NAMA,KODE_REKENING from TPAY "
	result =Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def barangdiscsup_simpan(request):
	kode = request.POST['kode']
	kodebarang = request.POST['kodebarang']
	disc01 = request.POST['disc01']
	disc02 = request.POST['disc02']
	userrs= request.session['user_id']
	status_aud = request.POST['status_aud']

	OutputNoBukti = request.POST['OutputNoBukti']
	q = "exec FRM_AUD_SUPPLIERDISC  %s, %s, %s, %s, %s, %s, %s"
	result = Globals().getDataSP(q, [kode, kodebarang, disc01, disc02,userrs, status_aud, OutputNoBukti])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")