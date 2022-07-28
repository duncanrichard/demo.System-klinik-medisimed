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


def rptkunjungan001(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "rptkunjungan001")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "rptkunjungan001", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "rptkunjungan001", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/printkunjungan001/printkunjungan001.html', {
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
    q = "select a.KPKD_PASIEN,a.KD_RESELER,a.KPNO_TRANSAKSI,a.KD_CABANG ,b.NAMAPASIEN,b.ALAMAT, convert(varchar, KPTGL_PERIKSA, 23) as TANGGAL "
    q += ",b.TELEPON,g.NAMA_SUMBER "
    q += ",d.KELURAHAN,e.KECAMATAN,f.KABUPATEN "
    q += ",c.NAMA_RESELER,c.NAMA_SPONSOR "
    q += "from KUNJUNGANPASIEN a inner join PASIEN b on a.KPKD_PASIEN=b.KD_PASIEN    "
    q += "left join RESELER c on a.KD_RESELER=c.KD_RESELER   "
    q += "left join KELURAHAN d on b.KD_KELURAHAN=d.KD_KELURAHAN "
    q += "left join KECAMATAN e on d.KD_KECAMATAN=e.KD_KECAMATAN "
    q += "left join KABUPATEN f on e.KD_KABUPATEN=f.KD_KABUPATEN "
    q += "left join SUMBER g on g.SUMBER_ID=b.KETERANGAN "
    q += "where (KPTGL_PERIKSA >= %s and KPTGL_PERIKSA<=%s  ) and (a.KD_CABANG = %s)  "
    q += "order by KPTGL_PERIKSA "
        
    result = Globals().getDataQuery(q, [tanggal_dr,tanggal_sd,KD_CABANG])


    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
