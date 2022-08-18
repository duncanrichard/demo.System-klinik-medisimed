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

def frm_order(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_order")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_order", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_order", '1')
		menubarCount = len(menubars)
		response = render(request, 'farmasi/orderbeli/orderpembelian.html', {
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
    q = "select * from SUPPLIER"
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getTpay(request):
    q = "SELECT tpay_id AS KODE, nama AS NAMA_MERK, KREDIT FROM TPAY ORDER BY tpay_id "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataBarang(request):
    nama = request.GET['nama']+'%'
    if nama == 'nullnone0':
        result = []
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    else:
        q = "select * from BARANG where AKTIF<>1 and  name_brg like %s order by NAME_BRG"
        result = Globals().getDataQuery(q, [nama])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getDataStatus(request):
    kode_barang = request.GET['kode_barang']
    q = "select SATSTAND as SATUAN, 1 as KONVERSI, CAST(Hpokok AS INT) as HARGA_POKOK "
    q += "from BARANG where AKTIF<>1 and BARANGC = %s union "
    q += "select SATKECIL as SATUAN, KSTANDART as KONVERSI, CAST(Hpokok AS INT) * KSTANDART as HARGA_POKOK "
    q += "from BARANG where AKTIF<>1 and BARANGC = %s union "
    q += "select SATKEMAS as SATUAN, (KSTANDART*KKECIL) as KONVERSI, CAST(Hpokok AS INT) * (KSTANDART*KKECIL) as HARGA_POKOK "
    q += "from BARANG where AKTIF<>1 and BARANGC = %s order by KONVERSI"
    result = Globals().getDataQuery(q, [kode_barang, kode_barang, kode_barang])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def SP_AUD_ORDER(request):
    # DETAIL
    FDPONO = json.loads(request.POST['FDPONO'])
    FDPOPRD_ID = json.loads(request.POST['FDPOPRD_ID'])
    FDPOBRG_ID = json.loads(request.POST['FDPOBRG_ID'])
    FDPOBRGN = json.loads(request.POST['FDPOBRGN'])
    FDPOSATUAN = json.loads(request.POST['FDPOSATUAN'])
    FDPOHARGA = json.loads(request.POST['FDPOHARGA'])
    FDPOQTY = json.loads(request.POST['FDPOQTY'])
    FDPODISC1 = json.loads(request.POST['FDPODISC1'])
    FDPODISC2 = json.loads(request.POST['FDPODISC2'])
    FDPODISC3 = json.loads(request.POST['FDPODISC3'])
    FDPOTOTAL = json.loads(request.POST['FDPOTOTAL'])
    # MAIN EXEC
    FHPOBUKTI_ID = request.POST['FHPOBUKTI_ID']
    FHPOTGL = request.POST['FHPOTGL']
    FHPOTGLKIRIM = request.POST['FHPOTGLKIRIM']
    FHPOSUPP_ID = request.POST['FHPOSUPP_ID']
    FHPOTPAY_ID = request.POST['FHPOTPAY_ID']
    FHPOREMARK = request.POST['FHPOREMARK']
    FHPODPP = request.POST['FHPODPP']
    FHPOPPN = request.POST['FHPOPPN']
    FHPOPPNRP = request.POST['FHPOPPNRP']
    FHPOJUMLAH = request.POST['FHPOJUMLAH']
    FHPOUSERS = request.session['user_id']
    ID_CABANG = request.session['kdCabang']
    FHPOUPDATE = ''
    StatusAUD = request.POST['StatusAUD']
    q = "SET NOCOUNT ON;DECLARE @LIST_RESEP ORDERD;"
    q += "DECLARE @NOW datetime; "
    q += "SET @NOW = GETDATE(); "
    proc_param = []
    i = 0
    for x in FDPONO:
        q += "INSERT INTO @LIST_RESEP (FDFBNOM, FDFBPRD_ID, FDFBBRG_ID, FDFBBRGN, FDFBSATUAN, FDFBHPOKOK, FDFBQTYT,"
        q += "FDFBDISC1,FDFBDISC2,FDFBDISC3,FDFBTOTAL) "
        q += "VALUES ("
        q += FDPONO[i] + ","
        q += "'" + FDPOPRD_ID[i] + "',"
        q += "'" + FDPOBRG_ID[i] + "',"
        q += "%s,"
        q += "'" + FDPOSATUAN[i] + "',"
        q += FDPOHARGA[i] + ","
        q += FDPOQTY[i] + ","
        q += FDPODISC1[i] + ","
        q += FDPODISC2[i] + ","
        q += FDPODISC3[i] + ","
        q += FDPOTOTAL[i] + ");"
        proc_param.extend([FDPOBRGN[i]])
        i += 1

    q += "EXEC FRM_AUD_H_POB "
    q += "'" + FHPOBUKTI_ID + "',"
    q += "'" + FHPOTGL + "',"
    q += "'" + FHPOTGLKIRIM + "',"
    q += "'" + FHPOSUPP_ID + "',"
    q += "'" + FHPOTPAY_ID + "',"
    q += "'" + FHPODPP + "',"
    q += "'" + FHPOPPN + "',"
    q += "'" + FHPOPPNRP + "',"
    q += "'" + FHPOJUMLAH + "',"
    q += "'" + FHPOREMARK + "',"
    q += "'" + FHPOUSERS + "',"
    q += "@NOW,"
    q += "'" + ID_CABANG + "',"
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
        data.append({"query": "select * from H_POB where FHPOBUKTI_ID = '" + FHPOBUKTI_ID + "'"})
        data.append({"query": "select * from D_POB where FDPOBUKTI_ID = '" + FHPOBUKTI_ID + "'"})
        Globals().create_log('Hapus LogDelete.txt', 'FARMASI', data, user)

    result = Globals().getDataSP(q,proc_param)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getOrder_Pembelian(request):
    ID_CABANG = request.session['kdCabang']
    no_bukti = '%'+request.GET['no_bukti']+'%'
    supplier = '%'+request.GET['supplier']+'%'
    tipe = request.GET['tipe']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")

    if(tipe == 'order_pembelian_by_bulan'):
        q = "select top 100 a.*, b.NAME_SUPPL, convert(varchar, a.FHPOTGL, 23) as TANGGAL "
        q += "from H_POB a inner join SUPPLIER b on a. FHPOSUPP_ID = b.SUPPLIERC "
        q += "where (a.FHPOBUKTI_ID like %s) and (b.NAME_SUPPL like %s) and "
        q += "(YEAR(FHPOTGL) = %s) and (MONTH(FHPOTGL) = %s) and FHPOBRANCH = %s "
        result = Globals().getDataQuery(q, [no_bukti, supplier, tanggal.year, tanggal.month,ID_CABANG])
    else:
        q = "select top 100 a.*, b.NAME_SUPPL, convert(varchar, a.FHPOTGL, 23) as TANGGAL "
        q += "from H_POB a inner join SUPPLIER b on a. FHPOSUPP_ID = b.SUPPLIERC "
        q += "where (a.FHPOBUKTI_ID like %s) and (b.NAME_SUPPL like %s) and "
        q += "FHPOTGL = %s and FHPOBRANCH = %s "
        result = Globals().getDataQuery(q, [no_bukti, supplier, tanggal,ID_CABANG])

    
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getorderBarangByBuktiPembelian(request):
    no_bukti = request.GET['no_bukti']
    q = "select a.*, b.FDPONO as NO, b.FDPOBRG_ID as ID_BARANG, "
    q += "b.FDPOBRGN as NAMA_BARANG, b.FDPOSATUAN as SATUAN, b.FDPOHARGA as HARGA_POKOK, "
    q += "b.FDPOQTY as QTY, b.FDPODISC1 as DISC_1, b.FDPODISC2 as DISC_2, b.FDPODISC3 as DISC_RP, "
    q += "b.FDPOTOTAL as TOTAL, "
    q += "(select kstandart from BARANG d where d.BARANGC= b.FDPOBRG_ID and d.satkecil= b.FDPOSATUAN "
    q += "union select KSTANDART*KKECIL as KONVERSI from BARANG e where e.BARANGC= b.FDPOBRG_ID and e.satkemas= b.FDPOSATUAN "
    q += "union select 1 as KONVERSI from BARANG F where F.BARANGC= b.FDPOBRG_ID and F.SATSTAND= b.FDPOSATUAN) as KONVERSI, "
    q += "c.SATSTAND  as SATSTAND "
    q += "from H_POB a inner join D_POB b on a.FHPOBUKTI_ID = b.FDPOBUKTI_ID "
    q += "inner join BARANG c on b.FDPOBRG_ID=c.barangc "
    q += "where a.FHPOBUKTI_ID = %s order by b.FDPONO "
    result = Globals().getDataQuery(q, [no_bukti])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getSupPay(request):
    kode = request.GET['kode']
    tipe = request.GET['tipe']
    if tipe == 'supplier':
        q = "select NAME_SUPPL as NAMA from SUPPLIER where SUPPLIERC = %s"
        result = Globals().getDataQuery(q, [kode])
    elif tipe == 'tpay':
        q = "select NAMA from TPAY where TPAY_ID = %s"
        result = Globals().getDataQuery(q, [kode])
    json_data = json.dumps(result[0], cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getvalidasiOrder(request):
    ID_CABANG = request.session['kdCabang']
    tipe = request.GET['tipe']
    tanggalawal = datetime.strptime(request.GET['tanggalawal'], "%Y-%m-%d")
    tanggalakhir = datetime.strptime(request.GET['tanggalakhir'], "%Y-%m-%d")
    if(tipe == 'mutasi_by_all'):
        q = "SELECT TOP (100)  H_POB. FHPOBUKTI_ID,  H_POB. FHPOTGL,  H_POB. FHPOSUPP_ID,  H_POB.FHPOREMARK,  SUPPLIER. NAME_SUPPL, "
        q += "CONVERT(varchar, H_POB. FHPOTGL, 23) AS TANGGAL,CAST(FKUNCI AS INT) as FKUNCI "
        q += "from  H_POB INNER JOIN    SUPPLIER ON  H_POB. FHPOSUPP_ID =  SUPPLIER. SUPPLIERC "
        q += "where ( FHPOTGL >= %s) and "
        q += "( FHPOTGL <= %s  and FHPOBRANCH = %s ) "
    elif (tipe == 'mutasi_by_belum'):
        q = "SELECT TOP (100)  H_POB. FHPOBUKTI_ID,  H_POB. FHPOTGL,  H_POB. FHPOSUPP_ID,  H_POB.FHPOREMARK,  SUPPLIER. NAME_SUPPL, "
        q += "CONVERT(varchar, H_POB. FHPOTGL, 23) AS TANGGAL,CAST(FKUNCI AS INT) as FKUNCI "
        q += "from  H_POB INNER JOIN    SUPPLIER ON  H_POB. FHPOSUPP_ID =  SUPPLIER. SUPPLIERC "
        q += "where ( FHPOTGL >= %s) and "
        q += "( FHPOTGL <= %s) and isnull(FKUNCI,0)=0  and FHPOBRANCH = %s  "
    else:
        q = "SELECT TOP (100)  H_POB. FHPOBUKTI_ID,  H_POB. FHPOTGL,  H_POB. FHPOSUPP_ID,  H_POB.FHPOREMARK,  SUPPLIER. NAME_SUPPL, "
        q += "CONVERT(varchar, H_POB. FHPOTGL, 23) AS TANGGAL,CAST(FKUNCI AS INT) as FKUNCI "
        q += "from  H_POB INNER JOIN    SUPPLIER ON  H_POB. FHPOSUPP_ID =  SUPPLIER. SUPPLIERC "
        q += "where ( FHPOTGL >= %s) and "
        q += "( FHPOTGL <= %s) and fkunci=1  and FHPOBRANCH = %s  "
    result = Globals().getDataQuery(q, [tanggalawal, tanggalakhir,ID_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def SPValidasiMutasi(request):
    users = request.POST['users']
    updaters = request.POST['updaters']
    No_faktur = request.POST['No_faktur']
    FKUNCI = request.POST['FKUNCI']
    i = 0
    q = ""
    No_faktur = json.loads(request.POST['No_faktur'])
    FKUNCI = json.loads(request.POST['FKUNCI'])

    for x in No_faktur:
        # if FKUNCI[i] == True:
        #     kunci = 1
        # else:
        #     kunci = 0

        q += "UPDATE  H_POB  SET FKUNCI =%s   WHERE  FHPOBUKTI_ID = '%s';" % (
            FKUNCI[i], No_faktur[i])
        i += 1
    Globals().executeQuery(q)
    json_data = json.dumps({'status': 'sukses'}, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetak_order(request):
    no_bukti = request.GET['no_bukti']
    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    pdf_file = Globals().generateReportDB(
        "order_pembelian.jrxml",
        'order_pembelian',
        user,
        {
            'no_bukti': no_bukti,
            'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
            'tanggal': Globals().dateIndo(tanggal),
            'jam': jam,
        }
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetak_orderinternal(request):
    no_bukti = request.GET['no_bukti']
    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    pdf_file = Globals().generateReportDB(
        "order_pembelianINT.jrxml",
        'order_pembelianINT',
        user,
        {
            'no_bukti': no_bukti,
            'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
            'tanggal': Globals().dateIndo(tanggal),
            'jam': jam,
        }
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap_supplier(request):
    start = request.GET['start']
    finish = request.GET['finish']

    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    pdf_file = Globals().generateReportDB(
        "orderbeli_frm02.jrxml",
        'orderbeli_frm02',
        user,
        {
            'start': start,
            'finish': finish,
            'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
            'alamat_rs': Globals().getDataCabang('ALAMAT1'),
            'tanggal': Globals().dateIndo(tanggal),
            'jam': jam,
        }
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap(request):
    start = request.GET['start']
    finish = request.GET['finish']

    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    # proses cetak
    # print(finish)
    pdf_file = Globals().generateReportDB(
        "orderbeli_frm03.jrxml",
        'orderbeli_frm03',
        user,
        {
            'start': start,
            'finish': finish,
            'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
            'alamat_rs': Globals().getDataCabang('ALAMAT1'),
            'tanggal': Globals().dateIndo(tanggal),
            'jam': jam,
        }
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap02(request):
    start = request.GET['start']
    finish = request.GET['finish']

    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    # proses cetak
    # print(finish)
    pdf_file = Globals().generateReportDB(
        "orderbeli_frm03A.jrxml",
        'orderbeli_frm03A',
        user,
        {
            'start': start,
            'finish': finish,
            'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
            'alamat_rs': Globals().getDataCabang('ALAMAT1'),
            'tanggal': Globals().dateIndo(tanggal),
            'jam': jam,
        }
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap03(request):
    start = request.GET['start']
    finish = request.GET['finish']

    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    # proses cetak
    # print(finish)
    pdf_file = Globals().generateReportDB(
        "orderbeli_frm03B.jrxml",
        'orderbeli_frm03B',
        user,
        {
            'start': start,
            'finish': finish,
            'nama_rs': Globals().getDataCabang('PERUSAHAAN'),
            'alamat_rs': Globals().getDataCabang('ALAMAT1'),
            'tanggal': Globals().dateIndo(tanggal),
            'jam': jam,
        }
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDiscSuppBarang(request):
    
    kode_supplier = request.GET['kode_supplier']
    kode_barang = request.GET['kode_barang']
    q = "SELECT a.FMSDKODESUP, FMSDKODEBRG, FMSDDISC01, FMSDDISC02,USERRS,UPDATERS,b.NAME_BRG,b.HPOKOK FROM  "
    q +="SUPPLIER_DISC a inner join BARANG b on a.FMSDKODEBRG=b.BARANGC where a.FMSDKODESUP=%s and a.FMSDKODEBRG=%s "
    result = Globals().getDataQuery(q, [kode_supplier,kode_barang])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getcloseOrder(request):
    ID_CABANG = request.session['kdCabang']
    tipe = request.GET['tipe']
    tanggalawal = datetime.strptime(request.GET['tanggalawal'], "%Y-%m-%d")
    tanggalakhir = datetime.strptime(request.GET['tanggalakhir'], "%Y-%m-%d")
    if(tipe == 'order_by_all'):
        q = "SELECT TOP (100)  H_POB. FHPOBUKTI_ID,  H_POB. FHPOTGL,  H_POB. FHPOSUPP_ID,  H_POB.FHPOREMARK,  SUPPLIER. NAME_SUPPL, "
        q += "CONVERT(varchar, H_POB. FHPOTGL, 23) AS TANGGAL,CAST(FCLOSE AS INT) as FCLOSE "
        q += "from  H_POB INNER JOIN    SUPPLIER ON  H_POB. FHPOSUPP_ID =  SUPPLIER. SUPPLIERC "
        q += "where ( FHPOTGL >= %s) and "
        q += "( FHPOTGL <= %s)  and FHPOBRANCH = %s  order by FHPOBUKTI_ID "
    elif (tipe == 'order_by_belum'):
        q = "SELECT TOP (100)  H_POB. FHPOBUKTI_ID,  H_POB. FHPOTGL,  H_POB. FHPOSUPP_ID,  H_POB.FHPOREMARK,  SUPPLIER. NAME_SUPPL, "
        q += "CONVERT(varchar, H_POB. FHPOTGL, 23) AS TANGGAL,CAST(FCLOSE AS INT) as FCLOSE "
        q += "from  H_POB INNER JOIN    SUPPLIER ON  H_POB. FHPOSUPP_ID =  SUPPLIER. SUPPLIERC "
        q += "where ( FHPOTGL >= %s) and "
        q += "( FHPOTGL <= %s) and isnull(FCLOSE,0)=0 and FHPOBRANCH = %s  order by FHPOBUKTI_ID "
    else:
        q = "SELECT TOP (100)  H_POB. FHPOBUKTI_ID,  H_POB. FHPOTGL,  H_POB. FHPOSUPP_ID,  H_POB.FHPOREMARK,  SUPPLIER. NAME_SUPPL, "
        q += "CONVERT(varchar, H_POB. FHPOTGL, 23) AS TANGGAL,CAST(FCLOSE AS INT) as FCLOSE "
        q += "from  H_POB INNER JOIN    SUPPLIER ON  H_POB. FHPOSUPP_ID =  SUPPLIER. SUPPLIERC "
        q += "where ( FHPOTGL >= %s) and "
        q += "( FHPOTGL <= %s) and FCLOSE=1  and FHPOBRANCH = %s order by FHPOBUKTI_ID "
    result = Globals().getDataQuery(q, [tanggalawal, tanggalakhir,ID_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def SPcloseorder(request):
    users = request.POST['users']
    updaters = request.POST['updaters']
    No_faktur = request.POST['No_faktur']

    q = "UPDATE  H_POB  SET FCLOSE = 1 WHERE   FHPOBUKTI_ID = %s"
    result = Globals().getDataQuery(q, [No_faktur])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def UNSPcloseorder(request):
    users = request.POST['users']
    updaters = request.POST['updaters']
    No_faktur = request.POST['No_faktur']
    q = "UPDATE  H_POB  SET FCLOSE = 0 WHERE   FHPOBUKTI_ID = %s"
    result = Globals().getDataQuery(q, [No_faktur])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
