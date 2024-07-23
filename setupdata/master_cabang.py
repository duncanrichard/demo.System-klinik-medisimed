from django.shortcuts import render, redirect
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


def exit(request):
    return redirect("/")


def master_cabang(request):
    if Globals().isLogin(request):
        user_priv = request.session["user_priv"]
        user_privelege = request.session["user_priv"]
        navbars = Globals().getNavbars(user_priv, "IMMODERMA", "master_cabang")
        menubars = Globals().getMenubars(user_priv, "IMMODERMA", "master_cabang", "0")
        menubarsChild = Globals().getMenubars(
            user_priv, "IMMODERMA", "master_cabang", "1"
        )
        menubarCount = len(menubars)

        response = render(
            request,
            "setupdata/cabang/cabang.html",
            {
                "navbars": navbars,
                "menubars": menubars,
                "menubarsChild": menubarsChild,
                "menubarsType": 1,
                "count_": menubarCount,
                "list_": Globals().getSeparator(menubarCount),
                "user_id": user_privelege,
                "SERVER_INDO": getattr(env, "SERVER_INDO", ""),
            },
        )
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def getProvinsi(request):
    q = "select KD_PROPINSI,PROPINSIN from PROPINSI order by KD_PROPINSI "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getKabupaten(request):
    Provinsi_id = request.GET["Provinsi_id"]
    q = "select KD_KABUPATEN,KABUPATEN from KABUPATEN  where  KD_PROPINSI= %s order by KD_KABUPATEN "
    result = Globals().getDataQuery(q, [Provinsi_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getKecamatan(request):
    Kabupaten_id = request.GET["Kabupaten_id"]
    q = "select  KD_KECAMATAN,KECAMATAN,KD_KABUPATEN from KECAMATAN  where  KD_KABUPATEN= %s order by KD_KECAMATAN"
    result = Globals().getDataQuery(q, [Kabupaten_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getKelurahan(request):
    Kecamatan_id = request.GET["Kecamatan_id"]
    q = "select KD_KELURAHAN,KELURAHAN,KD_KECAMATAN from KELURAHAN  where  KD_KECAMATAN= %s  order by KD_KELURAHAN "
    result = Globals().getDataQuery(q, [Kecamatan_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def aud_cabang(request):
    cabang_id = request.POST["cabang_id"]
    nama_perusahaan = request.POST["nama_perusahaan"]
    alamat = request.POST["alamat"]
    idKabupaten = request.POST["idKelurahan"]
    namaKabupaten = request.POST["namaKabupaten"]
    kode_pos = request.POST["kode_pos"]
    sip = request.POST["sip"]
    email = request.POST["email"]
    kontak = request.POST["kontak"]
    jabatan = request.POST["jabatan"]
    no_telepon = request.POST["no_telepon"]
    no_wa = request.POST["no_wa"]
    kode_fktp = request.POST["kode_fktp"]
    consid = request.POST["consid"]
    Secret_Number = request.POST["Secret_Number"]
    Userkey = request.POST["Userkey"]
    user_pcare = request.POST["user_pcare"]
    password = request.POST["password"]
    user_icare = request.POST["user_icare"]
    password_icare = request.POST["password_icare"]
    client_id = request.POST["client_id"]
    organization_id = request.POST["organization_id"]
    Secret_key = request.POST["Secret_key"]
    SS_FHIR_longitude = request.POST["SS_FHIR_longitude"]
    SS_FHIR_latitude = request.POST["SS_FHIR_latitude"]
    SS_FHIR_website = request.POST["SS_FHIR_website"]
    statusMjkn = request.POST["statusMjkn"]

    try:
        q = "EXEC MST_CABANG %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
        result = Globals().getDataSP(
            q,
            [
                cabang_id,
                nama_perusahaan,
                alamat,
                idKabupaten,
                namaKabupaten,
                kode_pos,
                sip,
                email,
                kontak,
                jabatan,
                no_telepon,
                no_wa,
                kode_fktp,
                consid,
                Secret_Number,
                Userkey,
                user_pcare,
                password,
                user_icare,
                password_icare,
                client_id,
                organization_id,
                Secret_key,
                SS_FHIR_longitude,
                SS_FHIR_latitude,
                SS_FHIR_website,
                statusMjkn,
            ],
        )
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print("coba")


def open_cabang(request):
    cabang_id = request.session["kdCabang"]
    q = "select a.CABANG_ID,a.PERUSAHAAN,a.ALAMAT1,KOTA_ID,KOTA,KODE_POS,TELEPON,no_whatsapp,email,KONTAK,JABATAN,NPWP,TGLPENGUKUHAN,USING,a.ppkpelayanan,consid,secret,bpjs_userkey,userncc,passwordncc, "
    q += "ijinSIP,user_icare,password_icare,statusmjkn,client_id,organization_id,Secret_key,SS_FHIR_KD_CABANG,SS_FHIR_longitude,SS_FHIR_latitude,website,   "
    q += "b.KD_KELURAHAN,b.KELURAHAN,c.KD_KECAMATAN,c.KECAMATAN,isnull(d.KD_KABUPATEN,a.KOTA_ID) as KD_KABUPATEN,isnull(d.KABUPATEN,KOTA) as KABUPATEN,e.KD_PROPINSI,e.PROPINSIN from CABANG a "
    q += "left join KELURAHAN b on a.KOTA_ID=b.KD_KELURAHAN  "
    q += "left join KECAMATAN c on b.KD_KECAMATAN=c.KD_KECAMATAN "
    q += "left join KABUPATEN d on c.KD_KABUPATEN=d.KD_KABUPATEN "
    q += "left join PROPINSI e on d.KD_PROPINSI=e.KD_PROPINSI "
    q += "WHERE CABANG_ID= %s "
    result = Globals().getDataQuery(q, [cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
