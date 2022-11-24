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

def frm_Ajdustment(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_mutasi_K01")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_mutasi_K01", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_mutasi_K01", '1')
		menubarCount = len(menubars)
		response = render(request, 'farmasi/mutasi_adjustment/mutasiadjustment.html', {
			'navbars': navbars,
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			'user_id': user_privelege,
			'kondisi_gudang' : getattr(env, 'kondisi_gudang',1),
		})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def getdivisi(request):
	tipe = request.GET['tipe']
	ID_CABANG = request.session['kdCabang']
	if(tipe == 'Divisi'):
		kode = request.GET['kode']
		q = "SELECT WH_ID, NAME_WH "
		q += "FROM WAREHOUSE  "
		q += "WHERE (WH_ID LIKE %s) AND aktif=1 and BRANCH=%s"
		result = Globals().getDataQuery(q,[kode,ID_CABANG])
	else:
		kode_divisi = '%'+request.GET['search_kode_divisi']+'%'
		nama_divisi = '%'+request.GET['search_nama_divisi']+'%'
		q = "SELECT WH_ID, NAME_WH "
		q += "FROM WAREHOUSE  "
		q += "WHERE (WH_ID LIKE %s) AND (NAME_WH LIKE %s)  AND aktif=1 and BRANCH=%s "
		result = Globals().getDataQuery(q, [kode_divisi,nama_divisi,ID_CABANG])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getIdDataBarang(request):
	kode = request.GET['kode']
	gudang = request.GET['gudang']
	q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,HPOKOK,TTYPEC,c.STATUSPRODUK,   "
	q += "CAST(((isnull(b.FSBSALDO_AWAL,0)+isnull(b.FSBPEMBELIAN,0)+isnull(b.FSBLAIN_MASUK,0)) - "
	q += "(isnull(b.FSBPENJUALAN,0)+isnull(b.FSBLAIN_KELUAR,0))) AS INT) AS STOK "
	q +=" FROM BARANG A INNER JOIN PRODUKOBAT c ON  A.TTYPEC=c.PRD_ID  "
	q +=" left join SALDOBARANG b on a.BARANGC = b.FSBBRG_ID  where BARANGC=%s  and b.FSBWH_ID=%s order by BARANGC "

	result = Globals().getDataQuery(q, [kode,gudang])
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

def SP_AUD_PCLAIMS(request):
	# DETAIL
	NO = json.loads(request.POST['NO'])
	TTYPEC = json.loads(request.POST['TTYPEC'])
	BARANGC = json.loads(request.POST['BARANGC'])
	NAME_BRG = json.loads(request.POST['NAME_BRG'])
	SATSTAND = json.loads(request.POST['SATSTAND'])
	HPOKOK = json.loads(request.POST['HPOKOK'])
	STOCK = json.loads(request.POST['STOCK'])
	PHISIK = json.loads(request.POST['PHISIK'])
	QTY = json.loads(request.POST['QTY'])
	TOTAL = json.loads(request.POST['TOTAL'])

	# MAIN EXEC
	FHPCLMBUKTI_ID = request.POST['FHPCLMBUKTI_ID']
	FHPCLMTGL = request.POST['FHPCLMTGL']
	FHPCLMCUST_ID = request.POST['FHPCLMCUST_ID']
	FHPCLMCUSTN = request.POST['FHPCLMCUSTN']
	FHPCLMWH_ID = request.POST['FHPCLMWH_ID']
	FHPCLMWHN = request.POST['FHPCLMWHN']
	FHPCLMREMARK = request.POST['FHPCLMREMARK']
	FHPCLMJENIS = request.POST['FHPCLMJENIS']
	StatusAUD = request.POST['StatusAUD']
	FKSMUTASI = request.POST['FKSMUTASI']

	USERRS = request.session['user_id']

	q = "DECLARE @LIST_FJINKOTAD FJINKOTAD;"
	q += "DECLARE @NOW datetime; "
	q += "SET @NOW = GETDATE(); "

	proc_param = []
	i = 0
	for x in BARANGC:
		q += "INSERT INTO @LIST_FJINKOTAD (FDFJNOM, FDFJPRD_ID, FDFJBRG_ID, FDFJBRGN, FDFJSATUAN, FDFJHJUAL,FDFJDISC1,FDFJDISC4, FDFJQTY) "
		q += "VALUES ("
		q += "'" + NO[i] + "',"
		q += "'" + TTYPEC[i] + "',"
		q += "'" + BARANGC[i] + "',"
		q += "%s,"
		q += "'" + SATSTAND[i] + "',"
		q += HPOKOK[i] + ","
		q += STOCK[i] + ","
		q += PHISIK[i] + ","
		q += QTY[i] + ");"
		proc_param.extend([NAME_BRG[i]])
		i += 1

	q += "EXEC FRM_AUD_PCLAIMS_ADJ "
	q += "'" + FHPCLMBUKTI_ID + "',"
	q += "'" + FHPCLMTGL + "',"
	q += "'" + FHPCLMCUST_ID + "',"
	q += "'" + FHPCLMCUSTN + "',"
	q += "'" + FHPCLMWH_ID + "',"
	q += "'" + FHPCLMWHN + "',"
	q += "'" + FHPCLMREMARK + "',"
	q += "'" + FHPCLMJENIS + "',"
	q += "'" + USERRS + "',"
	q += "@NOW,"
	q += "'" + StatusAUD + "',"
	q += "'" + FKSMUTASI + "',"
	q += "@LIST_FJINKOTAD,"
	q += "''"

	if (StatusAUD=='D') :
		user = {
		'user_id': request.session['user_id'],
		'user_name': request.session['user_name'],
		'user_priv': request.session['user_priv'],
		}
		data = []
		data.append({"query": "select * from PCLAIMS where FHPCLMBUKTI_ID = '" + FHPCLMBUKTI_ID + "'"})
		data.append({"query": "select * from PCLAIMSD where FDPCLMBUKTI_ID = '" + FHPCLMBUKTI_ID + "'"})
		Globals().create_log('Hapus LogDelete.txt', 'FARMASI', data, user)

	try:
		result = Globals().getDataSP(q,proc_param)
		json_data = json.dumps(result, cls=DjangoJSONEncoder)
		return HttpResponse(json_data, content_type="application/json")

	except ValueError:
		print(q)

def getMutasiKeluar(request):
	no_bukti = '%'+request.GET['no_bukti']+'%'
	pasien = '%'+request.GET['pasien']+'%'
	gudang = '%'+request.GET['gudang']+'%'
	tipe = request.GET['tipe']
	FHPCLMJENIS= request.GET['FHPCLMJENIS']

	tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")

	if(tipe == 'mutasi_by_bulan'):
		q = "select top 100 *, convert(varchar, FHPCLMTGL, 23) as TANGGAL "
		q +="from PCLAIMS where (FHPCLMBUKTI_ID like %s) and (FHPCLMCUSTN like %s) and "
		q += "(FHPCLMWHN like %s) and (YEAR(FHPCLMTGL) = %s) and (MONTH(FHPCLMTGL) = %s) AND FHPCLMJENIS= %s"
		result = Globals().getDataQuery(q, [no_bukti, pasien, gudang, tanggal.year, tanggal.month,FHPCLMJENIS])
	else:
		q = "select top 100 *, convert(varchar, FHPCLMTGL, 23) as TANGGAL "
		q +="from PCLAIMS where (FHPCLMBUKTI_ID like %s) and (FHPCLMCUSTN like %s) and "
		q += "(FHPCLMWHN like %s) and (FHPCLMTGL = %s AND FHPCLMJENIS= %s )"
		result = Globals().getDataQuery(q, [no_bukti, pasien, gudang, tanggal,FHPCLMJENIS])

	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getBarangByBuktiKeluar(request):
	no_bukti = request.GET['no_bukti']
	q = "select b.*, a.FDPCLMNOM as NO, a.FDPCLMPRD_ID as TTYPEC, a.FDPCLMBRG_ID as BARANGC, "
	q += "a.FDPCLMBRGN as NAME_BRG, a.FDPCLMSATUAN as SATSTAND, CAST(a.FDPCLMSTOCKQTY AS INT) as Stock,CAST(a.FDPCLMPHISIKQTY AS INT) as Phisik,CAST(a.FDPCLMQTY AS INT) as QTY, a.FDPCLMHPOKOK as HPOKOK "
	q += "from PCLAIMSD a left join PCLAIMS b on a.FDPCLMBUKTI_ID = b.FHPCLMBUKTI_ID "
	q += "where a.FDPCLMBUKTI_ID = %s order by FDPCLMNOM asc"
	result = Globals().getDataQuery(q, [no_bukti])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetakBarangKeluar(request):
	nomor = request.GET['no_bukti']
	tanggal_waktu_cetak = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pilihcetak=request.GET['pilihcetak'] 
	pdf_file = Globals().generateReportDB(
		"mutasi_bhp_Adj.jrxml", 
		'mutasi_bhp_Adj', 
		user,
		{
			'nomor': nomor,
			'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
			'tanggal_waktu_cetak': Globals().dateIndo(tanggal_waktu_cetak),
		},
		list_format=[pilihcetak]
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_lap_mutasi_BHP(request):
	start = request.GET['start']
	finish = request.GET['finish']
	dariDivisi = request.GET['dariDivisi']
	sdDivisi = request.GET['sdDivisi']
	dari_Tgl_minta = request.GET['dari_Tgl_minta']
	sd_Tgl_minta = request.GET['sd_Tgl_minta']
	STSJENIS=request.GET['STSJENIS']
	pilihcetak=request.GET['pilihcetak'] 
	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	# proses cetak
	# print(finish) 
	pdf_file = Globals().generateReportDB(
		"mutasi_bhp_Adj2.jrxml", 
		'mutasi_bhp_Adj2', 
		user,
		{
			'start': start,
			'finish': finish,
			'dariDivisi': dariDivisi,
			'sdDivisi': sdDivisi,
			'dari_Tgl_minta': dari_Tgl_minta,
			'sd_Tgl_minta': sd_Tgl_minta,
			'STSJENIS': STSJENIS,
			'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
		},
		list_format=[pilihcetak]
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_lap_mutasi_BHP_REKAP(request):
	start = request.GET['start']
	finish = request.GET['finish']
	dariDivisi = request.GET['dariDivisi']
	sdDivisi = request.GET['sdDivisi']
	dari_Tgl_minta = request.GET['dari_Tgl_minta']
	sd_Tgl_minta = request.GET['sd_Tgl_minta']
	STSJENIS=request.GET['STSJENIS']
	pilihcetak=request.GET['pilihcetak'] 
	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	# proses cetak
	pdf_file = Globals().generateReportDB(
		"mutasi_bhp_Adj3.jrxml", 
		'mutasi_bhp_Adj3', 
		user,
		{
			'start': start,
			'finish': finish,
			'dariDivisi': dariDivisi,
			'sdDivisi': sdDivisi,
			'dari_Tgl_minta': dari_Tgl_minta,
			'sd_Tgl_minta': sd_Tgl_minta,
			'STSJENIS': STSJENIS,
			'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
		},
		list_format=[pilihcetak]
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")


def dateIndo(date):
    tgl = date.split("-")
    tanggal = tgl[2]
    bulan = tgl[1]
    tahun = tgl[0]

    if (bulan == '01'):
        bulan = ' Januari '
    elif (bulan == '02'):
        bulan = ' Februari '
    elif (bulan == '03'):
        bulan = ' Maret '
    elif (bulan == '04'):
        bulan = ' April '
    elif (bulan == '05'):
        bulan = ' Mei '
    elif (bulan == '06'):
        bulan = ' Juni '
    elif (bulan == '07'):
        bulan = ' Juli '
    elif (bulan == '08'):
        bulan = ' Agustus '
    elif (bulan == '09'):
        bulan = ' September '
    elif (bulan == '10'):
        bulan = ' Oktober '
    elif (bulan == '11'):
        bulan = ' November '
    else:
        bulan = ' Desember '

    return tanggal + bulan + tahun

	
