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


def jasareseller001(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "jasareseller001")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "jasareseller001", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "jasareseller001", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/printjasareseller001/printjasareseller001.html', {
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
    kodereseller_dari = request.GET['kodereseller_dari']
    kodereseller_sampai = request.GET['kodereseller_sampai']
    tanggal_dr = request.GET['tanggal_dr']
    tanggal_sd = request.GET['tanggal_sd']
    KD_CABANG= request.session['kdCabang']
    q = "select  A.FTNO_TRANSAKSI as NO_TRANSAKSI,a.FTNO_KUNJUNGAN as NO_REGISTRASI,a.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN, "
    q += "d.FDTNOMER as NO,d.FDTKD_PRODUK as ID_PRODUK,d.FDTKDPRODUKN as NAMA_PRODUK,FDTQTY as QTY,d.FDTHARGA as HARGA,FDT_DISCKONSUMEN as DISCKONSUMEN,d.FDT_DISC as DISC,d.FDT_DISC2 as DISC2,d.FDT_DISC3 as DISC3,d.FDT_DISC4 as DISC4, "
    q += "d.FD_DISCRESELER as FEE_MEDIS,d.FDTNO_FAKTUR as NOFAKTUR,d.FDTJENISTRANSAKSI,a.USERRS,a.UPDATERS,a.KD_RESELER,e.NAMA_RESELER,a.FKUNCI "
    q += "from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI  "
    q += "inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN   "
    q += "inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI "
    q += "inner join RESELER e on a.KD_RESELER=e.KD_RESELER "
    q += "where (FD_DISCRESELER<>0 and a.KD_RESELER>=%s AND a.KD_RESELER<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
    result = Globals().getDataQuery(q, [kodereseller_dari,kodereseller_sampai,tanggal_dr,tanggal_sd,KD_CABANG])

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
