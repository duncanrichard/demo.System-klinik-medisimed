from django.shortcuts import render,redirect
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from urllib.parse import unquote
from inspect import getmembers
from pprint import pprint
from IMMODERMA.globals import Globals
from IMMODERMA.config import env
from datetime import datetime
from django.urls import include, re_path as url
from django.db import transaction



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
    hidden = request.POST.get("hidden", "0")
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
        dokter_id = far_kode_dokter
        if result and status_aud != "D":
            dokter_id = result[0].get("DOKTER_ID", dokter_id)
        if dokter_id and status_aud != "D":
            hidden = 1 if str(hidden) == "1" else 0
            # The visibility row must use the branch stored on the doctor
            # record.  Session branch codes and legacy doctor branch codes can
            # have different formatting (for example, 001 versus 1), which
            # otherwise makes the saved row impossible to read back.
            branch_row = Globals().getDataQuery(
                "SELECT TOP (1) KD_CABANG FROM DOKTER WHERE FMDDOKTER_ID = %s "
                "ORDER BY CASE WHEN KD_CABANG = %s THEN 0 ELSE 1 END",
                [dokter_id, cabang_id],
            )
            visibility_branch = branch_row[0]["KD_CABANG"] if branch_row else cabang_id
            with transaction.atomic():
                Globals().executeQuery(
                    "IF EXISTS (SELECT 1 FROM NAKES_PEMBELIAN_VISIBILITY "
                    "WHERE nakes_type = %s AND nakes_id = %s AND kd_cabang = %s) "
                    "UPDATE NAKES_PEMBELIAN_VISIBILITY SET is_hidden = %s, updated_by = %s, "
                    "updated_at = SYSUTCDATETIME() WHERE nakes_type = %s AND nakes_id = %s AND kd_cabang = %s "
                    "ELSE INSERT INTO NAKES_PEMBELIAN_VISIBILITY "
                    "(nakes_type, nakes_id, kd_cabang, is_hidden, updated_by) VALUES (%s, %s, %s, %s, %s)",
                    [
                        "DOKTER", dokter_id, visibility_branch, hidden, user,
                        "DOKTER", dokter_id, visibility_branch,
                        "DOKTER", dokter_id, visibility_branch, hidden, user,
                    ],
                )
                saved_visibility = Globals().getDataQuery(
                    "SELECT is_hidden FROM NAKES_PEMBELIAN_VISIBILITY "
                    "WHERE nakes_type = %s AND nakes_id = %s AND kd_cabang = %s",
                    ["DOKTER", dokter_id, visibility_branch],
                )
                if not saved_visibility or int(saved_visibility[0]["is_hidden"]) != hidden:
                    raise RuntimeError("Status tampil Pembelian Dokter gagal disimpan.")
            if result:
                result[0]["IS_HIDDEN"] = hidden
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print("coba")


def open_dokter(request):
    cabang_id = request.session["kdCabang"]
    q = "SELECT dokter.FMDDOKTER_ID,dokter.FMDDOKTERN,dokter.FMDJABATAN,dokter.FMDDOKTER_ID_BPJS,dokter.FMDNIP,dokter.KODEDOKTER,dokter.KODEDPJP,dokter.FMDNOTELP,dokter.SIP,dokter.FMDSTATUS,dokter.KD_CABANG,dokter.USERRS,dokter.UPDATERS,dokter.SSFHIR_KD_DOKTER,ISNULL(visibility.is_hidden, 0) AS IS_HIDDEN FROM DOKTER AS dokter LEFT JOIN NAKES_PEMBELIAN_VISIBILITY AS visibility ON visibility.nakes_type = 'DOKTER' AND visibility.nakes_id = dokter.FMDDOKTER_ID AND visibility.kd_cabang = dokter.KD_CABANG WHERE dokter.KD_CABANG = %s ORDER BY dokter.FMDDOKTERN"
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
