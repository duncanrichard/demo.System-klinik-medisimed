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
    id_Provinsi = '%' + request.GET['id_Provinsi'] + '%'
    nama_Provinsi = '%' + request.GET['nama_Provinsi'] + '%'
    q = "select KD_PROPINSI,PROPINSIN from PROPINSI  where KD_PROPINSI like %s and PROPINSIN like %s"
    result = Globals().getDataQuery(q, [id_Provinsi, nama_Provinsi])
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
    id_Kabupaten = '%' + request.GET['id_Kabupaten'] + '%'
    nama_Kabupaten = '%' + request.GET['nama_Kabupaten'] + '%'
    q = "select KD_KABUPATEN,KABUPATEN from KABUPATEN  where KD_KABUPATEN like %s and KABUPATEN like %s and KD_PROPINSI= %s "
    result = Globals().getDataQuery(q, [id_Kabupaten, nama_Kabupaten,Provinsi_id])
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
    id_Kecamatan = '%' + request.GET['id_Kecamatan'] + '%'
    nama_Kecamatan = '%' + request.GET['nama_Kecamatan'] + '%'
    q = "select  KD_KECAMATAN,KECAMATAN,KD_KABUPATEN from KECAMATAN  where KD_KECAMATAN like %s and KECAMATAN like %s and KD_KABUPATEN= %s "
    result = Globals().getDataQuery(q, [id_Kecamatan, nama_Kecamatan,Kabupaten_id])
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
    id_Kelurahan = '%' + request.GET['id_Kelurahan'] + '%'
    nama_Kelurahan = '%' + request.GET['nama_Kelurahan'] + '%'
    q = "select KD_KELURAHAN,KELURAHAN,KD_KECAMATAN from KELURAHAN  where KD_KELURAHAN like %s and KELURAHAN like %s and KD_KECAMATAN= %s "
    result = Globals().getDataQuery(q, [id_Kelurahan, nama_Kelurahan,Kecamatan_id])
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

def getPasien(request):
    search_name = '%'+request.GET['search_name']+'%'
    search_almt = '%'+request.GET['search_almt']+'%'
    search_kdpas = '%'+request.GET['search_kdpas']+'%'
    search_telp = '%'+request.GET['search_telp']+'%'
    q = " select TOP 200 a.KD_PASIEN,NAMAPASIEN,ALAMAT,NAMA_KELUARGA, TELEPON from  PASIEN a where NAMAPASIEN like %s  "
    q += " and ALAMAT like %s and KD_PASIEN like %s AND TELEPON like %s  order by a.NAMAPASIEN "

    proc_param = [search_name,search_almt,search_kdpas,search_telp]
    # pprint(proc_param)
    result = Globals().getDataQuery(q, proc_param)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getDataPasien(request):
    kdpas = request.GET['KD_PASIEN']
    q = "select TOP 5 A.*,B.AGAMA as NAMA_AGAMA,C.KELURAHAN AS NAMA_KELURAHAN, D.PENDIDIKAN AS NAMA_PENDIDIKAN, E.PEKERJAAN AS NAMA_PEKERJAAN, "
    q += " F.NAME as NAMA_PERUSAHAAN, G.KELAMIN AS JK, H.MARITAL, I.DARAH, J.FMKCUSTN AS NAMA_ASURANSI, J.FMKJENIS_TARIP AS JENIS_TARIF,K.BAHASA,L.FMSKETERANGAN  from  PASIEN as A "
    q += " LEFT JOIN AGAMA as B ON A.AGAMA = B.KD_AGAMA "
    q += " LEFT JOIN KELURAHAN as C ON A.KD_KELURAHAN = C.KD_KELURAHAN "
    q += " LEFT JOIN PENDIDIKAN as D ON A.KD_PENDIDIKAN = D.KD_PENDIDIKAN "
    q += " LEFT JOIN PEKERJAAN as E ON A.KD_PEKERJAAN = E.KD_PEKERJAAN "
    q += " LEFT JOIN CUSTOMER as F ON A.KD_PERUSAHAAN = F.CUSID "
    q += " LEFT JOIN JENIS_KELAMIN as G ON A.JENIS_KELAMIN  = G.KD_KELAMIN "
    q += " LEFT JOIN STATUSMARITAL as H ON A.STATUS_MARITA = H.KD_MARITAL "
    q += " LEFT JOIN GOL_DARAH as I ON A.GOL_DARAH = I.KD_DARAH "
    q += " LEFT JOIN KELOMPOKCUSTOMER as J ON A.KD_ASURANSI = J.FMKCUST_ID "
    q += " LEFT JOIN BAHASA as K ON A.BAHASA = K.BAHASA_ID "
    q += " LEFT JOIN SUKU as L ON A.SUKU = L.FMSKODE "
    q += " where KD_PASIEN = %s order by NAMAPASIEN "

    result = Globals().getDataQuery(q,[kdpas])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")