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

def frm_printstock002(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_printstock002")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printstock002", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_printstock002", '1')
		menubarCount = len(menubars)

		response = render(request, 'farmasi/printstock002/printstock002.html', {
			'navbars': navbars,
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			'user_id': user_privelege,
			'title': 'Posisi Stock-2',
		})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')



def getbarang(request):
	kode_barang = '%'+request.GET['search_kode_barang']+'%'
	nama_barang = '%'+request.GET['search_nama_barang']+'%'
	q = "SELECT A.BARANGC,NAME_BRG,SATSTAND, "
	q += "B.NAME_PRD, C.NAME_SUPPL "
	q +=  "FROM BARANG AS A LEFT JOIN "
	q +=  "PRODUKOBAT AS B ON A.TTYPEC = B.PRD_ID LEFT JOIN "
	q +=  "SUPPLIER AS C ON A.SUPPLIER_ID = C.SUPPLIERC "
	q += "WHERE (BARANGC LIKE %s) AND (NAME_BRG LIKE %s) ORDER BY  NAME_BRG "

	result = Globals().getDataQuery(q, [kode_barang,nama_barang])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getdivisi(request):
	tipe = request.GET['tipe']
	KD_CABANG= request.session['kdCabang']
	if(tipe == 'Divisi'):
		kode = request.GET['kode']
		q = "SELECT WH_ID, NAME_WH "
		q += "FROM WAREHOUSE  "
		q += "WHERE (WH_ID LIKE %s) AND aktif=1 and BRANCH=%s"
		result = Globals().getDataQuery(q,[kode,KD_CABANG])
	else:
		kode_divisi = '%'+request.GET['search_kode_divisi']+'%'
		nama_divisi = '%'+request.GET['search_nama_divisi']+'%'
		q = "SELECT WH_ID, NAME_WH "
		q += "FROM WAREHOUSE  "
		q += "WHERE (WH_ID LIKE %s) AND (NAME_WH LIKE %s)  AND aktif=1 and BRANCH=%s "
		result = Globals().getDataQuery(q, [kode_divisi,nama_divisi,KD_CABANG])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getjenis_barang(request):
	kode_jenis_barang = '%'+request.GET['search_kode_jenis_barang']+'%'
	nama_jenis_barang = '%'+request.GET['search_nama_jenis_barang']+'%'
	q = "select PRD_ID,NAME_PRD from PRODUKOBAT "
	q += "WHERE (PRD_ID LIKE %s) AND (NAME_PRD LIKE %s) "
	result = Globals().getDataQuery(q, [kode_jenis_barang,nama_jenis_barang])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getgolongan_barang(request):
	kode_golongan_barang = '%'+request.GET['search_kode_golongan_barang']+'%'
	nama_golongan_barang = '%'+request.GET['search_nama_golongan_barang']+'%'
	q = "select MERK_ID,NAMA from MERK "
	q += "WHERE (MERK_ID LIKE %s) AND (NAMA LIKE %s) "
	result = Globals().getDataQuery(q, [kode_golongan_barang,nama_golongan_barang])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")



def posisistock(request):
	kodebarang_dr = request.GET['kodebarang_dari']
	kodebarang_sd = request.GET['kodebarang_sampai']
	kodeproduk_dari = request.GET['kodeproduk_dari']
	kodeproduk_sampai = request.GET['kodeproduk_sampai']
	kodegolongan_dari = request.GET['kodegolongan_dari']
	kodegolongan_sampai = request.GET['kodegolongan_sampai']
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	tanggal_dr = request.GET['tanggal_dr']
	tanggal_sd = request.GET['tanggal_sd']

	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pilihcetak=request.GET['pilihcetak']
	KD_CABANG= request.session['kdCabang']

	q = "exec frm_reportstock004 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
	Globals().executeQuery(q, [kodebarang_dr, kodebarang_sd,kodeproduk_dari,kodeproduk_sampai,kodegolongan_dari,kodegolongan_sampai, cetak_dari, cetak_sampai, tanggal_dr, tanggal_sd,KD_CABANG])
	pdf_file = Globals().generateReportDB(
		"posisistock3.jrxml", 
		'posisistock3', 
		user,
		{
			'start': tanggal_dr,
			'finish': tanggal_sd,
			'nama_rs': request.session['nama_cabang'],
		},
		list_format=[pilihcetak]
	)

	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def proses_excel(request):
	kodebarang_dr = request.GET['kodebarang_dari']
	kodebarang_sd = request.GET['kodebarang_sampai']
	kodeproduk_dari = request.GET['kodeproduk_dari']
	kodeproduk_sampai = request.GET['kodeproduk_sampai']
	kodegolongan_dari = request.GET['kodegolongan_dari']
	kodegolongan_sampai = request.GET['kodegolongan_sampai']
	cetak_dari = request.GET['cetak_dari']
	cetak_sampai = request.GET['cetak_sampai']
	tanggal_dr = request.GET['tanggal_dr']
	tanggal_sd = request.GET['tanggal_sd']
	KD_CABANG= request.session['kdCabang']

	q = "exec frm_reportstock004 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
	Globals().executeQuery(q, [kodebarang_dr, kodebarang_sd,kodeproduk_dari,kodeproduk_sampai,kodegolongan_dari,kodegolongan_sampai, cetak_dari, cetak_sampai, tanggal_dr, tanggal_sd,KD_CABANG])

	q = "SELECT id_gudang,Gudang,id_barang,nama_barang,satuan,id_produk,nama_produk,id_golongan,nama_golongan, "
	q += "qty_saldo,qty_Beli,qty_RBeli,qty_Jual,qty_RJual,qty_MLain,qty_KLain,qty_MPindah,qty_KPindah,hargapokok, "
	q += "(isnull(qty_saldo,0)+isnull(qty_Beli,0)-isnull(qty_RBeli,0)-isnull(qty_Jual,0)+isnull(qty_RJual,0)+ "
	q += " isnull(qty_MLain,0)-isnull(qty_KLain,0)+isnull(qty_MPindah,0)-isnull(qty_KPindah,0)) as qty_Saldoakhir "
	q += "FROM ##POSISITOCK "
	q += "ORDER BY id_gudang,nama_barang "

	result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")


