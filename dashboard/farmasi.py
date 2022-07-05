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
    q += "WHERE  (FDDNO_TRANSAKSI = f.KPNO_TRANSAKSI)) AS KODE_DOKTER, "
    q += "(SELECT  TOP (1) e.FMDDOKTERN "
    q += "FROM   TRANSAKSIDOKTERD AS c INNER JOIN "
    q += "DOKTER AS e ON c.FDDKD_DOKTER = e.FMDDOKTER_ID "
    q += "WHERE (c.FDDNO_TRANSAKSI = f.KPNO_TRANSAKSI)) AS NAMA_DOKTER, f.KD_RESELER, h.NAMA_RESELER "
    q += "FROM   PASIEN AS a INNER JOIN "
    q += "KUNJUNGANPASIEN AS f ON a.KD_PASIEN = f.KPKD_PASIEN LEFT OUTER JOIN "
    q += "RESELER AS h ON h.KD_RESELER = f.KD_RESELER "
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

