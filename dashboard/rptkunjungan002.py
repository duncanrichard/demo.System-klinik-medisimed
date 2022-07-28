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


def rptkunjungan002(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "rptkunjungan002")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "rptkunjungan002", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "rptkunjungan002", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/printkunjungan002/printkunjungan002.html', {
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

def proses_excel(request):
    tanggal_dr = request.GET['tanggal_dr']
    tanggal_sd = request.GET['tanggal_sd']
    KD_CABANG= request.session['kdCabang']
    q = "select ROW_NUMBER() OVER(ORDER BY FDTKDPRODUKN) AS NO, d.FDTKD_PRODUK as ID_TREATMENT,d.FDTKDPRODUKN as NAMA_TREATMENT,sum(FDTQTY) as QTY, "
    q += "d.FDTHARGA  as HARGA,(sum(FDTQTY)*d.FDTHARGA) as JUMLAH,(sum(FDTQTY)*d.FDTHARGA)-(select sum(dbo.fungsiCalculasiDeposit(FDTHARGA,1,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4))) AS DISCOUNT "
    q += ",(select sum(dbo.fungsiCalculasiDeposit(FDTHARGA,1,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4))) as TOTAL "
    q += "from TRANSAKSIPASIEN c inner join TRANSAKSIPASIEND d on c.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI  "
    q += "where (c.FTTGL_TRANSAKSI >= %s and FTTGL_TRANSAKSI<=%s  ) and (c.KD_CABANG = %s)  "
    q += "group by  d.FDTKD_PRODUK,d.FDTKDPRODUKN,d.FDTHARGA  "
    q += "order by FDTKDPRODUKN "
    result = Globals().getDataQuery(q, [tanggal_dr,tanggal_sd,KD_CABANG])


    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
