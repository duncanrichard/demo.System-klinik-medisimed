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
import bcrypt

def exit(request):
    return redirect('/')

def master_voucher(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "master_voucher")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "master_voucher", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "master_voucher", '1')
        menubarCount = len(menubars)

        response = render(request, 'setupdata/voucher/base.html', {
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

def aud_voucher(request):
    kode_voucher = request.POST['kode_voucher']
    tgl_transaksi= request.POST['tgl_transaksi']
    nama_voucher = request.POST['nama_voucher']
    jumlah_voucher= request.POST['jumlah_voucher']
    tgl_expired= request.POST['tgl_expired']
    nilai_voucher = request.POST['nilai_voucher']
    aktif = request.POST['aktif']
    USERRS = request.session['user_id']
    status_aud = request.POST['status_aud']

    try:
        q = "EXEC MST_AUD_voucher %s, %s, %s, %s, %s, %s, %s, %s, %s "
        result = Globals().getDataSP(q, [kode_voucher,tgl_transaksi, nama_voucher,jumlah_voucher,tgl_expired,nilai_voucher,aktif,USERRS,status_aud])
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print('coba')


def open_voucher(request):
    no_bukti = '%'+request.GET['no_bukti']+'%'
    mutasi_nama = '%'+request.GET['mutasi_nama']+'%'
    tipe = request.GET['tipe']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")
    if(tipe == 'mutasi_by_bulan'):
        q =  "SELECT  b.NILAI_VOUCHER, b.STATUS_VOUCHER AS AKTIF, b.NORM_VOUCHER,convert(varchar, b.EXPR_VOUCHER, 23) as EXPR_VOUCHER, b.GROUP_VOUCHER, b.UPDATERS, "
        q += "(select count(*) as jumlah from VOUCHER_PASIEN a where a.GROUP_VOUCHER=b.GROUP_VOUCHER) as jumlah_voucher "
        q +="from VOUCHER_PASIEN b where (GROUP_VOUCHER like %s)  and "
        q += "(NORM_VOUCHER like %s) and (YEAR(UPDATERS) = %s) and (MONTH(UPDATERS) = %s) "
        q += "group by b.NILAI_VOUCHER, b.STATUS_VOUCHER, b.NORM_VOUCHER,b.EXPR_VOUCHER, b.GROUP_VOUCHER, b.UPDATERS order by b.GROUP_VOUCHER"
        result = Globals().getDataQuery(q, [no_bukti, mutasi_nama, tanggal.year, tanggal.month])
    else:
        q =  "SELECT b.NILAI_VOUCHER, b.STATUS_VOUCHER AS AKTIF, b.NORM_VOUCHER,convert(varchar, b.EXPR_VOUCHER, 23) as EXPR_VOUCHER, b.GROUP_VOUCHER, b.UPDATERS, "
        q += "(select count(*) as jumlah from VOUCHER_PASIEN a where a.GROUP_VOUCHER=b.GROUP_VOUCHER) as jumlah_voucher "
        q +="from VOUCHER_PASIEN b where (GROUP_VOUCHER like %s)  and "
        q += "(NORM_VOUCHER like %s) and (convert(varchar,UPDATERS, 23)= %s)  "
        q += "group by b.NILAI_VOUCHER, b.STATUS_VOUCHER, b.NORM_VOUCHER,b.EXPR_VOUCHER, b.GROUP_VOUCHER, b.UPDATERS order by b.GROUP_VOUCHER"
        result = Globals().getDataQuery(q, [no_bukti,mutasi_nama , tanggal])

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def buka_voucher(request):
    namagroupvoucher =  request.GET['namagroupvoucher']
    q =  "SELECT b.NO_VOUCHER,TGL_TRANSAKSI, b.NILAI_VOUCHER, b.STATUS_VOUCHER AS AKTIF, b.NORM_VOUCHER, b.EXPR_VOUCHER, b.GROUP_VOUCHER, b.USERRS, b.UPDATERS, "
    q += "(select count(*) as jumlah from VOUCHER_PASIEN a where a.GROUP_VOUCHER=b.GROUP_VOUCHER) as jumlah_voucher "
    q += "FROM VOUCHER_PASIEN b WHERE b.GROUP_VOUCHER= %s order by b.NO_VOUCHER"
    result = Globals().getDataQuery(q,[namagroupvoucher])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
