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



def exit(request):
    return redirect("/")


def master_dokter(request):
    if Globals().isLogin(request):
        user_priv = request.session["user_priv"]
        user_privelege = request.session["user_priv"]
        navbars = Globals().getNavbars(user_priv, "IMMODERMA", "master_dokter")
        menubars = Globals().getMenubars(user_priv, "IMMODERMA", "master_dokter", "0")
        menubarsChild = Globals().getMenubars(
            user_priv, "IMMODERMA", "master_dokter", "1"
        )
        menubarCount = len(menubars)

        response = render(
            request,
            "setupdata/dokter/base.html",
            {
                "navbars": navbars,
                "menubars": menubars,
                "menubarsChild": menubarsChild,
                "menubarsType": 1,
                "count_": menubarCount,
                "list_": Globals().getSeparator(menubarCount),
                "user_id": user_privelege,
            },
        )
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def aud_dokter(request):
    far_kode_dokter = request.POST["far_kode_dokter"]
    far_nama_dokter = request.POST["far_nama_dokter"]
    far_jabatan_dokter = request.POST["far_jabatan_dokter"]
    far_id_dokter_bpjs = request.POST["far_id_dokter_bpjs"]
    far_kode_nip = request.POST["far_kode_nip"]
    far_sip = request.POST["far_sip"]
    far_kode_antri = request.POST["far_kode_antri"]
    far_kode_bpjs = request.POST["far_kode_bpjs"]
    far_no_telepon = request.POST["far_no_telepon"]
    aktif = request.POST["aktif"]
    user = request.session["user_id"]
    cabang_id = request.session["kdCabang"]
    status_aud = request.POST["status_aud"]

    try:
        q = "EXEC MST_AUD_DOKTER %s,%s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s"
        result = Globals().getDataSP(
            q,
            [
                far_kode_dokter,
                far_nama_dokter,
                far_jabatan_dokter,
                far_id_dokter_bpjs,
                far_kode_nip,
                far_sip,
                far_kode_antri,
                far_kode_bpjs,
                far_no_telepon,
                aktif,
                user,
                cabang_id,
                status_aud,
            ],
        )
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print("coba")


def open_dokter(request):
    cabang_id = request.session["kdCabang"]
    q = "SELECT FMDDOKTER_ID,FMDDOKTERN,FMDJABATAN,FMDDOKTER_ID_BPJS,FMDNIP,KODEDOKTER,KODEDPJP,FMDNOTELP,SIP,FMDSTATUS,KD_CABANG,USERRS,UPDATERS,SSFHIR_KD_DOKTER FROM DOKTER  WHERE KD_CABANG= %s order by FMDDOKTERN"
    result = Globals().getDataQuery(q, [cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def Listdokter(request):
    parameter1 = "1"
    parameter2 = "100"
    # -------
    kdCabang = request.session["kdCabang"]
    # BPJS_USERPCARE=request.session['BPJS_USERPCARE']
    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/dokter/" + parameter1 + "/" + parameter2
    method = "get"
    data = Globals().bridgeBPJS(url, method, kdCabang)
    if data["metaData"]["code"] == 200:
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")
