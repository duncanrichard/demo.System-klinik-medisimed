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

def frm_mutasi_M(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_mutasi_M")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_mutasi_M", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_mutasi_M", '1')
        menubarCount = len(menubars)
        response = render(request, 'farmasi/mutasi_masuk/mutasimasuk.html', {
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

def getdivisi(request):
    tipe = request.GET['tipe']
    ID_CABANG = request.session['kdCabang']
    if(tipe == 'Divisi'):
        kode = request.GET['kode']
        q = "SELECT WH_ID, NAME_WH "
        q += "FROM WAREHOUSE  "
        q += "WHERE (WH_ID LIKE %s) AND aktif=1 and c.BRANCH=%s"
        result = Globals().getDataQuery(q,[kode,ID_CABANG])
    else:
        kode_divisi = '%'+request.GET['search_kode_divisi']+'%'
        nama_divisi = '%'+request.GET['search_nama_divisi']+'%'
        q = "SELECT WH_ID, NAME_WH "
        q += "FROM WAREHOUSE  "
        q += "WHERE (WH_ID LIKE %s) AND (NAME_WH LIKE %s)  AND aktif=1 and c.BRANCH=%s "
        result = Globals().getDataQuery(q, [kode_divisi,nama_divisi,ID_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def SP_AUD_CLAIMS(request):
    # DETAIL
    NO = json.loads(request.POST['NO'])
    TTYPEC = json.loads(request.POST['TTYPEC'])
    BARANGC = json.loads(request.POST['BARANGC'])
    NAME_BRG = json.loads(request.POST['NAME_BRG'])
    SATSTAND = json.loads(request.POST['SATSTAND'])
    HPOKOK = json.loads(request.POST['HPOKOK'])
    QTY = json.loads(request.POST['QTY'])
    TOTAL = json.loads(request.POST['TOTAL'])
    KONVERSI = json.loads(request.POST['KONVERSI'])
    SATUANSTD = json.loads(request.POST['SATUANSTD'])
    BUKTI_ID = json.loads(request.POST['BUKTI_ID'])
    SUPPL_ID = json.loads(request.POST['SUPPL_ID'])
    # MAIN EXEC
    FHCLMBUKTI_ID = request.POST['FHCLMBUKTI_ID']
    FHCLMTGL = request.POST['FHCLMTGL']
    FHCLMCUST_ID = request.POST['FHCLMCUST_ID']
    FHCLMCUSTN = request.POST['FHCLMCUSTN']
    FHCLMWH_ID = request.POST['FHCLMWH_ID']
    FHCLMWHN = request.POST['FHCLMWHN']
    FHCLMREMARK = request.POST['FHCLMREMARK']
    JENIS = request.POST['JENIS']
    StatusAUD = request.POST['StatusAUD']
    USERRS = request.session['user_id']
    ID_CABANG = request.session['kdCabang']
    q = "SET NOCOUNT ON;DECLARE @LIST_FJINKOTAD FBELID;"
    q += "DECLARE @NOW datetime; "
    q += "SET @NOW = GETDATE(); "
    proc_param = []
    i = 0
    for x in BARANGC:
        q += "INSERT INTO @LIST_FJINKOTAD (FDFBNOM,FDFBPRD_ID, FDFBBRG_ID, FDFBBRGN, FDFBSATUAN, FDFBHPOKOK,FDFBKONVERSI, FDFBSATUANSTD,FDFBBUKTI_ID,FDFBSUPPL_ID ,FDFBQTYT) "
        q += "VALUES ("
        q += "'" + NO[i] + "',"
        q += "'" + TTYPEC[i] + "',"
        q += "'" + BARANGC[i] + "',"
        q += "%s,"
        q += "'" + SATSTAND[i] + "',"
        q += HPOKOK[i] + ","
        q += KONVERSI[i] + ","
        q += "'" + SATUANSTD[i] + "',"
        q += "'" + BUKTI_ID[i] + "',"
        q += "'" + SUPPL_ID[i] + "',"
        q += QTY[i] + ");"
        proc_param.extend([NAME_BRG[i]])
        i += 1
    q += "EXEC FRM_AUD_CLAIMS "
    q += "'" + FHCLMBUKTI_ID + "',"
    q += "'" + FHCLMTGL + "',"
    q += "'" + FHCLMCUST_ID + "',"
    q += "'" + FHCLMCUSTN + "',"
    q += "'" + FHCLMWH_ID + "',"
    q += "'" + FHCLMWHN + "',"
    q += "'" + FHCLMREMARK + "',"
    q += "'" + USERRS + "',"
    q += "@NOW,"
    q += "'" + JENIS + "',"
    q += "'" + ID_CABANG + "',"
    q += "'" + StatusAUD + "',"
    q += "@LIST_FJINKOTAD,"
    q += "''"
    if (StatusAUD=='D') :
        user = {
        'user_id': request.session['user_id'],
        'user_name': request.session['user_name'],
        'user_priv': request.session['user_priv'],
        }
        data = []
        data.append({"query": "select * from CLAIMS where FHCLMBUKTI_ID = '" + FHCLMBUKTI_ID + "'"})
        data.append({"query": "select * from CLAIMSD where FDCLMBUKTI_ID = '" + FHCLMBUKTI_ID + "'"})
        Globals().create_log('Hapus LogDelete.txt', 'FARMASI', data, user)

    result = Globals().getDataSP(q,proc_param)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getMutasiMasuk(request):
    no_bukti = '%'+request.GET['no_bukti']+'%'
    supplier = '%'+request.GET['supplier']+'%'
    gudang = '%'+request.GET['gudang']+'%'
    tipe = request.GET['tipe']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")

    if(tipe == 'mutasi_by_bulan'):
        q = "select top 100 *, convert(varchar, FHCLMTGL, 23) as TANGGAL "
        q +="from CLAIMS where (FHCLMBUKTI_ID like %s) and "
        q += "(FHCLMCUSTN like %s) and (FHCLMWHN like %s) and (YEAR(FHCLMTGL) = %s) and (MONTH(FHCLMTGL) = %s)"
        result = Globals().getDataQuery(q, [no_bukti, supplier, gudang, tanggal.year, tanggal.month])
    else:
        q = "select top 100 *, convert(varchar, FHCLMTGL, 23) as TANGGAL "
        q +="from CLAIMS where (FHCLMBUKTI_ID like %s) and "
        q += "(FHCLMCUSTN like %s) and (FHCLMWHN like %s) and (FHCLMTGL = %s)"
        result = Globals().getDataQuery(q, [no_bukti, supplier, gudang, tanggal])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
    
def getBarangByBukti(request):
    no_bukti = request.GET['no_bukti']
    q = "select b.*, a.FDCLMNOM as NO, a.FDCLMPRD_ID as TTYPEC, a.FDCLMBRG_ID as BARANGC, "
    q += "a.FDCLMBRGN as NAME_BRG, a.FDCLMSATUAN as SATSTAND, CAST(a.FDCLMQTY AS INT) as QTY, a.FDCLMHPOKOK as HPOKOK,FDCLMKONVERSI AS KONVERSI,FDCLMSATUANSTD AS SATUANSTD "
    q += "from CLAIMSD a left join CLAIMS b on a.FDCLMBUKTI_ID = b.FHCLMBUKTI_ID "
    q += "where a.FDCLMBUKTI_ID = %s order by FDCLMNOM asc"
    result = Globals().getDataQuery(q, [no_bukti])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetakBarang(request):
    nomor = request.POST['nomor']
    pilihcetak=request.POST['pilihcetak']
    q = "select a.FHCLMBUKTI_ID as NOMOR, convert(varchar, a.FHCLMTGL, 23) as TANGGAL, "
    q += "a.FHCLMCUSTN as SUPPLIER, a.FHCLMWHN as GUDANG, a.FHCLMREMARK as KETERANGAN, "
    q += "CAST((select sum(b.FDCLMQTY) as SUB_TOTALs from CLAIMSD b "
    q += "where b.FDCLMBUKTI_ID = %s group by FDCLMBUKTI_ID) as INT) as SUB_TOTAL, "
    q += "CAST((select count(b.FDCLMQTY) as JML_DETAILs from CLAIMSD b "
    q += "where b.FDCLMBUKTI_ID = %s group by FDCLMBUKTI_ID) as INT) as JML_DETAIL "
    q += "from CLAIMS a where FHCLMBUKTI_ID = %s "
    result = Globals().getDataQuery(q, [nomor, nomor, nomor])
    nomor_nama_file = nomor.replace("/", "-")
    user = request.session['user_id']
    tanggal = dateIndo(datetime.now().strftime('%Y-%m-%d'))
    jam = str(datetime.now().strftime('%H:%M:%S'))
    tanggal_waktu_cetak = tanggal + ' ' + jam
    pdf_file = Globals().generateReportDB(
        'mutasi_bhp_masuk.jrxml',
        'MUTASI_BHP_MASUK_' + nomor_nama_file,
        user,
        {
            'nama_rs':request.session['nama_cabang'],
            'nomor':nomor,
        },
		list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetak_lap_rekap_divisi(request):
    start = request.GET['start']
    finish = request.GET['finish']
    dariDivisi = request.GET['dariDivisi']
    sdDivisi = request.GET['sdDivisi']

    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    pilihcetak=request.GET['pilihcetak']

    pdf_file = Globals().generateReportDB(
        "mutasi_bhp_masuk2.jrxml", 
        'mutasi_bhp_masuk2', 
        user,
        {
            'start': start,
            'finish': finish,
            'dariDivisi': dariDivisi,
            'sdDivisi': sdDivisi,
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

