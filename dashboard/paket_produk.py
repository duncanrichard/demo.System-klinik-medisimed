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


def paket_produk(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "paket_produk")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "paket_produk", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "paket_produk", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/paket_produk/base.html', {
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

def SP_AUD_PAKET(request):
    # DETAIL
    FD_NO = json.loads(request.POST['FD_NO'])
    FD_ID_PRODUK = json.loads(request.POST['FD_ID_PRODUK'])
    FD_NAMA_PRODUK = json.loads(request.POST['FD_NAMA_PRODUK'])
    FD_HARGA = json.loads(request.POST['FD_HARGA'])
    FD_QTY = json.loads(request.POST['FD_QTY'])
    FD_DISC = json.loads(request.POST['FD_DISC'])
    FD_DISC2 = json.loads(request.POST['FD_DISC2'])
    FD_DISC3 = json.loads(request.POST['FD_DISC3'])
    FD_DISC4 = json.loads(request.POST['FD_DISC4'])
    FD_DISCKONSUMEN = json.loads(request.POST['FD_DISCKONSUMEN'])

    # header
    FH_BUKTI_ID = request.POST['FH_BUKTI_ID']
    FH_DATE = request.POST['FH_DATE']
    FH_NAMA_PAKET = request.POST['FH_NAMA_PAKET']
    FH_NUM_KUNJUNGAN = request.POST['FH_NUM_KUNJUNGAN']
    FH_PAKET_AKTIF = request.POST['FH_PAKET_AKTIF']

    USERRS = request.session['user_id']
    KD_CABANG= request.session['kdCabang']
    status_aud = request.POST['StatusAUD']

    q = "SET NOCOUNT ON;"
    q += "DECLARE @LIST_TRANSAKSI TRANSAKSID;"
    q += "DECLARE @NOW datetime; "
    q += "SET @NOW = GETDATE(); "

    proc_param = []
    i = 0
    for x in FD_NO:
        q += "INSERT INTO @LIST_TRANSAKSI (NO, ID_PODUK, NAMA_PRODUK, HARGA, QTY, DISC, DISC2, DISC3, DISC4, DISCKONSUMEN, BUKTI_ID) "
        q += "VALUES ("
        q += FD_NO[i] + ","
        q += "'" + FD_ID_PRODUK[i] + "',"
        q += "'" + FD_NAMA_PRODUK[i] + "',"
        q += FD_HARGA[i] + ","
        q += FD_QTY[i] + ","
        q += FD_DISC[i] + ","
        q += FD_DISC2[i] + ","
        q += FD_DISC3[i] + ","
        q += FD_DISC4[i] + ","
        q += FD_DISCKONSUMEN[i] + ","
        q += "'" + FH_BUKTI_ID + "');"
        i += 1



    q += "EXEC IMD_AUD_PAKET_PRODUK "
    q += "'" + FH_BUKTI_ID + "',"
    q += "'" + FH_DATE + "',"
    q += "'" + FH_NAMA_PAKET + "',"
    q += "'" + FH_NUM_KUNJUNGAN + "',"
    q += "'" + FH_PAKET_AKTIF + "',"
    q += "'" + USERRS + "',"
    q += "'" + status_aud + "', "
    q += "@LIST_TRANSAKSI"

    if (status_aud=='D') :
        user = {
        'user_id': request.session['user_id'],
        'user_name': request.session['user_name'],
        'user_priv': request.session['user_priv'],
        }
        data = []
        data.append({"query": "select * from PRODUK_PAKET where FMPKKD_PAKET = '" + FH_BUKTI_ID + "'"})
        data.append({"query": "select * from PRODUK_PAKETD where FMPDKD_PAKET = '" + FH_BUKTI_ID + "'"})
        
        Globals().create_log('Hapus LogDelete.txt', 'IMMODERMA', data, user)
    try:
        result = Globals().getDataSP(q)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)

def getTransaksi(request):
    no_bukti = '%'+request.GET['no_bukti']+'%'
    nama_produk = '%'+request.GET['nama_produk']+'%'
    tipe = request.GET['tipe']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")

    if(tipe == 'mutasi_by_bulan'):
        q = "select  top 100 a.FMPKKD_PAKET,a.FMPKPAKETN,convert(varchar, a.FMPTGL, 23) as TANGGAL  "
        q +="from PRODUK_PAKET a  "
        q +="where (FMPKKD_PAKET like %s) and  "
        q += "(FMPKPAKETN like %s) and (YEAR(FMPTGL) = %s) and (MONTH(FMPTGL) = %s) "
        result = Globals().getDataQuery(q, [no_bukti, nama_produk, tanggal.year, tanggal.month])
    else:
        q = "select  top 100 a.FMPKKD_PAKET,a.FMPKPAKETN,convert(varchar, a.FMPTGL, 23) as TANGGAL "
        q +="from PRODUK_PAKET a "
        q +="where (FMPKKD_PAKET like %s) and "
        q += "(FMPKPAKETN like %s) and (FMPTGL = %s )"
        result = Globals().getDataQuery(q, [no_bukti, nama_produk, tanggal])

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getpaketprodukByBukti(request):
    no_bukti = request.GET['no_bukti']
    q = "select ROW_NUMBER() OVER(ORDER BY FMPDKD_PRODUK) AS NO,a.FMPKKD_PAKET,a.FMPKPAKETN,c.FMPPRODUKN as NAMA_PRODUK,a.USERRS,a.UPDATERS,a.FMPKQTY,a.FMPKSTATUS,convert(varchar, a.FMPTGL, 23) as TANGGAL, "
    q += "b.FMPDKD_PRODUK as ID_PRODUK,b.FMPDQTY as QTY,b.FMPDTARIF as HARGA,b.FMPD_DISCKONSUMEN as DISCKONSUMEN,b.FMPD_DISC as DISC,b.FMPD_DISC2 as DISC2,b.FMPD_DISC3 as DISC3,b.FMPD_DISC4 as DISC4  "
    q += "from PRODUK_PAKET a inner join PRODUK_PAKETD b on a.FMPKKD_PAKET=b.FMPDKD_PAKET "
    q += "inner join PRODUK c on b.FMPDKD_PRODUK=c.FMPPRODUK_ID  "
    q += "where (FMPKKD_PAKET=%s) "
    result = Globals().getDataQuery(q, [no_bukti])

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
