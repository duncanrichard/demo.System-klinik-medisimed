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

def master_produk(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "master_produk")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "master_produk", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "master_produk", '1')
        menubarCount = len(menubars)

        qjenis_tarip = "SELECT * FROM TARIF_JENIS"
        jenis_tarip =Globals().getDataQuery(qjenis_tarip)

        qkomponen = "select * from PRODUK_COMPONENT"
        komponen = Globals().getDataQuery(qkomponen)

        response = render(request, 'dashboard/master_produk/base.html', {
            'navbars': navbars,
            'menubars': menubars,
            'menubarsChild': menubarsChild,
            'menubarsType': 1,
            'count_': menubarCount,
            'list_': Globals().getSeparator(menubarCount),
            'user_id': user_privelege,
            'jenis_tarip':jenis_tarip,
            'komponen':komponen,
        })
        response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
        return response
    else:
        return redirect('/login')

def getProdukHeader(request):
    jenis_tarip = request.GET['jenis_tarip']
    q = "SELECT A.FMKKLAS_ID,A.FMKKLASN,a.PARENT,a.FMPPOSFLAG,a.LEVEL,a.FMKJENISTARIP,a.FMKGOLTARIP,b.KPGNAMA, C.FMKKLASN AS induk  "
    q += "from KLAS_PRODUK a left join KLAS_PRODUK_GOLONGAN b on a.FMKGOLTARIP=b.KPGKODE "
    q += 'LEFT JOIN KLAS_PRODUK AS C ON a.PARENT = C.FMKKLAS_ID AND C.FMKJENISTARIP = %s '
    q += "where a.FMKJENISTARIP=%s ORDER BY a.FMKKLAS_ID, a.PARENT "
    result = Globals().getDataQuery(q,[jenis_tarip,jenis_tarip])
    arr = []
    for x in range(len(result)):
        if result[x]['PARENT'] == '0':
            del result[x]['PARENT']

    arr.append(result)
    # arr = []
    # result.insert(0,{'FMKKLAS_ID':'0','FMKKLAS_ID':'Root'})
    # arr.append(result)
    json_data = json.dumps(arr[0], cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getProdukDetail(request):
    id_produk = request.GET['id_produk']
    jenis_tarip = request.GET['jenis_tarip']
    q = "SELECT A.FMKKLAS_ID,A.FMKKLASN,a.PARENT,a.FMPPOSFLAG,a.LEVEL,a.FMKJENISTARIP,a.FMKGOLTARIP,b.KPGNAMA, C.FMKKLASN AS induk  "
    q += "from KLAS_PRODUK a left join KLAS_PRODUK_GOLONGAN b on a.FMKGOLTARIP=b.KPGKODE "
    q += 'LEFT JOIN KLAS_PRODUK AS C ON a.PARENT = C.FMKKLAS_ID AND C.FMKJENISTARIP = %s '
    q += "where a.FMKJENISTARIP=%s and a.PARENT= %s "
    q += "ORDER BY a.FMKKLAS_ID, a.PARENT "
    result = Globals().getDataQuery(q, [jenis_tarip,jenis_tarip,id_produk])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDatagol_klas(request):
    entry_kd_gol_klas = request.GET['entry_kd_gol_klas']
    q = "select KPGKODE,KPGNAMA from KLAS_PRODUK_GOLONGAN  where KPGKODE= %s "
    result = Globals().getDataQuery(q, [entry_kd_gol_klas])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getgol_klas(request):
    q = "select KPGKODE,KPGNAMA from KLAS_PRODUK_GOLONGAN order by KPGKODE "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def get_klas_tarif(request):
    q = "select FTGKODE,FTGNAMA from PRODUK_GOLONGAN order by FTGKODE "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def get_produk_unit(request):
    q = "select FTUKODE,FTUNAMA from PRODUK_UNIT order by FTUKODE "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def get_produk_acc(request):
    q = "select FMNOACC,FMNOACCKETERANGAN from PRODUK_NOACC order by FMNOACC "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getdataProduk(request):
    kode_induk = request.GET['kode_induk']
    jenis_tarip = request.GET['jenis_tarip']
    q = ' SELECT A.FMPPRODUK_ID, FMPKLAS_ID, FMPPRODUKN, A.FMPPOSFLAG, FMPUNITPRODUK, FMPUNITKLASPRODUK, FMPJENISTARIP, FMPADMINISTRASI, '
    q +=' FMPJASADOKTER, FMPPOSTMANUAL, FMPHIDDEN, FMPPOSTPAKET, FMPUNITKLASPRODUK2, FMPNOACC, FMPProdukBPjs, '
    q += ' B.FMKKLASN,C.FMKKLAS_ID as kd_induk, C.FMKKLASN AS induk, D.FTGKODE, D.FTGNAMA, E.FTUKODE, '
    q += ' E.FTUNAMA, F.FMNOACCKETERANGAN ,isnull(G.FMTTARIF,0) as FMTTARIF,isnull(G.FMTTGL_BERLAKU,getdate()) AS TGL_BERLAKU,FMTDISC_KONSUMEN,FMTFEE_RESELER '
    q += ' FROM PRODUK AS A JOIN KLAS_PRODUK AS B ON A.FMPKLAS_ID=B.FMKKLAS_ID AND B.FMKJENISTARIP = %s AND A.FMPJENISTARIP = %s '
    q += ' LEFT JOIN KLAS_PRODUK AS C ON B.PARENT = C.FMKKLAS_ID AND C.FMKJENISTARIP = %s '
    q += ' LEFT JOIN PRODUK_GOLONGAN AS D ON A.FMPUNITKLASPRODUK = D.FTGKODE '
    q += ' LEFT JOIN PRODUK_UNIT AS E ON A.FMPUNITPRODUK = E.FTUKODE '
    q += ' LEFT JOIN PRODUK_NOACC AS F ON A.FMPNOACC = F.FMNOACC '
    q += ' LEFT JOIN TARIF AS G ON A.FMPPRODUK_ID=G.FMTKD_PRODUK AND G.FMTJENISTARIF=A.FMPJENISTARIP '
    q += ' AND FMTTGL_BERLAKU in (SELECT MAX(FMTTGL_BERLAKU) AS TGL_AKHIR FROM TARIF WHERE FMTKD_PRODUK =A.FMPPRODUK_ID AND FMTJENISTARIF =A.FMPJENISTARIP) '
    q += ' WHERE A.FMPKLAS_ID = %s ORDER BY A.FMPPRODUK_ID '
    result = Globals().getDataQuery(q, [jenis_tarip,jenis_tarip,jenis_tarip,kode_induk])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def save_produk_kelas(request):
    kode_Induk = request.POST['kode_Induk']
    nama_Induk = request.POST['nama_Induk']
    Parent = request.POST['Parent']
    pos_produk = request.POST['pos_produk']
    level = request.POST['level']
    kode_tarip = request.POST['kode_tarip']
    kode_gol_tarip = request.POST['kode_gol_tarip']
    FMKGOLOK = request.POST['FMKGOLOK']
    status_aud = request.POST['status_aud']
    q = "exec AUD_MASTER_KLAS_PRODUK  %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s, %s "
    proc_param = [kode_Induk,nama_Induk, Parent,pos_produk, level, kode_tarip,kode_gol_tarip,FMKGOLOK, status_aud]
    # print (q % tuple(proc_param))
    result = Globals().getDataSP(q, proc_param,setIndex=2)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
        # print(result) SET INDEX DI GUNAKAN UNTUK MENENTUKAN SELECT TERAKHIR UNTUK OUTPUT
    return HttpResponse(json_data, content_type="application/json")

def getdataProduk_simpan(request):
    FMPPRODUK_ID = request.POST['kd_produk']
    FMPKLAS_ID = request.POST['kd_klas_produk']
    FMPPRODUKN = request.POST['nama_produk']
    FMPPOSFLAG = request.POST['FMPPOSFLAG']
    FMPUNITPRODUK = request.POST['kd_unit_produk']
    FMPUNITKLASPRODUK = request.POST['kd_klas_tarif']
    FMPJENISTARIP = request.POST['FMPJENISTARIP']
    FMPADMINISTRASI = request.POST['adm_rs']
    FMPJASADOKTER = request.POST['jasa_dokter']
    FMPPOSTMANUAL = request.POST['pos_posting']
    FMPHIDDEN = request.POST['produk_hidden']
    FMPPOSTPAKET = request.POST['pos_paket']
    FMPNOACC = request.POST['kd_no_akun']
    status_aud = request.POST['status_aud']
    q = "exec AUD_MASTER_PRODUK  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
    proc_param=[FMPPRODUK_ID,FMPKLAS_ID, FMPPRODUKN, FMPPOSFLAG,FMPUNITPRODUK,FMPUNITKLASPRODUK,FMPJENISTARIP,FMPADMINISTRASI,FMPJASADOKTER,FMPPOSTMANUAL,FMPHIDDEN,FMPPOSTPAKET,FMPNOACC, status_aud]
    # print (q % tuple(proc_param))
    result = Globals().getDataSP(q, proc_param,setIndex=2)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
        # print(result) SET INDEX DI GUNAKAN UNTUK MENENTUKAN SELECT TERAKHIR UNTUK OUTPUT
    return HttpResponse(json_data, content_type="application/json")

def tgl_produk_tarif(request):
    produk_id = request.GET['id_produk']
    jenis_tarip = request.GET['jenis_tarip']
    q = "SELECT (FMTTGL_BERLAKU) as cl from TARIF WHERE  "
    q += " FMTKD_PRODUK= %s AND FMTJENISTARIF = %s GROUP BY FMTTGL_BERLAKU ORDER BY FMTTGL_BERLAKU DESC "
    result = Globals().getDataQuery(q, [produk_id,jenis_tarip])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def get_produk_tarif(request):
    produk_id = request.GET['id_produk']
    jenis_tarip = request.GET['jenis_tarip']
    tgl_berlaku = request.GET['tgl_berlaku']
    q = "SELECT * FROM TARIF_KOMPONENT WHERE FMTCKD_PRODUK = %s AND  FMTCTGL_BERLAKU in (SELECT MAX(FMTCTGL_BERLAKU) AS TGL_AKHIR FROM TARIF_KOMPONENT WHERE FMTCKD_PRODUK = %s AND FMTCJENISTARIF = %s) AND FMTCJENISTARIF = %s"
    kom = Globals().getDataQuery(q, [produk_id,produk_id,jenis_tarip,jenis_tarip])
    q = 'SELECT * FROM Tarif_IUR WHERE FMITKD_PRODUK = %s AND FMITTGL_BERLAKU = %s AND FMITJENISTARIF = %s'
    iur = Globals().getDataQuery(q, [produk_id,tgl_berlaku,jenis_tarip])
    result = {
			'tarif_komponen' : kom,
			'tarif_iur' : iur,
		}
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def save_produk_tarif(request):
    kd_produk = request.POST['kd_produk']
    kd_klas_produk = request.POST['kd_klas_produk']
    tgl_berlaku = request.POST['tgl_berlaku']
    FMPJENISTARIP = request.POST['FMPJENISTARIP']
    total_tarif = request.POST['total_tarif']
    disc_konsumenpersen = request.POST['disc_konsumenpersen']
    fee_reselerpersen = request.POST['fee_reselerpersen']
    status_aud = request.POST['status_aud']
    list_tarif = json.loads(request.POST['data_tarif'])

    # pprint(list_tarif)

    q = "SET NOCOUNT ON;"
    q += "DECLARE @LIST_KOMPONENT MASTERCOMPONENT;"
    i = 0
    for x in list_tarif:
        if(list_tarif[i]['prosentase'] != ' ' and list_tarif[i]['prosentase'] != '0'):
            q += "INSERT INTO @LIST_KOMPONENT (FCDKD_COMPONENT, COMPONENT,  FCDTARIF, FCDDISCOUNT, FCDTARIFUPDOWN) VALUES ("
            q += "'" + list_tarif[i]['kd_component'] + "',"
            q += "'" + list_tarif[i]['kd_component'] + "',"
            q += "{}, ".format(list_tarif[i]['tarif'])
            q += "{}, ".format(list_tarif[i]['prosentase'])
            q += "0"
            q += ");"
        i+= 1
    # print(q)
    q += "exec AUD_MASTER_PRODUK_TARIF"
    q += " %s ,"
    q += " %s ,"
    q += " %s ,"
    q += " %s ,"
    q += " %s ,"
    q += " %s ,"
    q += " %s ,"
    q += " @LIST_KOMPONENT ,"
    q += " %s ;"

    proc_param = [kd_produk,kd_klas_produk,FMPJENISTARIP,tgl_berlaku,total_tarif,disc_konsumenpersen,fee_reselerpersen,status_aud]
    # pprint(proc_param)
    result = Globals().getDataSP(q, proc_param,setIndex=1)
    # pprint(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
        # print(result) SET INDEX DI GUNAKAN UNTUK MENENTUKAN SELECT TERAKHIR UNTUK OUTPUT
    return HttpResponse(json_data, content_type="application/json")