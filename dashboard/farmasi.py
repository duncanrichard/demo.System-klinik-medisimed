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


def farmasi(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "farmasi")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "farmasi", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "farmasi", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/farmasi/base.html', {
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

def getPasien(request):
    today = datetime.today().strftime('%Y-%m-%d')
    search_name = '%'+request.GET['search_name']+'%'
    search_almt = '%'+request.GET['search_almt']+'%'
    search_kdpas = '%'+request.GET['search_kdpas']+'%'
    search_telp = '%'+request.GET['search_telp']+'%'
    tanggal = request.GET['tanggal']
    pilihan = request.GET['pilihan']
    cabang_id = request.session['kdCabang']
    if pilihan == 'search_pasien_all':
        q = " select TOP 200 a.KD_PASIEN as KODE_PASIEN,NAMAPASIEN as NAMA_PASIEN,ALAMAT,NAMA_KELUARGA, TELEPON from  PASIEN a where NAMAPASIEN like %s  "
        q += " and ALAMAT like %s and KD_PASIEN like %s AND TELEPON like %s and (KD_ASAL_CABANG= %s)  order by a.NAMAPASIEN "
    elif pilihan == 'search_pasien_today':
        q = "select top 200 a.KPKD_PASIEN as KODE_PASIEN,b.NAMAPASIEN as NAMA_PASIEN,b.ALAMAT,NAMA_KELUARGA, TELEPON, convert(varchar, KPTGL_PERIKSA, 23) as TANGGAL "
        q +="from KUNJUNGANPASIEN a inner join PASIEN b on a.KPKD_PASIEN=b.KD_PASIEN  where  "
        q += "(NAMAPASIEN like %s) and ALAMAT like %s and (KPKD_PASIEN like %s) AND TELEPON like %s  and (KPTGL_PERIKSA = '"+today+"' ) and (a.KD_CABANG = %s) "
    else:
        q = "select top 200 a.KPKD_PASIEN as KODE_PASIEN,b.NAMAPASIEN as NAMA_PASIEN,b.ALAMAT,NAMA_KELUARGA, TELEPON, convert(varchar, KPTGL_PERIKSA, 23) as TANGGAL "
        q +="from KUNJUNGANPASIEN a inner join PASIEN b on a.KPKD_PASIEN=b.KD_PASIEN  where  "
        q += "(NAMAPASIEN like %s) and ALAMAT like %s and (KPKD_PASIEN like %s) AND TELEPON like %s  and (KPTGL_PERIKSA = '"+tanggal+"' ) and (a.KD_CABANG = %s) "
        

    proc_param = [search_name,search_almt,search_kdpas,search_telp,cabang_id]
    # pprint(proc_param)
    result = Globals().getDataQuery(q, proc_param)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataPasien(request):
    kdpas = request.GET['KD_PASIEN']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")
    # CEK RAWAT JALAN
    q = "SELECT  a.KD_PASIEN AS KODE_PASIEN, a.NAMAPASIEN AS NAMA_PASIEN, a.ALAMAT, a.TGL_LAHIR, "
    q += "(SELECT TOP (1) FDDKD_DOKTER "
    q += "FROM   TRANSAKSIDOKTERD AS b "
    q += "WHERE  (FDDNO_TRANSAKSI = i.FTNO_TRANSAKSI)) AS KODE_DOKTER, "
    q += "(SELECT  TOP (1) e.FMDDOKTERN "
    q += "FROM   TRANSAKSIDOKTERD AS c INNER JOIN "
    q += "DOKTER AS e ON c.FDDKD_DOKTER = e.FMDDOKTER_ID "
    q += "WHERE (c.FDDNO_TRANSAKSI = i.FTNO_TRANSAKSI)) AS NAMA_DOKTER, i.KD_RESELER, h.NAMA_RESELER "
    q += "FROM   PASIEN AS a INNER JOIN "
    q += "KUNJUNGANPASIEN AS f ON a.KD_PASIEN = f.KPKD_PASIEN INNER JOIN "
    q += "TRANSAKSIPASIEN AS i on i.FTNO_KUNJUNGAN=f.KPNO_TRANSAKSI  LEFT JOIN "
    q += "RESELER AS h ON h.KD_RESELER = i.KD_RESELER "
    q += "WHERE (KPTGL_PERIKSA= %s  and a.KD_PASIEN = %s) "
    result1 = Globals().getDataQuery(q, [tanggal,kdpas])
	# CEK PASIEN LANGSUNG
    q = "SELECT a.KD_PASIEN AS KODE_PASIEN, a.NAMAPASIEN AS NAMA_PASIEN, a.ALAMAT,a.TGL_LAHIR, "
    q += "c.KD_RESELER,c.NAMA_RESELER  "
    q += "FROM PASIEN AS a LEFT OUTER JOIN  "
    q += "RESELER AS c ON a.KD_RESELER = c.KD_RESELER  "
    q += "WHERE (a.KD_PASIEN = %s ) "
    result3 = Globals().getDataQuery(q, [kdpas])
    data = {
        'data1': result1,
        'data3': result3,
    }
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataDokter(request):
    idDokter=request.GET['search_name']
    cabang_id = request.session['kdCabang']
    q = "select ROW_NUMBER() OVER (ORDER BY FMDDOKTERN) AS NO, a.FMDDOKTER_ID AS ID_DOKTER,FMDDOKTERN AS NAMA_DOKTER from  DOKTER a where FMDDOKTER_ID=%s and KD_CABANG=%s and a.FMDSTATUS='0' order by FMDDOKTERN "
    result = Globals().getDataQuery(q,[idDokter,cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getdokter(request):
    cabang_id = request.session['kdCabang']
    q = "select ROW_NUMBER() OVER (ORDER BY FMDDOKTERN) AS NO, a.FMDDOKTER_ID AS ID_DOKTER,FMDDOKTERN AS NAMA_DOKTER from  DOKTER a where  KD_CABANG=%s and a.FMDSTATUS='0' order by FMDDOKTERN "
    result = Globals().getDataQuery(q,[cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataGudang(request):
    idGudang=request.GET['search_name']
    cabang_id = request.session['kdCabang']
    q = "select ROW_NUMBER() OVER (ORDER BY NAME_WH) AS NO, a.WH_ID AS WH_ID,NAME_WH AS NAME_WH from  WAREHOUSE a where WH_ID=%s and BRANCH=%s and AKTIF=1 order by NAME_WH "
    result = Globals().getDataQuery(q,[idGudang,cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getgudang(request):
    cabang_id = request.session['kdCabang']
    q = "select ROW_NUMBER() OVER (ORDER BY NAME_WH) AS NO, a.WH_ID AS WH_ID,NAME_WH AS NAME_WH from  WAREHOUSE a where  BRANCH=%s and AKTIF=1 order by NAME_WH "
    result = Globals().getDataQuery(q,[cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getIdDataBarang(request):
	kode = request.GET['kode']
	tarifobat= 0
	if len(kode)==0:
		q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,iif(case when %s=1 then DBP "
		q +=" when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end =0,HJUAL,case when %s=1 then DBP  "
		q +=" when %s=2 then HJUALASKIN  when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end) AS HJUAL, "
		q +=" iif(case when %s=1 then DBP "
		q +=" when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end =0,0,case when %s=1 then 1  "
		q +=" when %s=2 then 1  when %s=3 then 1 "
		q +=" when %s=4 then 0 else 0 end) AS STATUS, "
		q +=" TTYPEC,B.STATUSPRODUK  "
		q +=" FROM BARANG A INNER JOIN PRODUKOBAT B ON  A.TTYPEC=B.PRD_ID where AKTIF<>1 and  BARANGC=%s  order by BARANGC "
		result = Globals().getDataQuery(q, [tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,kode])
	else:
		q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,iif(case when %s=1 then DBP "
		q +=" when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end =0,HJUAL,case when %s=1 then DBP  "
		q +=" when %s=2 then HJUALASKIN  when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end) AS HJUAL, "
		q +=" iif(case when %s=1 then DBP "
		q +=" when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end =0,0,case when %s=1 then 1  "
		q +=" when %s=2 then 1  when %s=3 then 1 "
		q +=" when %s=4 then 0 else 0 end) AS STATUS, "
		q +=" TTYPEC,B.STATUSPRODUK  "
		q +=" FROM BARANG A INNER JOIN PRODUKOBAT B ON  A.TTYPEC=B.PRD_ID where AKTIF<>1 and  BARANGC=%s or BARCODE=%s order by BARANGC "
		result = Globals().getDataQuery(q, [tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,kode,kode])
	
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

def getDataBarang(request):
	# nama = '%'+request.GET['nama']+'%'
	nama = request.GET['nama']+'%'
	tarifobat= 0
	gudang = request.GET['kode_gudang']

	if nama == 'nullnone0':
		result = []
		json_data = json.dumps(result, cls=DjangoJSONEncoder)
		return HttpResponse(json_data, content_type="application/json")

	else:
		q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,iif(case when %s=1 then DBP "
		q +=" when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end =0,HJUAL,case when %s=1 then DBP  "
		q +=" when %s=2 then HJUALASKIN  when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end) AS HJUAL, "
		q +=" iif(case when %s=1 then DBP "
		q +=" when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
		q +=" when %s=4 then HPOKOK else hjual end =0,0,case when %s=1 then 1  "
		q +=" when %s=2 then 1  when %s=3 then 1 "
		q +=" when %s=4 then 0 else 0 end) AS STATUS, "
		q +=" TTYPEC,B.STATUSPRODUK,  "
		q += "CAST(((isnull(d.FSBSALDO_AWAL,0)+isnull(d.FSBPEMBELIAN,0)+isnull(d.FSBRPENJUALAN,0)+isnull(d.FSBLAIN_MASUK,0)) - "
		q += "(isnull(d.FSBPENJUALAN,0)+isnull(d.FSBRPEMBELIAN,0)+isnull(d.FSBLAIN_KELUAR,0))) AS INT) AS STOK "
		q +=" FROM BARANG A INNER JOIN PRODUKOBAT B ON  A.TTYPEC=B.PRD_ID "
		q += "left join SALDOBARANG d on a.BARANGC = d.FSBBRG_ID  and d.FSBWH_ID=%s "
		q +=" where AKTIF<>1 and name_brg like %s order by BARANGC "
		
		result = Globals().getDataQuery(q, [tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,tarifobat,gudang,nama])

	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getDiscCustomer(request):
	kode_produk = request.GET['kode_produk']

	q = ' SELECT A.PRODUK_ID,B.NAME_PRD,A.DISC1,A.DISC2  '
	q += ' from DISCCUSTOMER A  INNER JOIN PRODUKOBAT B ON  A.PRODUK_ID=B.PRD_ID  '
	q += ' where PRODUK_ID= %s  order by PRODUK_ID '
	result = Globals().getDataQuery(q,[kode_produk])
	json_data = json.dumps(result, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getParameter(request):
	q = "select * from PARAMETER "
	result = Globals().getDataQuery(q)
	json_data = json.dumps(result[0], cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getHistoryBarang(request):
    kode_barang = request.GET['kode_barang']
    q = "select c.NAME_WH,a.BARANGC, a.NAME_BRG, a.SATSTAND, "
    q += "CAST(((isnull(b.FSBSALDO_AWAL,0)+isnull(b.FSBRPENJUALAN,0)+isnull(b.FSBPEMBELIAN,0)+isnull(b.FSBLAIN_MASUK,0)+isnull(b.FSBRKANVAS,0)) - "
    q += "(isnull(b.FSBPENJUALAN,0)+isnull(b.FSBRPEMBELIAN,0)+isnull(b.FSBLAIN_KELUAR,0)+isnull(b.FSBKANVAS,0))) AS INT) AS STOK "
    q += "from BARANG a left join SALDOBARANG b on "
    q += "a.BARANGC = b.FSBBRG_ID  left join WAREHOUSE c on "
    q += "b.FSBWH_ID=c.WH_ID where a.BARANGC =  %s  "
    result = Globals().getDataQuery(q,[kode_barang])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cekStokBarangFarmasi(request):
	kode = request.GET['kode']
	gudang = request.GET['kode_gudang']

	q = "select a.BARANGC, a.NAME_BRG, a.SATSTAND, a.TTYPEC, "
	q += "CAST(((isnull(b.FSBSALDO_AWAL,0)+isnull(b.FSBRPENJUALAN,0)+isnull(b.FSBPEMBELIAN,0)+isnull(b.FSBLAIN_MASUK,0)+isnull(b.FSBRKANVAS,0)) - "
	q += "(isnull(b.FSBPENJUALAN,0)+isnull(b.FSBRPEMBELIAN,0)+isnull(b.FSBLAIN_KELUAR,0)+isnull(b.FSBKANVAS,0))) AS INT) AS STOK "
	q += "from BARANG a left join SALDOBARANG b on "
	q += "a.BARANGC = b.FSBBRG_ID left join WAREHOUSE c on "
	q += "b.FSBWH_ID=c.wh_id  "
	q += "where a.BARANGC = %s and b.FSBWH_ID=%s"
	result = Globals().getDataQuery(q, [kode,gudang])
	if(len(result) == 0):
		data = {
			'status':'gagal',
			'pesan':'Data Barang Tidak Tersedia',
			'item': None,
		}
	else:
		data = {
			'status':'ok',
			'pesan':'Data Barang Tersedia',
			'item': result[0],
		}

	json_data = json.dumps(data, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def SP_AUD_FJINKOTA(request):
    # DETAIL
    NO = json.loads(request.POST['NO'])
    TTYPEC = json.loads(request.POST['TTYPEC'])
    ID_BARANG = json.loads(request.POST['ID_BARANG'])
    ID_BARANG2 = json.loads(request.POST['ID_BARANG2'])
    NAMA_BARANG = json.loads(request.POST['NAMA_BARANG'])
    SATSTAND = json.loads(request.POST['SATSTAND'])
    HJUAL = json.loads(request.POST['HJUAL'])
    QTY = json.loads(request.POST['QTY'])
    DISC = json.loads(request.POST['DISC'])
    DISC2 = json.loads(request.POST['DISC2'])
    RESEP = json.loads(request.POST['RESEP'])
    TOTAL = json.loads(request.POST['TOTAL'])
    STATUS = json.loads(request.POST['STATUS'])
    HPP = request.POST['HPP']
    BUKTI_ID = request.POST['BUKTI_ID']
    CUST_ID = request.POST['CUST_ID']


    # MAIN EXEC
    FHFJBUKTI_ID = request.POST['FHFJBUKTI_ID']
    FHFJNO_TRANSAKSI = request.POST['FHFJNO_TRANSAKSI']
    FHFJDATE = request.POST['FHFJDATE']
    FHFJRESELER_ID = request.POST['FHFJRESELER_ID']
    FHFJDOKTER_ID = request.POST['FHFJDOKTER_ID']
    FHFJSTATUSOBAT = request.POST['FHFJSTATUSOBAT']
    FHFJCUST_ID = request.POST['FHFJCUST_ID']
    FHFJCUSTN = request.POST['FHFJCUSTN']
    FHFJADDR1 = request.POST['FHFJADDR1']
    FHFJTPAY_ID = request.POST['FHFJTPAY_ID']
    FHFJWH_ID = request.POST['FHFJWH_ID']
    FHFJREMARK = request.POST['FHFJREMARK']
    FHFJBRANCH = request.session['kdCabang']
    FHFJJUMLAH = request.POST['FHFJJUMLAH']
    FHFJRACIK = request.POST['FHFJRACIK']
    FHFJRESEP = request.POST['FHFJRESEP']
    FHFJBULAT = request.POST['FHFJBULAT']
    FHFJTOTAL = request.POST['FHFJTOTAL']
    FHFJBAYAR = request.POST['FHFJBAYAR']
    FHFJTGL_BAYAR = request.POST['FHFJTGL_BAYAR']
    FHFJUSER = request.POST['FHFJUSER']
    FKUNCI = request.POST['FKUNCI']
    FHFJSTSRETUR = request.POST['FHFJSTSRETUR']
    FKUNCIFIFO = request.POST['FKUNCIFIFO']
    FKUNCISTOCK = request.POST['FKUNCISTOCK']
    FHFJCETAKAN = request.POST['FHFJCETAKAN']
    FHFJJENIS = request.POST['FHFJJENIS']
    FHFJJENISTRANSAKSI = request.POST['FHFJJENISTRANSAKSI']
    USERRS = request.POST['USERRS']
    FHFJIURASKES = request.POST['FHFJIURASKES']
    FHFJSTATUS = request.POST['FHFJSTATUS']
    FHFJJUMLAHUANG = request.POST['FHFJJUMLAHUANG']
    StatusAUD = request.POST['StatusAUD']
    FKSMUTASI = request.POST['FKSMUTASI']
    FDFJJENISTARIP = request.POST['FDFJJENISTARIP']

    q = "SET NOCOUNT ON;DECLARE @LIST_FJINKOTAD FJINKOTAD;"
    q += "DECLARE @NOW datetime; "
    q += "SET @NOW = GETDATE(); "

    proc_param = []
    i = 0
    for x in ID_BARANG:
        q += "INSERT INTO @LIST_FJINKOTAD (FDFJNOM, FDFJPRD_ID, FDFJBRG_ID,KDBARANG, FDFJBRGN, FDFJSATUAN, FDFJHJUAL, FDFJQTY, FDFJDISC1, "
        q += "FDFJDISC4, FDFJTOTAL, FDFJHPP, FDFJBUKTI_ID, FDFJCUST_ID, FDFJJENISTARIP, FDFJEMBALAGE) VALUES ("
        q += "'" + NO[i] + "',"
        q += "'" + TTYPEC[i] + "',"
        q += "'" + ID_BARANG[i] + "',"
        q += "'" + ID_BARANG2[i] + "',"
        q += "%s,"
        q += "'" + SATSTAND[i] + "',"
        q += HJUAL[i] + ","
        q += QTY[i] + ","
        q += DISC[i] + ","
        q += DISC2[i] + ","
        q += TOTAL[i] + ","
        q += HPP + ","
        q += "'" + BUKTI_ID + "',"
        q += "'" + CUST_ID + "',"
        q += STATUS[i] + ","
        q += RESEP[i] + ");"
        proc_param.extend([NAMA_BARANG[i]])
        i += 1

    q += "EXEC FRM_AUD_FJINKOTA "
    q += "'" + FHFJBUKTI_ID + "',"
    q += "'" + FHFJNO_TRANSAKSI + "',"
    q += "'" + FHFJDATE + "',"
    q += "'" + FHFJRESELER_ID + "',"
    q += "'" + FHFJDOKTER_ID + "',"
    q += "'" + FHFJSTATUSOBAT + "',"
    q += "'" + FHFJCUST_ID + "',"
    q += " %s,"
    q += "'" + FHFJADDR1 + "',"
    q += "null,"
    q += "'" + FHFJTPAY_ID + "',"
    q += "'" + FHFJWH_ID + "',"
    q += "'" + FHFJREMARK + "',"
    q += "'" + FHFJBRANCH + "',"
    q += FHFJJUMLAH + ","
    q += FHFJRACIK + ","
    q += FHFJRESEP + ","
    q += FHFJBULAT + ","
    q += FHFJTOTAL + ","
    q += FHFJBAYAR + ","
    q += "'" + FHFJTGL_BAYAR + "',"
    q += "'" + FHFJUSER + "',"
    q += "@NOW,"
    q += FKUNCI + ","
    q += "'" + FHFJSTSRETUR + "',"
    q += "'" + FKUNCIFIFO + "',"
    q += "'" + FKUNCISTOCK + "',"
    q += "'" + FHFJCETAKAN + "',"
    q += "null,"
    q += "'" + FHFJJENIS + "',"
    q += "'" + FHFJJENISTRANSAKSI + "',"
    q += "'" + USERRS + "',"
    q += "@NOW,"
    q += FHFJIURASKES + ","
    q += FHFJSTATUS + ","
    q += FHFJJUMLAHUANG + ","
    q += "null,"
    q += "null,"
    q += "null,"
    q += "'" + StatusAUD + "',"
    q += "'" + FKSMUTASI + "',"
    q += FDFJJENISTARIP + ","
    q += "@LIST_FJINKOTAD"
    if (StatusAUD=='D') :
        user = {
        'user_id': request.session['user_id'],
        'user_name': request.session['user_name'],
        'user_priv': request.session['user_priv'],
        }
        data = []
        data.append({"query": "select * from FJINKOTA where FHFJBUKTI_ID = '" + FHFJBUKTI_ID + "'"})
        data.append({"query": "select * from FJINKOTAD where FDFJBUKTI_ID = '" + FHFJBUKTI_ID + "'"})
        Globals().create_log('Hapus LogDelete.txt', 'IMMODERMA', data, user)
        
    proc_param.extend([FHFJCUSTN])
    try:
        print (q)
        result = Globals().getDataSP(q,proc_param)
        print (result)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)