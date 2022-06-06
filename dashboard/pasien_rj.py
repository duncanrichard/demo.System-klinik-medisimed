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


def pasien_rj(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "pasien_rj")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "pasien_rj", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "pasien_rj", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/pasien_rj/base.html', {
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

def cekRMterakhir(request):
    KD_CABANG= request.session['kdCabang']
    qlastnorm = "SELECT MAX(LTRIM(RTRIM(SEQNO))) as no_rm FROM AUTONUM WHERE FORMC = '01' and BRANCH= %s "
    lastnorm = Globals().getDataQuery(qlastnorm,[KD_CABANG])
    json_data = json.dumps(lastnorm[0], cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def AUD_PASIENRJ(request):
    KD_PASIEN = request.POST['KD_PASIEN']
    KD_KELURAHAN = request.POST['KD_KELURAHAN']
    KD_PENDIDIKAN = request.POST['KD_PENDIDIKAN']
    KD_PEKERJAAN = request.POST['KD_PEKERJAAN']
    KD_PERUSAHAAN = request.POST['KD_PERUSAHAAN']
    NAMAPASIEN = request.POST['NAMAPASIEN']
    TGL_LAHIR = request.POST['TGL_LAHIR']
    GOL_DARAH = request.POST['GOL_DARAH']
    JENIS_KELAMIN = request.POST['JENIS_KELAMIN']
    STATUS_MARITA = request.POST['STATUS_MARITA']

    AGAMA = request.POST['AGAMA']
    ALAMAT = request.POST['ALAMAT']
    TELEPON = request.POST['TELEPON']
    KD_POS = request.POST['KD_POS']
    NO_ASURANSI = request.POST['NO_ASURANSI']
    KETERANGAN = request.POST['KETERANGAN']
    NAMA_KELUARGA = request.POST['NAMA_KELUARGA']
    TEMPAT_LAHIR = request.POST['TEMPAT_LAHIR']
    BAHASA = request.POST['BAHASA']
    SUKU = request.POST['SUKU']
    EMAIL = request.POST['EMAIL']

    KD_RESELER = request.POST['KD_RESELER']
    KD_ASAL_CABANG= request.POST['KD_ASAL_CABANG']

    USERRS = request.session['user_id']
    status_aud = request.POST['status_aud']

    TGL_PERIKSA= request.POST['TGL_PERIKSA']
    NO_TRANSAKSI= request.POST['NO_TRANSAKSI']

    try:
        q = "EXEC AUD_KUNJUNGAN_PASIEN  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
        param = [KD_PASIEN, KD_KELURAHAN, KD_PENDIDIKAN,KD_PEKERJAAN, KD_PERUSAHAAN, NAMAPASIEN, TGL_LAHIR, GOL_DARAH, JENIS_KELAMIN, STATUS_MARITA, 
                AGAMA,ALAMAT, TELEPON, KD_POS,NO_ASURANSI, KETERANGAN, NAMA_KELUARGA, TEMPAT_LAHIR, BAHASA, SUKU, EMAIL, 
                KD_RESELER, USERRS,TGL_PERIKSA,NO_TRANSAKSI,KD_ASAL_CABANG,status_aud]
        # print (q % tuple(param))
        result = Globals().getDataSP(
            q, param,setIndex=2)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        # print(result) SET INDEX DI GUNAKAN UNTUK MENENTUKAN SELECT TERAKHIR UNTUK OUTPUT
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)

def getDaftarPasien(request):
    no_bukti = '%'+request.GET['no_bukti']+'%'
    pasien = '%'+request.GET['pasien']+'%'
    nama_pasien = '%'+request.GET['nama_pasien']+'%'
    tipe = request.GET['tipe']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")
    idAsal_cabang= request.GET['idAsal_cabang']

    if(tipe == 'mutasi_by_bulan'):
        q = "select top 100  a.KPKD_PASIEN,a.KD_RESELER,a.KPNO_TRANSAKSI,a.KD_CABANG ,b.NAMAPASIEN,b.ALAMAT, convert(varchar, KPTGL_PERIKSA, 23) as TANGGAL "
        q +="from KUNJUNGANPASIEN a inner join PASIEN b on a.KPKD_PASIEN=b.KD_PASIEN where (KPNO_TRANSAKSI like %s) and (KPKD_PASIEN like %s) and "
        q += "(NAMAPASIEN like %s) and (YEAR(KPTGL_PERIKSA) = %s) and (MONTH(KPTGL_PERIKSA) = %s) and (a.KD_CABANG = %s) "
        result = Globals().getDataQuery(q, [no_bukti, pasien, nama_pasien, tanggal.year, tanggal.month,idAsal_cabang])
    else:
        q = "select top 100 a.KPKD_PASIEN,a.KD_RESELER,a.KPNO_TRANSAKSI,a.KD_CABANG ,b.NAMAPASIEN,b.ALAMAT, convert(varchar, KPTGL_PERIKSA, 23) as TANGGAL "
        q +="from KUNJUNGANPASIEN a inner join PASIEN b on a.KPKD_PASIEN=b.KD_PASIEN  where (KPNO_TRANSAKSI like %s) and (KPKD_PASIEN like %s) and "
        q += "(NAMAPASIEN like %s) and (KPTGL_PERIKSA = %s  ) and (a.KD_CABANG = %s) "
        result = Globals().getDataQuery(q, [no_bukti, pasien, nama_pasien, tanggal,idAsal_cabang])


    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")