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


def data_pasien(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "data_pasien")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "data_pasien", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "data_pasien", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/data_pasien/base.html', {
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

def getDataKelamin(request):
    idKelamin = request.GET['idKelamin']
    q = "select KD_KELAMIN,KELAMIN from JENIS_KELAMIN where KD_KELAMIN= %s "
    result = Globals().getDataQuery(q, [idKelamin])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getKelamin(request):
    id_Kelamin = '%' + request.GET['id_Kelamin'] + '%'
    nama_kelamin = '%' + request.GET['nama_kelamin'] + '%'
    q = "select KD_KELAMIN,KELAMIN from JENIS_KELAMIN  where KD_KELAMIN like %s and KELAMIN like %s"
    result = Globals().getDataQuery(q, [id_Kelamin, nama_kelamin])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataProvinsi(request):
    idProvinsi = request.GET['idProvinsi']
    q = "select KD_PROPINSI,PROPINSIN from PROPINSI where KD_PROPINSI= %s "
    result = Globals().getDataQuery(q, [idProvinsi])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getProvinsi(request):
    q = "select KD_PROPINSI,PROPINSIN from PROPINSI order by KD_PROPINSI "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataKabupaten(request):
    idKabupaten = request.GET['idKabupaten']
    q = "select KD_KABUPATEN,KABUPATEN from KABUPATEN where KD_KABUPATEN= %s "
    result = Globals().getDataQuery(q, [idKabupaten])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getKabupaten(request):
    Provinsi_id = request.GET['Provinsi_id'] 
    q = "select KD_KABUPATEN,KABUPATEN from KABUPATEN  where  KD_PROPINSI= %s order by KD_KABUPATEN "
    result = Globals().getDataQuery(q, [Provinsi_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataKecamatan(request):
    idKecamatan = request.GET['idKecamatan']
    q = "select  KD_KECAMATAN,KECAMATAN,KD_KABUPATEN from KECAMATAN where KD_KECAMATAN= %s "
    result = Globals().getDataQuery(q, [idKecamatan])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getKecamatan(request):
    Kabupaten_id = request.GET['Kabupaten_id'] 
    q = "select  KD_KECAMATAN,KECAMATAN,KD_KABUPATEN from KECAMATAN  where  KD_KABUPATEN= %s order by KD_KECAMATAN"
    result = Globals().getDataQuery(q, [Kabupaten_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataKelurahan(request):
    idKelurahan = request.GET['idKelurahan']
    q = "select KD_KELURAHAN,KELURAHAN,KD_KECAMATAN from KELURAHAN where KD_KELURAHAN= %s "
    result = Globals().getDataQuery(q, [idKelurahan])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getKelurahan(request):
    Kecamatan_id = request.GET['Kecamatan_id'] 
    q = "select KD_KELURAHAN,KELURAHAN,KD_KECAMATAN from KELURAHAN  where  KD_KECAMATAN= %s  order by KD_KELURAHAN "
    result = Globals().getDataQuery(q, [Kecamatan_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataReseler(request):
    idReseler = request.GET['idReseler']
    q = "select KD_RESELER, NAMA_RESELER, IDSPONSOR, NAMA_SPONSOR from RESELER where KD_RESELER= %s "
    result = Globals().getDataQuery(q, [idReseler])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getReseler(request):
    q = "select KD_RESELER, NAMA_RESELER, IDSPONSOR, NAMA_SPONSOR from RESELER  order by KD_RESELER "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataKlpPasien(request):
    idKlpPasien = request.GET['customerId']
    q = "select FMKCUST_ID,FMKCUSTN from KELOMPOKCUSTOMER where FMKCUST_ID= %s "
    result = Globals().getDataQuery(q, [idKlpPasien])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getKlpPasien(request):
    q = "select FMKCUST_ID,FMKCUSTN from KELOMPOKCUSTOMER  "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataCustomer(request):
    customerId = request.GET['customerId']
    q = "select A.CUSID,A.NAME,B.FMKCUST_ID,B.FMKCUSTN,B.FMKJENIS_TARIP from CUSTOMER A INNER JOIN KELOMPOKCUSTOMER B ON A.KELOMPOK_ID=B.FMKCUST_ID  where CUSID= %s "
    result = Globals().getDataQuery(q, [customerId])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getCustomer(request):
    idKlpPasien =  '%' + request.GET['idKlpPasien'] + '%' 
    q = "select A.CUSID,A.NAME,B.FMKCUST_ID,B.FMKCUSTN,B.FMKJENIS_TARIP from CUSTOMER A INNER JOIN KELOMPOKCUSTOMER B ON A.KELOMPOK_ID=B.FMKCUST_ID where KELOMPOK_ID like %s  "
    result = Globals().getDataQuery(q,[idKlpPasien])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataAgama(request):
    idAgama = request.GET['idAgama']
    q = "select KD_AGAMA, AGAMA from AGAMA where KD_AGAMA= %s "
    result = Globals().getDataQuery(q, [idAgama])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getAgama(request):
    q = "select KD_AGAMA, AGAMA from AGAMA   order by KD_AGAMA "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")  

def getDataPendidikan(request):
    idPendidikan = request.GET['idPendidikan']
    q = "select KD_PENDIDIKAN, PENDIDIKAN from PENDIDIKAN where KD_PENDIDIKAN= %s "
    result = Globals().getDataQuery(q, [idPendidikan])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getPendidikan(request):
    q = "select KD_PENDIDIKAN, PENDIDIKAN from PENDIDIKAN   order by KD_PENDIDIKAN "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json") 

def getDataGoldarah(request):
    idGoldarah = request.GET['idGoldarah']
    q = "select KD_DARAH,DARAH from GOL_DARAH where KD_DARAH= %s "
    result = Globals().getDataQuery(q, [idGoldarah])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getGoldarah(request):
    q = "select KD_DARAH,DARAH from GOL_DARAH   order by KD_DARAH "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataMarital(request):
    idMarital = request.GET['idMarital']
    q = "select KD_MARITAL,MARITAL from STATUSMARITAL where KD_MARITAL= %s "
    result = Globals().getDataQuery(q, [idMarital])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getMarital(request):
    q = "select KD_MARITAL,MARITAL from STATUSMARITAL   order by KD_MARITAL "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataPekerjaan(request):
    idPekerjaan = request.GET['idPekerjaan']
    q = "select KD_PEKERJAAN,PEKERJAAN from PEKERJAAN where KD_PEKERJAAN= %s "
    result = Globals().getDataQuery(q, [idPekerjaan])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getPekerjaan(request):
    q = "select KD_PEKERJAAN,PEKERJAAN from PEKERJAAN   order by KD_PEKERJAAN "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataSuku(request):
    idSuku = request.GET['idSuku']
    q = "select FMSKETERANGAN,FMSKODE from SUKU  where FMSKODE= %s "
    result = Globals().getDataQuery(q, [idSuku])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getSuku(request):
    q = "select FMSKETERANGAN,FMSKODE from SUKU    order by FMSKODE "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDataBahasa(request):
    idBahasa = request.GET['idBahasa']
    q = "select BAHASA_ID,BAHASA from BAHASA   where BAHASA_ID= %s "
    result = Globals().getDataQuery(q, [idBahasa])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getBahasa(request):
    q = "select BAHASA_ID,BAHASA from BAHASA    order by BAHASA_ID "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getPasien(request):
    search_name = '%'+request.GET['search_name']+'%'
    search_almt = '%'+request.GET['search_almt']+'%'
    search_kdpas = '%'+request.GET['search_kdpas']+'%'
    search_telp = '%'+request.GET['search_telp']+'%'
    cabang_id = request.session['kdCabang']
    pilihan = request.GET['pilihan']
    if pilihan == 'search_cabang_all':
        q = " select TOP 200 a.KD_PASIEN,NAMAPASIEN,ALAMAT,NAMA_KELUARGA, TELEPON from  PASIEN a where NAMAPASIEN like %s  "
        q += " and ALAMAT like %s and KD_PASIEN like %s AND TELEPON like %s   order by a.NAMAPASIEN "
        proc_param = [search_name,search_almt,search_kdpas,search_telp]
    else:
        q = " select TOP 200 a.KD_PASIEN,NAMAPASIEN,ALAMAT,NAMA_KELUARGA, TELEPON from  PASIEN a where NAMAPASIEN like %s  "
        q += " and ALAMAT like %s and KD_PASIEN like %s AND TELEPON like %s and (a.KD_ASAL_CABANG = %s)  order by a.NAMAPASIEN "
        proc_param = [search_name,search_almt,search_kdpas,search_telp,cabang_id]

    result = Globals().getDataQuery(q, proc_param)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getDataPasien(request):
    kdpas = request.GET['PasienId']
    cabang_id = request.session['kdCabang']
    q = "select  A.KD_PASIEN,NAMAPASIEN,ALAMAT,NAMA_KELUARGA, A.TELEPON,A.EMAIL,KD_POS,JENIS_KELAMIN,TEMPAT_LAHIR,TGL_LAHIR, "
    q += " A.KD_KELURAHAN,C.KELURAHAN AS NAMA_KELURAHAN,C.KD_KECAMATAN,C2.KECAMATAN AS NAMA_KECAMATAN, "
    q += " C2.KD_KABUPATEN,C3.KABUPATEN AS NAMA_KABUPATEN,C3.KD_PROPINSI,C4.PROPINSIN AS NAMA_PROPINSI, "
    q += " A.KETERANGAN,A.KD_RESELER,A.KD_ASAL_CABANG,M.NAMA_RESELER,N.PERUSAHAAN,A.KD_PERUSAHAAN,F.KELOMPOK_ID, "
    q += " A.AGAMA,A.KD_PENDIDIKAN,A.GOL_DARAH,A.STATUS_MARITA,A.KD_PEKERJAAN,A.SUKU,A.BAHASA,A.NO_ASURANSI, "
    q += " B.AGAMA as NAMA_AGAMA, D.PENDIDIKAN AS NAMA_PENDIDIKAN, E.PEKERJAAN AS NAMA_PEKERJAAN, "
    q += " F.NAME as NAMA_PERUSAHAAN, G.KELAMIN , H.MARITAL, I.DARAH, J.FMKCUSTN AS NAMA_ASURANSI, isnull(J.FMKJENIS_TARIP,'') AS JENIS_TARIF,K.BAHASA as NAMA_BAHASA,L.FMSKETERANGAN,O.NAMA_SUMBER  from  PASIEN as A "
    q += " LEFT JOIN AGAMA as B ON A.AGAMA = B.KD_AGAMA "
    q += " LEFT JOIN KELURAHAN as C ON A.KD_KELURAHAN = C.KD_KELURAHAN "
    q += " LEFT JOIN KECAMATAN as C2 ON C2.KD_KECAMATAN = C.KD_KECAMATAN "
    q += " LEFT JOIN KABUPATEN as C3 ON C3.KD_KABUPATEN = C2.KD_KABUPATEN "
    q += " LEFT JOIN PROPINSI as C4 ON C4.KD_PROPINSI = C3.KD_PROPINSI "
    q += " LEFT JOIN PENDIDIKAN as D ON A.KD_PENDIDIKAN = D.KD_PENDIDIKAN "
    q += " LEFT JOIN PEKERJAAN as E ON A.KD_PEKERJAAN = E.KD_PEKERJAAN "
    q += " LEFT JOIN CUSTOMER as F ON A.KD_PERUSAHAAN = F.CUSID "
    q += " LEFT JOIN JENIS_KELAMIN as G ON A.JENIS_KELAMIN  = G.KD_KELAMIN "
    q += " LEFT JOIN STATUSMARITAL as H ON A.STATUS_MARITA = H.KD_MARITAL "
    q += " LEFT JOIN GOL_DARAH as I ON A.GOL_DARAH = I.KD_DARAH "
    q += " LEFT JOIN KELOMPOKCUSTOMER as J ON F.KELOMPOK_ID = J.FMKCUST_ID "
    q += " LEFT JOIN BAHASA as K ON A.BAHASA = K.BAHASA_ID "
    q += " LEFT JOIN SUKU as L ON A.SUKU = L.FMSKODE "
    q += " LEFT JOIN RESELER as M ON A.KD_RESELER = M.KD_RESELER "
    q += " LEFT JOIN CABANG as N ON A.KD_ASAL_CABANG = N.CABANG_ID "
    q += " LEFT JOIN SUMBER as O ON A.KETERANGAN = O.SUMBER_ID "
    q += " where KD_PASIEN = %s  order by NAMAPASIEN "

    result = Globals().getDataQuery(q,[kdpas])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getlistPasien(request):
    cabang_id = request.session['kdCabang']
    q = "select  A.KD_PASIEN,NAMAPASIEN,ALAMAT,NAMA_KELUARGA, A.TELEPON,A.EMAIL,KD_POS,JENIS_KELAMIN,TEMPAT_LAHIR,TGL_LAHIR, "
    q += " A.KD_KELURAHAN,C.KELURAHAN AS NAMA_KELURAHAN,C.KD_KECAMATAN,C2.KECAMATAN AS NAMA_KECAMATAN, "
    q += " C2.KD_KABUPATEN,C3.KABUPATEN AS NAMA_KABUPATEN,C3.KD_PROPINSI,C4.PROPINSIN AS NAMA_PROPINSI, "
    q += " A.KETERANGAN,A.KD_RESELER,A.KD_ASAL_CABANG,M.NAMA_RESELER,N.PERUSAHAAN,A.KD_PERUSAHAAN,F.KELOMPOK_ID, "
    q += " A.AGAMA,A.KD_PENDIDIKAN,A.GOL_DARAH,A.STATUS_MARITA,A.KD_PEKERJAAN,A.SUKU,A.BAHASA,A.NO_ASURANSI, "
    q += " B.AGAMA as NAMA_AGAMA, D.PENDIDIKAN AS NAMA_PENDIDIKAN, E.PEKERJAAN AS NAMA_PEKERJAAN, "
    q += " F.NAME as NAMA_PERUSAHAAN, G.KELAMIN , H.MARITAL, I.DARAH, J.FMKCUSTN AS NAMA_ASURANSI, isnull(J.FMKJENIS_TARIP,'') AS JENIS_TARIF,K.BAHASA as NAMA_BAHASA,L.FMSKETERANGAN,O.NAMA_SUMBER  from  PASIEN as A "
    q += " LEFT JOIN AGAMA as B ON A.AGAMA = B.KD_AGAMA "
    q += " LEFT JOIN KELURAHAN as C ON A.KD_KELURAHAN = C.KD_KELURAHAN "
    q += " LEFT JOIN KECAMATAN as C2 ON C2.KD_KECAMATAN = C.KD_KECAMATAN "
    q += " LEFT JOIN KABUPATEN as C3 ON C3.KD_KABUPATEN = C2.KD_KABUPATEN "
    q += " LEFT JOIN PROPINSI as C4 ON C4.KD_PROPINSI = C3.KD_PROPINSI "
    q += " LEFT JOIN PENDIDIKAN as D ON A.KD_PENDIDIKAN = D.KD_PENDIDIKAN "
    q += " LEFT JOIN PEKERJAAN as E ON A.KD_PEKERJAAN = E.KD_PEKERJAAN "
    q += " LEFT JOIN CUSTOMER as F ON A.KD_PERUSAHAAN = F.CUSID "
    q += " LEFT JOIN JENIS_KELAMIN as G ON A.JENIS_KELAMIN  = G.KD_KELAMIN "
    q += " LEFT JOIN STATUSMARITAL as H ON A.STATUS_MARITA = H.KD_MARITAL "
    q += " LEFT JOIN GOL_DARAH as I ON A.GOL_DARAH = I.KD_DARAH "
    q += " LEFT JOIN KELOMPOKCUSTOMER as J ON F.KELOMPOK_ID = J.FMKCUST_ID "
    q += " LEFT JOIN BAHASA as K ON A.BAHASA = K.BAHASA_ID "
    q += " LEFT JOIN SUKU as L ON A.SUKU = L.FMSKODE "
    q += " LEFT JOIN RESELER as M ON A.KD_RESELER = M.KD_RESELER "
    q += " LEFT JOIN CABANG as N ON A.KD_ASAL_CABANG = N.CABANG_ID "
    q += " LEFT JOIN SUMBER as O ON A.KETERANGAN = O.SUMBER_ID "
    q += " where KD_ASAL_CABANG = %s  order by KD_PASIEN "
    print (q)
    result = Globals().getDataQuery(q,[cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def GUD_PASIEN(request):
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
    USERRS = request.session['user_id']
    status_aud = request.POST['status_aud']

    try:
        q = "EXEC GUD_PASIEN  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
        result = Globals().getDataSP(
            q, [KD_PASIEN, KD_KELURAHAN, KD_PENDIDIKAN,KD_PEKERJAAN, KD_PERUSAHAAN, NAMAPASIEN, TGL_LAHIR, GOL_DARAH, JENIS_KELAMIN, STATUS_MARITA, 
                AGAMA,ALAMAT, TELEPON, KD_POS,NO_ASURANSI, KETERANGAN, NAMA_KELUARGA, TEMPAT_LAHIR, BAHASA, SUKU, EMAIL, 
                KD_RESELER, USERRS,status_aud])
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print('coba')