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

def frm_beli(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_beli")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_beli", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_beli", '1')
		menubarCount = len(menubars)
		response = render(request, 'farmasi/beli/pembelian.html', {
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
def getSupplier(request):
	kode = request.GET['kode']
	tipe = request.GET['tipe']
	if(tipe == 'supplier'):
		q = "select * from SUPPLIER WHERE SUPPLIERC= %s ORDER BY SUPPLIERC"
		result = Globals().getDataQuery(q,[kode])
	else:	
		q = "select * from SUPPLIER"
		result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getPabrikan(request):
	kode = request.GET['kode']
	tipe = request.GET['tipe']
	if(tipe == 'Pabrikan'):
		q = "select * from Pabrikan WHERE FMPSUPPLIERC= %s ORDER BY FMPSUPPLIERC"
		result = Globals().getDataQuery(q,[kode])
	else:	
		q = "select * from Pabrikan"
		result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getTpay(request):
	kode = request.GET['kode']
	tipe = request.GET['tipe']
	if(tipe == 'tpay'):
		q = "SELECT tpay_id AS KODE, nama AS NAMA_MERK, KREDIT FROM TPAY WHERE tpay_id= %s ORDER BY tpay_id "
		result = Globals().getDataQuery(q,[kode])
	else:
		q = "SELECT tpay_id AS KODE, nama AS NAMA_MERK, KREDIT FROM TPAY ORDER BY tpay_id "
		result = Globals().getDataQuery(q)
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getdivisi(request):
	
	tipe = request.GET['tipe']
	if(tipe == 'Divisi'):
		kode = request.GET['kode']
		q = "SELECT WH_ID, NAME_WH "
		q += "FROM WAREHOUSE  "
		q += "WHERE (WH_ID LIKE %s) AND aktif=1 "
		result = Globals().getDataQuery(q,[kode])
	else:
		kode_divisi = '%'+request.GET['search_kode_divisi']+'%'
		nama_divisi = '%'+request.GET['search_nama_divisi']+'%'
		q = "SELECT WH_ID, NAME_WH "
		q += "FROM WAREHOUSE  "
		q += "WHERE (WH_ID LIKE %s) AND (NAME_WH LIKE %s)  AND aktif=1  "
		result = Globals().getDataQuery(q, [kode_divisi,nama_divisi])
	
	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	
	return HttpResponse(json_data, content_type="application/json")

def getIdDataBarang(request):
	
	kode = request.GET['kode']
	if len(kode)==0:
		q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,HPOKOK,TTYPEC  "
		q +=" FROM BARANG A  where AKTIF<>1 and BARANGC=%s  order by BARANGC "
		result = Globals().getDataQuery(q, [kode])
	else:
		q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,HPOKOK,TTYPEC  "
		q +=" FROM BARANG A  where AKTIF<>1 and BARANGC=%s or BARCODE=%s order by BARANGC "
		result = Globals().getDataQuery(q, [kode,kode])


	
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

def getPembelianByBuktiPembelian(request):
	
	no_bukti = request.GET['no_bukti']
	# pprint(no_bukti)
	q = "select a.*, b.FDFBNOM as NO, b.FDFBPRD_ID as ID_PRODUK, b.FDFBBRG_ID as ID_BARANG, "
	q += "b.FDFBBRGN as NAMA_BARANG, b.FDFBSATUAN as SATUAN, b.FDFBHPOKOK as HARGA_POKOK, "
	q += "b.FDFBQTYT as QTY, b.FDFBDISC1 as DISC_1, b.FDFBDISC2 as DISC_2, b.FDFBDISC3 as DISC_RP, "
	q += "b.FDFBTOTAL as TOTAL "
	q += "from FBELI a inner join FBELID b on a.FHFBBUKTI_ID = b.FDFBBUKTI_ID "
	q += "where a.FHFBBUKTI_ID = %s order by b.FDFBNOM "
	result = Globals().getDataQuery(q, [no_bukti])
	
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

def SP_AUD_BELI(request):
	
	# DETAIL
	FDFBNOM = json.loads(request.POST['FDFBNOM'])
	FDFBPRD_ID = json.loads(request.POST['FDFBPRD_ID'])
	FDFBBRG_ID = json.loads(request.POST['FDFBBRG_ID'])
	FDFBBRGN = json.loads(request.POST['FDFBBRGN'])
	FDFBSATUAN = json.loads(request.POST['FDFBSATUAN'])
	FDFBHPOKOK = json.loads(request.POST['FDFBHPOKOK'])
	FDFBQTYT = json.loads(request.POST['FDFBQTYT'])
	FDFBDISC1 = json.loads(request.POST['FDFBDISC1'])
	FDFBDISC2 = json.loads(request.POST['FDFBDISC2'])
	FDFBDISC3 = json.loads(request.POST['FDFBDISC3'])
	FDFBTOTAL = json.loads(request.POST['FDFBTOTAL'])
	FDFBBUKTI_ID = json.loads(request.POST['FDFBBUKTI_ID'])
	FDFBSUPPL_ID = json.loads(request.POST['FDFBSUPPL_ID'])
	FDFBTGL_EXPIRED = json.loads(request.POST['FDFBTGL_EXPIRED'])
	FDFBVALIDASI = json.loads(request.POST['FDFBVALIDASI'])
	FDFBKONVERSI = json.loads(request.POST['FDFBKONVERSI'])
	FDFBSATUANSTD = json.loads(request.POST['FDFBSATUANSTD'])
	FDFBKERJASAMA = json.loads(request.POST['FDFBKERJASAMA'])
	FDFBBATHNO = json.loads(request.POST['FDFBBATHNO'])

	# MAIN EXEC
	FHFBBUKTI_ID = request.POST['FHFBBUKTI_ID']
	FHFBDATE = request.POST['FHFBDATE']
	FHFBSUPPL_ID = request.POST['FHFBSUPPL_ID']
	FHFBTPAY_ID = request.POST['FHFBTPAY_ID']
	FHFBWH_ID = request.POST['FHFBWH_ID']
	FHFBDATE_TEMPO = request.POST['FHFBDATE_TEMPO']
	FHFBREMARK = request.POST['FHFBREMARK']
	FHFBDPP = request.POST['FHFBDPP']
	FHFBPPNPERCENT = request.POST['FHFBPPNPERCENT']
	FHFBPPN = request.POST['FHFBPPN']
	FHFBADM = request.POST['FHFBADM']
	FHFBJUMLAH = request.POST['FHFBJUMLAH']
	FHFBUSERS = request.session['user_id']
	FHFBUPDATE = ''
	FHFBTAX = request.POST['FHFBTAX']
	FHFBTAXDATE = request.POST['FHFBTAXDATE']
	FHFBEXPIRE = request.POST['FHFBEXPIRE']
	FHFBLPB = request.POST['FHFBLPB']
	FHFBSP = request.POST['FHFBSP']
	FKUNCIBPJS = request.POST['FKUNCIBPJS']
	StatusAUD = request.POST['StatusAUD']

	q = "DECLARE @LIST_RESEP FBELID;"
	q += "DECLARE @NOW datetime; "
	q += "SET @NOW = GETDATE(); "

	proc_param = []
	i = 0
	for x in FDFBNOM:
		q += "INSERT INTO @LIST_RESEP (FDFBNOM, FDFBPRD_ID, FDFBBRG_ID, FDFBBRGN, FDFBSATUAN, FDFBHPOKOK, FDFBQTYT, FDFBDISC1, FDFBDISC2, FDFBDISC3, FDFBTOTAL, FDFBBUKTI_ID, FDFBSUPPL_ID, FDFBTGL_EXPIRED, FDFBVALIDASI, FDFBKONVERSI, FDFBSATUANSTD, FDFBKERJASAMA, FDFBBATHNO) "
		q += "VALUES ("
		q += FDFBNOM[i] + ","
		q += "'" + FDFBPRD_ID[i] + "',"
		q += "'" + FDFBBRG_ID[i] + "',"
		q += "%s,"
		q += "'" + FDFBSATUAN[i] + "',"
		q += FDFBHPOKOK[i] + ","
		q += FDFBQTYT[i] + ","
		q += FDFBDISC1[i] + ","
		q += FDFBDISC2[i] + ","
		q += FDFBDISC3[i] + ","
		q += FDFBTOTAL[i] + ","
		q += "'" + FDFBBUKTI_ID[i] + "',"
		q += "'" + FDFBSUPPL_ID[i] + "',"
		q += "'" + FDFBTGL_EXPIRED[i] + "',"
		q += FDFBVALIDASI[i] + ","
		q += FDFBKONVERSI[i] + ","
		q += "'" + FDFBSATUANSTD[i] + "',"
		q += FDFBKERJASAMA[i] + ","
		q += "'" + FDFBBATHNO[i] + "');"
		proc_param.extend([FDFBBRGN[i]])
		i += 1

	

	q += "EXEC FRM_AUD_FBELI "
	q += "'" + FHFBBUKTI_ID + "',"
	q += "'" + FHFBDATE + "',"
	q += "'" + FHFBSUPPL_ID + "',"
	q += "'" + FHFBTPAY_ID + "',"
	q += "'" + FHFBWH_ID + "',"
	q += "'" + FHFBDATE_TEMPO + "',"
	q += "'" + FHFBREMARK + "',"
	q += "'" + FHFBDPP + "',"
	q += "'" + FHFBPPNPERCENT + "',"
	q += "'" + FHFBPPN + "',"
	q += "'" + FHFBADM + "',"
	q += "'" + FHFBJUMLAH + "',"
	q += "'" + FHFBUSERS + "',"
	q += "@NOW,"
	q += "'" + FHFBTAX + "',"
	q += "'" + FHFBTAXDATE + "',"
	q += "'" + FHFBEXPIRE + "',"
	q += "'" + FHFBLPB + "',"
	q += "'" + FHFBSP + "',"
	q += "'" + FKUNCIBPJS + "',"
	q += "'" + StatusAUD + "',"
	q += "@LIST_RESEP,"
	q += "''"

	if (StatusAUD=='D') :
		user = {
		'user_id': request.session['user_id'],
		'user_name': request.session['user_name'],
		'user_priv': request.session['user_priv'],
		}
		data = []
		data.append({"query": "select * from FBELI where FHFBBUKTI_ID = '" + FHFBBUKTI_ID + "'"})
		data.append({"query": "select * from FBELID where FDFBBUKTI_ID = '" + FHFBBUKTI_ID + "'"})
		Globals().create_log('Hapus LogDelete.txt', 'FARMASI', data, user)
	
	
	# print (q % tuple(proc_param))
	result = Globals().getDataQuery(q,proc_param)
	
	
	result = None
	while result is None:
		try:
			result = cursor.fetchall()
			break
		except ProgrammingError as e:
			cursor.nextset()

	if result[0][0] != 0:
		json_data = json.dumps({'status':'gagal', 'data':result[0][1]}, cls=DjangoJSONEncoder)
	else:
		json_data = json.dumps({'status':'sukses', 'data':result[0][1]}, cls=DjangoJSONEncoder)
		
	
	return HttpResponse(json_data, content_type="application/json")

def getPembelian(request):
	
	no_bukti = '%'+request.GET['no_bukti']+'%'
	supplier = '%'+request.GET['supplier']+'%'
	gudang = '%'+request.GET['gudang']+'%'
	tipe = request.GET['tipe']
	tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")

	if(tipe == 'pembelian_by_bulan'):
		q = "select top 100 a.*, b.NAME_SUPPL, c.NAME_WH, convert(varchar, a.FHFBDATE, 23) as TANGGAL,FHFBJUMLAH "
		q += "from FBELI a inner join SUPPLIER b on a.FHFBSUPPL_ID = b.SUPPLIERC "
		q += "inner join WAREHOUSE c on a.FHFBWH_ID = c.WH_ID "
		q += "where (a.FHFBBUKTI_ID like %s) and (b.NAME_SUPPL like %s) and "
		q += "(c.NAME_WH like %s) and (YEAR(FHFBDATE) = %s) and (MONTH(FHFBDATE) = %s) "
		result = Globals().getDataQuery(q, [no_bukti, supplier, gudang, tanggal.year, tanggal.month])
	else:
		q = "select top 100 a.*, b.NAME_SUPPL, c.NAME_WH, convert(varchar, a.FHFBDATE, 23) as TANGGAL,FHFBJUMLAH "
		q += "from FBELI a inner join SUPPLIER b on a.FHFBSUPPL_ID = b.SUPPLIERC "
		q += "inner join WAREHOUSE c on a.FHFBWH_ID = c.WH_ID "
		q += "where (a.FHFBBUKTI_ID like %s) and (b.NAME_SUPPL like %s) and "
		q += "(c.NAME_WH like %s) and FHFBDATE = %s"
		result = Globals().getDataQuery(q, [no_bukti, supplier, gudang, tanggal])

	
	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getBarangByBuktiPembelian(request):
	
	no_bukti = request.GET['no_bukti']

	q = "select a.*, b.FDFBNOM as NO, b.FDFBPRD_ID as ID_PRODUK, b.FDFBBRG_ID as ID_BARANG, "
	q += "b.FDFBBRGN as NAMA_BARANG, b.FDFBSATUAN as SATUAN, b.FDFBHPOKOK as HARGA_POKOK, "
	q += "b.FDFBQTYT as QTY_BELI,b.FDFBQTYT as QTY, b.FDFBDISC1 as DISC_1, b.FDFBDISC2 as DISC_2, b.FDFBDISC3 as DISC_RP, "
	q += "b.FDFBTOTAL as TOTAL, IIF(b.FDFBTGL_EXPIRED = '1900-01-01', null, b.FDFBTGL_EXPIRED) as TGL_EXPIRED, "
	q += "b.FDFBKONVERSI as KONVERSI, b.FDFBSATUANSTD as SATSTAND, IIF(b.FDFBKERJASAMA = 0, 'Non', 'KRSM') as KRSM, b.FDFBBATHNO as NO_BATCH "
	q += "from FBELI a inner join FBELID b on a.FHFBBUKTI_ID = b.FDFBBUKTI_ID "
	q += "where a.FHFBBUKTI_ID = %s order by b.FDFBNOM "
	result = Globals().getDataQuery(q, [no_bukti])
	
	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetakPembelian(request):
	
	cursor2 = connection.cursor()
	
	nama_rs = ''
	nomor = request.POST['nomor']
	lpb = request.POST['lpb']
	nama_supplier = request.POST['nama_supplier']
	nama_gudang = request.POST['nama_gudang']
	keterangan = request.POST['keterangan']
	tanggal_faktur_beli = request.POST['tanggal_faktur_beli']
	sistem_pembayaran = request.POST['sistem_pembayaran']
	tanggal_jatuh_tempo = request.POST['tanggal_jatuh_tempo']
	nama_user = request.session['user_name']
	dasar_pengenaan_pajak = request.POST['dasar_pengenaan_pajak']
	ppn_persen = request.POST['ppn_persen']
	ppn_hasil = request.POST['ppn_hasil']
	total = request.POST['total']
	materai_adm = request.POST['materai_adm']
	netto = request.POST['netto']
	pilihcetak=request.POST['pilihcetak']
	no_po=request.POST['no_so']

	# q = 'update FBELI set FKUNCIREGRISTASI = 1, FHFBTGL_REGRISTASI = GETDATE() '
	# q += 'where FHFBBUKTI_ID = %s and FHFBLPB = %s'
	# result = Globals().getDataQuery(q, [nomor, lpb])

	qcabang = "select * from CABANG"
	cursor2.execute(qcabang)
	cabang = Globals().dictfetchall(cursor2)

	nomor_nama_file = nomor.replace("/", "-")
	nomor_nama_file = nomor.replace("\\", "-")
	nomor_nama_file = nomor.replace(":", "-")
	nomor_nama_file = nomor.replace("*", "-")
	nomor_nama_file = nomor.replace("?", "-")
	nomor_nama_file = nomor.replace("\"", "-")
	nomor_nama_file = nomor.replace("\"", "-")
	nomor_nama_file = nomor.replace("<", "-")
	nomor_nama_file = nomor.replace(">", "-")
	nomor_nama_file = nomor.replace("|", "-")

	user = request.session['user_id']
	

	pdf_file = Globals().generateReportDB(
		'faktur_pembelian.jrxml',
		'faktur_pembelian', 
		user,
		{
			'nama_rs': cabang[0]['PERUSAHAAN'],
			'no_faktur_beli': nomor,
			'nama_supplier': nama_supplier,
			'nama_gudang': nama_gudang,
			'keterangan': keterangan,
			'tanggal_faktur_beli': dateIndo(tanggal_faktur_beli),
			'sistem_pembayaran': sistem_pembayaran,
			'tanggal_jatuh_tempo': dateIndo(tanggal_jatuh_tempo),
			'nama_user': nama_user,
			'dasar_pengenaan_pajak': dasar_pengenaan_pajak,
			'ppn_persen': ppn_persen + ' %',
			'ppn_hasil': ppn_hasil,
			'total': total,
			'materai_adm': materai_adm,
			'netto': netto,
			'no_po': no_po,
			'lpb': lpb,
		},
		list_format=[pilihcetak]
	)

	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	
	cursor2.close()
	return HttpResponse(json_data, content_type="application/json")

def getvalidasiPembelian(request):
	
	tipe = request.GET['tipe']
	tanggalawal = datetime.strptime(request.GET['tanggalawal'], "%Y-%m-%d")
	tanggalakhir = datetime.strptime(request.GET['tanggalakhir'], "%Y-%m-%d")
	
	if(tipe == 'mutasi_by_all'):
		q = "SELECT TOP (100)  FBELI. FHFBBUKTI_ID,  FBELI. FHFBDATE,  FBELI.   FHFBSUPPL_ID,  FBELI. FHFBJUMLAH,  SUPPLIER.NAME_SUPPL, " 
		q +="CONVERT(varchar, FBELI. FHFBDATE, 23) AS TANGGAL "
		q +="from  FBELI INNER JOIN    SUPPLIER ON  FBELI.   FHFBSUPPL_ID =  SUPPLIER.SUPPLIERC "
		q +="where ( FHFBDATE >= %s) and "
		q += "( FHFBDATE <= %s) "
		result = Globals().getDataQuery(q, [tanggalawal, tanggalakhir])
	elif (tipe == 'mutasi_by_belum'):
		q = "SELECT TOP (100)  FBELI. FHFBBUKTI_ID,  FBELI. FHFBDATE,  FBELI.   FHFBSUPPL_ID,  FBELI. FHFBJUMLAH,  SUPPLIER.NAME_SUPPL, " 
		q +="CONVERT(varchar, FBELI. FHFBDATE, 23) AS TANGGAL "
		q +="from  FBELI INNER JOIN    SUPPLIER ON  FBELI.   FHFBSUPPL_ID =  SUPPLIER.SUPPLIERC "
		q +="where ( FHFBDATE >= %s) and "
		q += "( FHFBDATE <= %s) and isnull(FKUNCI,0)=0 "
	else :
		q = "SELECT TOP (100)  FBELI. FHFBBUKTI_ID,  FBELI. FHFBDATE,  FBELI.   FHFBSUPPL_ID,  FBELI. FHFBJUMLAH,  SUPPLIER.NAME_SUPPL, " 
		q +="CONVERT(varchar, FBELI. FHFBDATE, 23) AS TANGGAL "
		q +="from  FBELI INNER JOIN    SUPPLIER ON  FBELI.   FHFBSUPPL_ID =  SUPPLIER.SUPPLIERC "
		q +="where ( FHFBDATE >= %s) and "
		q += "( FHFBDATE <= %s) and fkunci=1 "

	result = Globals().getDataQuery(q, [tanggalawal, tanggalakhir])

	
	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def SPPerubahanfaktur(request):
	
	users = request.POST['users']
	updaters = request.POST['updaters']
	No_faktur_baru = request.POST['No_faktur_baru']
	No_faktur_lama = request.POST['No_faktur_lama']
	# dgn Store procedure
	q = "exec FRM_UPDATEFAKTUR_BELI  %s, %s, %s, %s "
	result = Globals().getDataQuery(q, [No_faktur_baru, No_faktur_lama, users, updaters])
	result = cursor.fetchall()
	json_data = json.dumps({'pesan':'ok'}, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def SPValidasiMutasi(request):
	
	users = request.POST['users']
	updaters = request.POST['updaters']
	No_faktur = request.POST['No_faktur']

	q = "UPDATE  FBELI  SET FKUNCI = 1 WHERE   FHFBBUKTI_ID = %s"
	result = Globals().getDataQuery(q, [No_faktur])
	json_data = json.dumps({"pesan":"Berhasil Di validasi"}, cls=DjangoJSONEncoder)
	
	return HttpResponse(json_data, content_type="application/json")

def UNSPValidasiMutasi(request):
	
	users = request.POST['users']
	updaters = request.POST['updaters']
	No_faktur = request.POST['No_faktur']

	q = "UPDATE  FBELI  SET FKUNCI = 0 WHERE   FHFBBUKTI_ID = %s"
	result = Globals().getDataQuery(q, [No_faktur])
	json_data = json.dumps({"pesan":"Berhasil Di Batalkan"}, cls=DjangoJSONEncoder)
	
	return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap_supplier(request):
	start = request.GET['start']
	finish = request.GET['finish']
	dariSupp = request.GET['dariSupp']
	sdSupp = request.GET['sdSupp']

	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pilihcetak=request.GET['pilihcetak']
	# proses cetak
	# print(finish) 
	pdf_file = Globals().generateReportDB(
		"beli_frm02.jrxml", 
		'beli_frm02', 
		user,
		{
			'start': start,
			'finish': finish,
			'dariSupp': dariSupp,
			'sdSupp': sdSupp,
			'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
		},
		list_format=[pilihcetak]
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap(request):
	start = request.GET['start']
	finish = request.GET['finish']
	dariSupp = request.GET['dariSupp']
	sdSupp = request.GET['sdSupp']

	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pilihcetak=request.GET['pilihcetak']
	# proses cetak
	# print(finish) 
	pdf_file = Globals().generateReportDB(
		"beli_frm03.jrxml", 
		'beli_frm03', 
		user,
		{
			'start': start,
			'finish': finish,
			'dariSupp': dariSupp,
			'sdSupp': sdSupp,
			'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
		},
		list_format=[pilihcetak]
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_lap_Pembelian(request):
	start = request.GET['start']
	finish = request.GET['finish']
	dariSupp = request.GET['dariSupp']
	sdSupp = request.GET['sdSupp']

	tanggal = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	pilihcetak=request.GET['pilihcetak']
	# proses cetak
	# print(finish) 
	pdf_file = Globals().generateReportDB(
		"faktur_pembelian002.jrxml", 
		'faktur_pembelian002', 
		user,
		{
			'start': start,
			'finish': finish,
			'dariSupp': dariSupp,
			'sdSupp': sdSupp,
			'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
		},
		list_format=[pilihcetak]
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def cetak_supp_pabrik_gudang(request):
	
	start = request.GET['start']
	finish = request.GET['finish']
	dariSupp = request.GET['dariSupp']
	sdSupp = request.GET['sdSupp']
	dariPabrikan = request.GET['dariPabrikan']
	sdPabrikan = request.GET['sdPabrikan']
	dariGudang = request.GET['dariGudang']
	sdGudang = request.GET['sdGudang']
	

	q = "select a.FHFBBUKTI_ID as NO_BUKTI,A.FHFBDATE as TANGGAL_TERIMA,A.FHFBEXPIRE AS TANGGAL_BELI,A.FHFBDATE_TEMPO AS TANGGAL_TEMPO,D.NAME_SUPPL AS NAMA_SUPLIER,E.FMPNAME_SUPPL AS PABRIKAN,  "
	q += "f.NAME_WH AS NAMA_GUDANG,g.NAMA as CARA_BAYAR, "
	q += "A.FHFBDPP AS DPP,A.FHFBPPNPERCENT,A.FHFBPPN AS PPN,A.FHFBJUMLAH AS NETTO,A.FHFBLPB as LPB, "
	q += "b.FDFBNOM as NO, b.FDFBPRD_ID as ID_PRODUK, b.FDFBBRG_ID as ID_BARANG,  "
	q += "b.FDFBBRGN as NAMA_BARANG, b.FDFBSATUAN as SATUAN, b.FDFBHPOKOK as HARGA_POKOK,  "
	q += "b.FDFBQTYT as QTY_BELI,b.FDFBQTYT as QTY, b.FDFBDISC1 as DISC_1, b.FDFBDISC2 as DISC_2, b.FDFBDISC3 as DISC_RP,  "
	q += "b.FDFBTOTAL as TOTAL, IIF(b.FDFBTGL_EXPIRED = '1900-01-01', null, b.FDFBTGL_EXPIRED) as TGL_EXPIRED,  "
	q += "b.FDFBKONVERSI as KONVERSI, b.FDFBSATUANSTD as SATSTAND, IIF(b.FDFBKERJASAMA = 0, 'Non', 'KRSM') as KRSM, b.FDFBBATHNO as NO_BATCH  "
	q += "from FBELI a inner join FBELID b on a.FHFBBUKTI_ID = b.FDFBBUKTI_ID  "
	q += "inner join BARANG c on b.FDFBBRG_ID=c.BARANGC "
	q += "left join SUPPLIER d on a.FHFBSUPPL_ID =d.SUPPLIERC "
	q += "left join PABRIKAN e on c.PABRIKAN=e.FMPSUPPLIERC  and c.PABRIKAN>=%s and c.PABRIKAN<=%s "
	q += "inner join WAREHOUSE f on a.FHFBWH_ID=f.WH_ID "
	q += "left join TPAY g on a.FHFBTPAY_ID=g.TPAY_ID "
	q += "where a.FHFBDATE>=%s and  a.FHFBDATE<=%s  "
	q += "and a.FHFBSUPPL_ID>=%s and a.FHFBSUPPL_ID<=%s "
	q += "and a.FHFBWH_ID>=%s and a.FHFBWH_ID<=%s "
	q += "order by A.FHFBDATE, A.FHFBBUKTI_ID, b.FDFBNOM"

	result = Globals().getDataQuery(q, [dariPabrikan,sdPabrikan,start,finish,dariSupp,sdSupp,dariGudang,sdGudang])
	
	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getOrder_Pembelian(request):
	
	no_bukti = '%'+request.GET['no_bukti']+'%'
	supplier = '%'+request.GET['supplier']+'%'
	tipe = request.GET['tipe']
	tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")

	if(tipe == 'order_pembelian_by_bulan'):
		q = "select top 100 a.*, b.NAME_SUPPL, convert(varchar, a.FHPOTGL, 23) as TANGGAL "
		q += "from H_POB a inner join SUPPLIER b on a. FHPOSUPP_ID = b.SUPPLIERC "
		q += "where (a.FHPOBUKTI_ID like %s) and (b.NAME_SUPPL like %s) and FKUNCI=1 and ISNULL(FCLOSE,0)<>1 and "
		q += "(YEAR(FHPOTGL) = %s) and (MONTH(FHPOTGL) = %s) "
		result = Globals().getDataQuery(q, [no_bukti, supplier, tanggal.year, tanggal.month])
	else:
		q = "select top 100 a.*, b.NAME_SUPPL, convert(varchar, a.FHPOTGL, 23) as TANGGAL "
		q += "from H_POB a inner join SUPPLIER b on a. FHPOSUPP_ID = b.SUPPLIERC "
		q += "where (a.FHPOBUKTI_ID like %s) and (b.NAME_SUPPL like %s) and FKUNCI=1 and ISNULL(FCLOSE,0)<>1 and  "
		q += "FHPOTGL = %s"
		result = Globals().getDataQuery(q, [no_bukti, supplier, tanggal])


	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getorderBarangByBuktiPembelian(request):
	
	no_bukti = request.GET['no_bukti']
	databukti=no_bukti.split(',')
	q = "select a.*,ROW_NUMBER() OVER (ORDER BY b.FDPOBUKTI_ID,b.FDPONO) AS NO , b.FDPOBRG_ID as ID_BARANG, "
	q += "b.FDPOBRGN as NAMA_BARANG, b.FDPOSATUAN as SATUAN, b.FDPOHARGA as HARGA_POKOK, "
	q += "b.FDPOQTY as QTY, b.FDPODISC1 as DISC_1, b.FDPODISC2 as DISC_2, b.FDPODISC3 as DISC_RP, "
	q += "b.FDPOTOTAL as TOTAL, "
	q += "(select kstandart from BARANG d where d.BARANGC= b.FDPOBRG_ID and d.satkecil= b.FDPOSATUAN "
	q += "union select KSTANDART*KKECIL as KONVERSI from BARANG e where e.BARANGC= b.FDPOBRG_ID and e.satkemas= b.FDPOSATUAN "
	q += "union select 1 as KONVERSI from BARANG F where F.BARANGC= b.FDPOBRG_ID and F.SATSTAND= b.FDPOSATUAN) as KONVERSI, "
	q += "c.SATSTAND  as SATSTAND "
	q += "from H_POB a inner join D_POB b on a.FHPOBUKTI_ID = b.FDPOBUKTI_ID "
	q += "inner join BARANG c on b.FDPOBRG_ID=c.barangc "
	q += "inner join SUPPLIER d on a.FHPOSUPP_ID=d.SUPPLIERC "
	q += "where a.FHPOBUKTI_ID in(  "
	i=0
	for x in databukti:
		if i==0:
			q +="'"+ x +"'"
		else :
			q +=",'"+ x +"'"
		i+=1

	q += ") order by FDPONO "

	result = Globals().getDataQuery(q)
	
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	
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

def format_rupiah(angka, with_prefix=False, desimal=0):
    locale.setlocale(locale.LC_NUMERIC, 'ENG')
    rupiah = locale.format_string("%.*f", (desimal, angka), True)
    if with_prefix:
        return "Rp. {}".format(rupiah)
    return rupiah

