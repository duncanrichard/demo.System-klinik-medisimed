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


def frm_barang(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "frm_barang")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_barang", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "frm_barang", '1')
        menubarCount = len(menubars)

        response = render(request, 'farmasi/barang/barang.html', {
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
    
def load_barang(request):
    nama = '%'+request.GET['nama']+'%'
    q = "SELECT TOP 100 A.BARANGC,A.BARCODE, A.NAME_BRG, A.TTYPEC, A.HPOKOK, A.HJUAL,HJUALRI, HJUALASKIN, HJUALSUKARELA, A.QTYMIN, A.QTYMAX, A.SUPPLIER_ID, A.SATSTAND, isnull(A.aktif,0) as aktif, A.satkemas, A.satkecil, A.kstandart, A.kkecil,  "
    q += "GENERIC,KERJASAMA, OBATDROPING, ZATADITIF, KEKUATAN, SATKEKUATAN, INDIKASI, ATURANPAKAI, EFEKSAMPING, PENYIMPANAN, CARAPENGGUNAAN,  "
    q += "C.NAME_SUPPL,B.NAME_PRD,D.MERK_ID,D.NAMA,E.FMPSUPPLIERC,E.FMPNAME_SUPPL,F.FMLFKODE,F.FMLFKETERAGAN,G.FMSKODE,G.FMSSEDIAAN  "
    q += "FROM BARANG AS A  LEFT OUTER JOIN  "
    q += "PRODUKOBAT AS B ON A.TTYPEC = B.PRD_ID LEFT OUTER JOIN  "
    q += "SUPPLIER AS C ON A.SUPPLIER_ID = C.SUPPLIERC LEFT OUTER JOIN " 
    q += "MERK AS D ON D.MERK_ID = A.MERK_ID LEFT OUTER JOIN  "
    q += "PABRIKAN AS E ON A.PABRIKAN = E.FMPSUPPLIERC LEFT OUTER JOIN " 
    q += "LOKASI AS F ON A.LOKASI = F.FMLFKODE LEFT OUTER JOIN " 
    q += "SEDIAAN AS G ON A.SEDIAAN=G.FMSKODE where aktif=0 and name_brg like %s ORDER BY NAME_BRG"
    result = Globals().getDataQuery(q, [nama])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def load_barangNon(request):
    nama = '%'+request.GET['nama']+'%'
    q = "SELECT TOP 100 A.BARANGC,A.BARCODE, A.NAME_BRG, A.TTYPEC, A.HPOKOK, A.HJUAL,HJUALRI, HJUALASKIN, HJUALSUKARELA, A.QTYMIN, A.QTYMAX, A.SUPPLIER_ID, A.SATSTAND, isnull(A.aktif,0) as aktif, A.satkemas, A.satkecil, A.kstandart, A.kkecil,  "
    q += "GENERIC,KERJASAMA, OBATDROPING, ZATADITIF, KEKUATAN, SATKEKUATAN, INDIKASI, ATURANPAKAI, EFEKSAMPING, PENYIMPANAN, CARAPENGGUNAAN,  "
    q += "C.NAME_SUPPL,B.NAME_PRD,D.MERK_ID,D.NAMA,E.FMPSUPPLIERC,E.FMPNAME_SUPPL,F.FMLFKODE,F.FMLFKETERAGAN,G.FMSKODE,G.FMSSEDIAAN  "
    q += "FROM BARANG AS A  LEFT OUTER JOIN  "
    q += "PRODUKOBAT AS B ON A.TTYPEC = B.PRD_ID LEFT OUTER JOIN  "
    q += "SUPPLIER AS C ON A.SUPPLIER_ID = C.SUPPLIERC LEFT OUTER JOIN " 
    q += "MERK AS D ON D.MERK_ID = A.MERK_ID LEFT OUTER JOIN  "
    q += "PABRIKAN AS E ON A.PABRIKAN = E.FMPSUPPLIERC LEFT OUTER JOIN " 
    q += "LOKASI AS F ON A.LOKASI = F.FMLFKODE LEFT OUTER JOIN " 
    q += "SEDIAAN AS G ON A.SEDIAAN=G.FMSKODE where aktif<>0 and name_brg like %s ORDER BY NAME_BRG"
    
    result = Globals().getDataQuery(q, [nama])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def open_barang(request):
    q = "SELECT A.BARANGC,A.BARCODE, A.NAME_BRG, A.TTYPEC, A.HPOKOK, A.HJUAL,HJUALRI, HJUALASKIN, HJUALSUKARELA, A.QTYMIN, A.QTYMAX, A.SUPPLIER_ID, A.SATSTAND, isnull(A.aktif,0) as aktif, A.satkemas, A.satkecil, A.kstandart, A.kkecil,  "
    q += "GENERIC,KERJASAMA, OBATDROPING, ZATADITIF, KEKUATAN, SATKEKUATAN, INDIKASI, ATURANPAKAI, EFEKSAMPING, PENYIMPANAN, CARAPENGGUNAAN,  "
    q += "C.NAME_SUPPL,B.NAME_PRD,D.MERK_ID,D.NAMA,E.FMPSUPPLIERC,E.FMPNAME_SUPPL,F.FMLFKODE,F.FMLFKETERAGAN,G.FMSKODE,G.FMSSEDIAAN  "
    q += "FROM BARANG AS A  LEFT OUTER JOIN  "
    q += "PRODUKOBAT AS B ON A.TTYPEC = B.PRD_ID LEFT OUTER JOIN  "
    q += "SUPPLIER AS C ON A.SUPPLIER_ID = C.SUPPLIERC LEFT OUTER JOIN " 
    q += "MERK AS D ON D.MERK_ID = A.MERK_ID LEFT OUTER JOIN  "
    q += "PABRIKAN AS E ON A.PABRIKAN = E.FMPSUPPLIERC LEFT OUTER JOIN " 
    q += "LOKASI AS F ON A.LOKASI = F.FMLFKODE LEFT OUTER JOIN " 
    q += "SEDIAAN AS G ON A.SEDIAAN=G.FMSKODE where aktif=0 ORDER BY NAME_BRG"
    result = Globals().getDataQuery(q)
    res = {
        'data': result,
        'totalCount' : len(result)
    }
    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def load_barang_stokmaxmin(request):
    kode_barang =request.GET['kode_barang']
    q = "SELECT a.BARANGID, a.GUDANGID, a.STOKMAX, a.STOKMIN,B.NAME_BRG , C.NAME_WH "
    q +="FROM BARANG_STOKMAXMIN AS a INNER JOIN "
    q +="BARANG AS b ON a.BARANGID = b.BARANGC INNER JOIN "
    q +="WAREHOUSE AS C ON a.GUDANGID = C.WH_ID where BARANGID= %s "
    result = Globals().getDataQuery(q, [kode_barang])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getgudang(request):
    q = "select WH_ID,NAME_WH from WAREHOUSE a where a.AKTIF=1 "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def barang_simpan(request):
    kode = request.POST['kode']
    barcode = request.POST['barcode']
    nama = request.POST['nama']
    harga_pokok = request.POST['harga_pokok']
    harga_jual = request.POST['harga_jual']
    harga_jualri = request.POST['harga_jualri']
    harga_jualbpjs = request.POST['harga_jualbpjs']
    harga_jualprsh = request.POST['harga_jualprsh']
    
    qty_max = request.POST['qty_max']
    qty_min = request.POST['qty_min']
    sat_standart = request.POST['sat_standart']
    sat_sedang = request.POST['sat_sedang']
    sat_kemas = request.POST['sat_kemas']
    konversistd = request.POST['konversistd']
    konversikemas = request.POST['konversikemas']
    aktif = request.POST['aktif']
    satkekuatan = request.POST['satkekuatan']
    kekuatan = request.POST['kekuatan']
    ZatAktif = request.POST['ZatAktif']
    golongan = request.POST['golongan']
    produk = request.POST['produk']
    sediaan = request.POST['sediaan']
    supplier = request.POST['supplier']
    pabrikan = request.POST['pabrikan']
    lokasi = request.POST['lokasi']
    indikasi = request.POST['indikasi']
    penyimpanan = request.POST['penyimpanan']
    aturanpakai = request.POST['aturanpakai']
    efekSamping = request.POST['efekSamping']
    caraguna = request.POST['caraguna']
    Generik = request.POST['Generik']
    Formalarium = request.POST['Formalarium']
    PRB = request.POST['PRB']
    kerjasama = request.POST['kerjasama']
    retriksi= request.POST['retriksi']
    status_aud = request.POST['status_aud']
    userrs = request.session['user_id']
    OutputNoBukti = request.POST['OutputNoBukti']
    q = "SET NOCOUNT ON;"
    q += "exec FRM_AUD_BARANG  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
    proc_param =[kode,barcode, nama, harga_pokok, harga_jual,harga_jualri,harga_jualbpjs,harga_jualprsh, qty_max, qty_min, sat_standart,
                        sat_sedang, sat_kemas, konversistd, konversikemas, aktif,satkekuatan,kekuatan,ZatAktif,
                        golongan,produk,sediaan,supplier,pabrikan,lokasi,kerjasama,indikasi,aturanpakai,efekSamping,penyimpanan,caraguna,Formalarium,
                        Generik,PRB,retriksi, status_aud,userrs, OutputNoBukti]
    # print (q % tuple(proc_param))
    result = Globals().getDataSP(q, proc_param)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def suplier_hapus(request):
    kode = request.POST['kode']
    user = {
		'user_id': request.session['user_id'],
		'user_name': request.session['user_name'],
		'user_priv': request.session['user_priv'],
	}
    data = []
    data.append({"query": "select * from BARANG WHERE BARANGC = '" + kode + "'"})
    Globals().create_log('Hapus LogDelete.txt', 'FARMASI', data, user)

    q = "DELETE FROM BARANG WHERE BARANGC = %s"
    result = Globals().getDataSP(q, [kode])
    return HttpResponse(result, content_type="application/json")

def cetak_barang(request):
    start = request.GET['start']
    finish = request.GET['finish']
    kodeproduk_dari = request.GET['kodeproduk_dari']
    kodeproduk_sampai = request.GET['kodeproduk_sampai']
    kodesuplier_dari = request.GET['kodesuplier_dari']
    kodesuplier_sampai = request.GET['kodesuplier_sampai']
    kodepabrikan_dari = request.GET['kodepabrikan_dari']
    kodepabrikan_sampai = request.GET['kodepabrikan_sampai']
    cetak = request.GET['cetak']
    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    
    

    if cetak=='1' :
        q = "SELECT A.BARANGC AS KODE_BARANG,A.NAME_BRG AS NAMA_BARANG,A.SATSTAND AS SATUAN,A.KSTANDART AS KONVERSI,A.SATKEMAS,A.SATKECIL,A.KKECIL AS KONVERSI_KECIL, "
        q +="A.HJUAL AS HARGA_RJ,A.HJUALRI AS HARGA_RI,a.HPOKOK,a.HJUALASKIN as HJUAL_BPJS,A.ZATADITIF AS KANDUNGAN, "
        q +="A.PRB,A.GENERIC,A.FORMULARIUMRS,A.QTYMAX,A.QTYMIN,B.NAME_PRD AS KELOMPOK,C.NAMA as GOLONGAN,D.NAME_SUPPL AS PBF,E.FMPNAME_SUPPL AS PABRIKAN,F.FMSSEDIAAN AS SEDIAAN "
        q +="FROM BARANG A LEFT JOIN PRODUKOBAT B ON A.TTYPEC=B.PRD_ID "
        q +="LEFT JOIN MERK C ON A.MERK_ID=C.MERK_ID "
        q +="LEFT JOIN SUPPLIER D ON A.SUPPLIER_ID=D.SUPPLIERC "
        q +="LEFT JOIN PABRIKAN E ON A.PABRIKAN=E.FMPSUPPLIERC "
        q +="LEFT JOIN SEDIAAN F ON A.SEDIAAN=F.FMSKODE where a.AKTIF=0 "
        q +="and a.BARANGC>=%s and a.BARANGC<=%s "
        q +="and a.TTYPEC>=%s and a.TTYPEC<=%s "
        q +="and a.SUPPLIER_ID>=%s and a.SUPPLIER_ID<=%s "
        q +="and a.PABRIKAN>=%s and a.PABRIKAN<=%s "
        result =Globals().getDataQuery(q,[start,finish,kodeproduk_dari,kodeproduk_sampai,kodesuplier_dari,kodesuplier_sampai,kodepabrikan_dari,kodepabrikan_sampai])
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")
    else :
        pdf_file = Globals().generateReportDB(
            "barang_frm.jrxml",
            'barang_frm',
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

def barangwh_simpan(request):
    kode = request.POST['kode']
    kodewh = request.POST['kodewh']
    qtywh_max = request.POST['qtywh_max']
    qtywh_min = request.POST['qtywh_min']
    status_aud = request.POST['status_aud']
    OutputNoBukti = request.POST['OutputNoBukti']
    q = "exec FRM_AUD_BARANGWH  %s, %s, %s, %s, %s, %s"
    result = Globals().getDataSP(q, [kode, kodewh, qtywh_max, qtywh_min, status_aud, OutputNoBukti])
    return HttpResponse(result, content_type="application/json")

def cetak_barangwh(request):
    start = request.GET['start']
    finish = request.GET['finish']
    tanggal = datetime.now().strftime('%Y-%m-%d')
    jam = str(datetime.now().strftime('%H:%M:%S'))
    user = request.session['user_priv']
    # proses cetak
    # print(start)
    pdf_file = Globals().generateReportDB(
        "barangwh_frm.jrxml",
        'barangwh_frm',
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
