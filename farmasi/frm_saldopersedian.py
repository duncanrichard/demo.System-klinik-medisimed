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

def frm_saldopersedian(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_saldopersedian")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_saldopersedian", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_saldopersedian", '1')
		menubarCount = len(menubars)
		qmastercoa = "SELECT * FROM MASTER_COA"
		mastercoa = Globals().getDataQuery(qmastercoa)

		response = render(request, 'farmasi/saldo_persediaan/saldo_persediaan.html', {
            'navbars': navbars,
            'menubars': menubars,
			'mastercoa':mastercoa,
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

def getIdDataBarang(request):
	
	kode = request.GET['kode']
	q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,HPOKOK,SUPPLIER_ID,B.NAME_SUPPL "
	q +=" FROM BARANG A LEFT JOIN SUPPLIER B ON  A.SUPPLIER_ID=B.SUPPLIERC where BARANGC= %s order by BARANGC"
	result = Globals().getDataQuery(q, [kode])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getDataBarang(request):
	nama = '%'+request.GET['nama']+'%'
	if nama == 'nullnone0':
		result = []
		json_data = json.dumps(result, cls=DjangoJSONEncoder)
		return HttpResponse(json_data, content_type="application/json")
	else:
		q = "SELECT A.BARANGC,NAME_BRG,SATSTAND,HPOKOK,SUPPLIER_ID,B.NAME_SUPPL FROM BARANG A LEFT JOIN SUPPLIER B ON  A.SUPPLIER_ID=B.SUPPLIERC where AKTIF<>1 and name_brg like %s order by NAME_BRG"
		result = Globals().getDataQuery(q, [nama])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getsupplier(request):
	q = "SELECT SUPPLIERC, NAME_SUPPL "
	q += "FROM SUPPLIER  "
	q += "ORDER BY SUPPLIERC "
	result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getidsupplier(request):
	kode = request.GET['kode']
	q = " SELECT SUPPLIERC, NAME_SUPPL " 
	q +=" FROM SUPPLIER "
	q += "where SUPPLIERC = %s  "
	result = Globals().getDataQuery(q, [kode])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def SP_AUD_SALDO(request):
	# DETAIL
	FDETNO = json.loads(request.POST['FDETNO'])
	FDET_BARANG = json.loads(request.POST['FDET_BARANG'])
	FDET_BARANGN = json.loads(request.POST['FDET_BARANGN'])
	FDET_SUPP = json.loads(request.POST['FDET_SUPP'])
	FDET_SUPPN = json.loads(request.POST['FDET_SUPPN'])
	FDET_SATUAN = json.loads(request.POST['FDET_SATUAN'])
	FDET_HPOKOK = json.loads(request.POST['FDET_HPOKOK'])
	FDET_QTY = json.loads(request.POST['FDET_QTY'])
	# MAIN EXEC
	FHEADBUKTI_ID = request.POST['FHEADBUKTI_ID']
	FHEADDATE = request.POST['FHEADDATE']
	FHEADWHID = request.POST['FHEADWHID']
	USERRS = request.session['user_id']
	UPDATERS = ''
	ID_CABANG = request.session['kdCabang']
	StatusAUD = request.POST['StatusAUD']
	q = "SET NOCOUNT ON;"
	q += "DECLARE @LIST_GRID FJINKOTAD;"
	q += "DECLARE @NOW datetime; "
	q += "SET @NOW = GETDATE(); "
	i = 0
	for x in FDETNO:
		q += "INSERT INTO @LIST_GRID (FDFJNOM, FDFJBRG_ID, FDFJBRGN, FDFJPRD_ID, FDFJSATUAN, FDFJHJUAL,FDFJQTY) "
		q += "VALUES ("
		q += FDETNO[i] + ","
		q += "'" + FDET_BARANG[i] + "',"
		q += "'" + FDET_BARANGN[i] + "',"
		q += "'" + FDET_SUPP[i] + "',"
		q += "'" + FDET_SATUAN[i] + "',"
		q += FDET_HPOKOK[i] + ","
		q += FDET_QTY[i] + ");"
		i += 1

	q += "EXEC FRM_AUD_SALDO_PERSEDIAAN "
	q += "'" + FHEADBUKTI_ID + "',"
	q += "'" + FHEADDATE + "',"
	q += "'" + FHEADWHID + "',"
	q += "'" + USERRS + "',"
	q += "@NOW,"
	q += "'" + ID_CABANG + "',"
	q += "'" + StatusAUD + "',"
	q += "@LIST_GRID,"
	q += "''"
	result = Globals().getDataSP(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def load_saldorekening(request):
	no_bukti = '%'+request.GET['no_bukti']+'%'
	supplier = '%'+request.GET['supplier']+'%'
	saldo_gudang = '%'+request.GET['saldo_gudang']+'%'
	tipe = request.GET['tipe']
	tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")
	ID_CABANG = request.session['kdCabang']
	if(tipe == 'saldo_by_bulan'):
		q = "SELECT distinct top 100 BBBULAN, BBDATE, BBSUPP_ID, BBUSERS, BBUPDATE, BBWH_ID,b.NAME_SUPPL,c.NAME_WH "
		q += "FROM BBALINV as a inner join  "
		q += "SUPPLIER as b on a.BBSUPP_ID=b.SUPPLIERC  inner join   "
		q += "WAREHOUSE as c on a.BBWH_ID=c.WH_ID  "
		q += "where (a.BBBULAN like %s) and (b.NAME_SUPPL like %s)  and  "
		q += "(c.NAME_WH like %s) and (YEAR(BBDATE) = %s) and (MONTH(BBDATE) = %s) and ID_CABANG= %s "
		result = Globals().getDataQuery(q, [no_bukti, supplier, saldo_gudang, tanggal.year, tanggal.month,ID_CABANG])
	else:
		q = "SELECT distinct top 100 BBBULAN, BBDATE, BBSUPP_ID, BBUSERS, BBUPDATE, BBWH_ID,b.NAME_SUPPL,c.NAME_WH "
		q += "FROM BBALINV as a inner join  "
		q += "SUPPLIER as b on a.BBSUPP_ID=b.SUPPLIERC  inner join   "
		q += "WAREHOUSE as c on a.BBWH_ID=c.WH_ID  "
		q += "where (a.BBBULAN like %s) and (b.NAME_SUPPL like %s)  and  "
		q += "(c.NAME_WH like %s) and BBDATE = %s and ID_CABANG= %s "
		result = Globals().getDataQuery(q, [no_bukti, supplier, saldo_gudang, tanggal,ID_CABANG])
	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getsaldoByBukti(request):
	no_bukti = request.GET['no_bukti']
	ID_CABANG = request.session['kdCabang']
	q ="SELECT ROW_NUMBER() OVER (ORDER BY NAME_BRG) AS NO, BBBULAN, BBDATE, BBSUPP_ID as KODE_SUPP, BBUSERS, BBUPDATE, BBWH_ID,BBQTY_HPOKOK as HARGA_POKOK,BBQTY_SAWAL as QTY,b.NAME_SUPPL as NAME_SUPPL,c.NAME_WH, "
	q += "d.BARANGC as ID_BARANG,d.NAME_BRG as NAMA_BARANG,d.SATSTAND as SATUAN "
	q += "FROM BBALINV as a inner join  "
	q += "SUPPLIER as b on a.BBSUPP_ID=b.SUPPLIERC  inner join  "
	q += "WAREHOUSE as c on a.BBWH_ID=c.WH_ID inner join  "
	q += "BARANG as d on a.BBBRG_ID=d.BARANGC "
	q += "where (a.BBBULAN = %s) and ID_CABANG= %s order by NAME_BRG,BBWH_ID "
	result = Globals().getDataQuery(q, [no_bukti,ID_CABANG])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetaksaldo(request):
	nomor = request.GET['no_bukti']
	tanggal_waktu_cetak = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pdf_file = Globals().generateReportDB(
		"mutasi_saldofrm.jrxml", 
		'mutasi_saldofrm', 
		user,
		{
			'nomor': nomor,
			'nama_rs':  request.session['nama_cabang'],
			'tanggal_waktu_cetak': Globals().tanggalIndo(tanggal_waktu_cetak),
		} 
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")