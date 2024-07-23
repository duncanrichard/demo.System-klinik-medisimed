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
import requests
import os
import datetime
from datetime import *


def exit(request):
    return redirect("/")


def satu_sehat_bridge(request):
    if Globals().isLogin(request):
        user_priv = request.session["user_id"]
        user_privelege = request.session["user_priv"]
        user_name = request.session["user_name"]
        navbars = Globals().getNavbars(user_priv, "IMMODERMA", "satu_sehat_bridge")
        menubars = Globals().getMenubars(
            user_priv, "IMMODERMA", "satu_sehat_bridge", "0"
        )
        menubarsChild = Globals().getMenubars(
            user_priv, "IMMODERMA", "satu_sehat_bridge", "1"
        )
        menubarCount = len(menubars)
        response = render(
            request,
            "emr_new/satu_sehat_bridge/base.html",
            {
                "navbars": navbars,
                "menubars": menubars,
                "menubarsChild": menubarsChild,
                "menubarsType": 1,
                "count_": menubarCount,
                "list_": Globals().getSeparator(menubarCount),
                "user_id": user_priv,
                "user_privelege": user_privelege,
                "user_name": user_name,
                "cabangid": request.session["kdCabang"],
                "SERVER_INDO": getattr(env, "SERVER_INDO", ""),
            },
        )
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def getToken(request):
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    q = "SELECT * FROM SATUSEHAT_TOKEN WHERE expired_token>GETDATE() and CABANG_ID= %s "
    result = Globals().getDataQuery(q, [kdCabang])
    if len(result) > 0:
        # return HttpResponse(result[0]["access_token"], content_type="application/json")
        # print(result[0]["access_token"])
        return result[0]["access_token"]
    else:
        q = "select a.CABANG_ID,a.PERUSAHAAN,a.ALAMAT1,KOTA_ID,KOTA,KODE_POS,TELEPON,no_whatsapp,email,KONTAK,JABATAN,NPWP,TGLPENGUKUHAN,USING,a.ppkpelayanan,consid,secret,bpjs_userkey,userncc,passwordncc,ijinSIP,user_icare,password_icare,statusmjkn,client_id,organization_id,Secret_key,SS_FHIR_KD_CABANG,   "
        q += "b.KD_KELURAHAN,b.KELURAHAN,c.KD_KECAMATAN,c.KECAMATAN,isnull(d.KD_KABUPATEN,a.KOTA_ID) as KD_KABUPATEN,isnull(d.KABUPATEN,KOTA) as KABUPATEN,e.KD_PROPINSI,e.PROPINSIN from CABANG a "
        q += "left join KELURAHAN b on a.KOTA_ID=b.KD_KELURAHAN  "
        q += "left join KECAMATAN c on b.KD_KECAMATAN=c.KD_KECAMATAN "
        q += "left join KABUPATEN d on c.KD_KABUPATEN=d.KD_KABUPATEN "
        q += "left join PROPINSI e on d.KD_PROPINSI=e.KD_PROPINSI "
        q += "WHERE CABANG_ID= %s "
        resultCabang = Globals().getDataQuery(q, [kdCabang])
        url = (
            getattr(
                env,
                "SATU_SEHAT_URL",
                "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
            )
            + "/accesstoken?grant_type=client_credentials"
        )
        payload = {
            "client_id": resultCabang[0]["client_id"],
            "client_secret": resultCabang[0]["Secret_key"],
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        }
        # print(url)
        # print(payload)
        # print(headers)
        # print("headers")
        json_data = requests.post(url, data=payload, headers=headers)
        # print(json_data.text)
        # print(json.loads(json_data.text)["access_token"])
        # print(json.loads(json_data.text))
        # print(json.loads(json_data.text)["access_token"])
        q = "SELECT * FROM SATUSEHAT_TOKEN WHERE CABANG_ID= %s "
        result = Globals().getDataQuery(q, [kdCabang])

        if len(result) > 0:
            q = "UPDATE SATUSEHAT_TOKEN SET access_token='{}',JSON_DATA='{}',expired_token=DATEADD(SECOND,(3599*7.5),DATEADD(S, CONVERT(int,LEFT('{}', 10)), '1970-01-01')) where CABANG_ID= %s ".format(
                json.loads(json_data.text)["access_token"],
                json_data.text,
                json.loads(json_data.text)["issued_at"],
            )
            Globals().executeQuery(q, [kdCabang])
        else:
            q = "INSERT INTO  SATUSEHAT_TOKEN(access_token,JSON_DATA,expired_token,cabang_id) VALUES "
            q += "('{}','{}',DATEADD(SECOND,(3599*7.5),DATEADD(S, CONVERT(int,LEFT('{}', 10)), '1970-01-01')),%s )".format(
                json.loads(json_data.text)["access_token"],
                json_data.text,
                json.loads(json_data.text)["issued_at"],
            )

            Globals().executeQuery(q, [kdCabang])

        # return HttpResponse(json_data, content_type="application/json")
        # print(json.loads(json_data.text)["access_token"])
        return json.loads(json_data.text)["access_token"]


def proses_satu_sehat(request):
    # proses pasien
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]

    if "tglAwal" in request.GET:
        tglAwal = request.GET["tglAwal"]
        tglAkhir = request.GET["tglAkhir"]
        query = "SELECT A.KD_PASIEN,A.NO_PENGENAL "
        query += " FROM PASIEN A "
        query += " INNER JOIN KUNJUNGANPASIEN B ON A.KD_PASIEN=B.KPKD_PASIEN "
        query += " WHERE  B.KPTGL_PERIKSA>= %s AND B.KPTGL_PERIKSA<= %s  "
        query += " AND ISNULL(PKD_PASIEN_FHIR,'')='' AND LEN(ISNULL(NO_PENGENAL,''))=16 AND A.KD_ASAL_CABANG= %s "
        query += " ORDER BY KD_PASIEN ASC"
        result = Globals().getDataQuery(query, [tglAwal, tglAkhir, kdCabang])
    else:
        query = "SELECT A.KD_PASIEN,A.NO_PENGENAL "
        query += " FROM PASIEN A "
        query += " INNER JOIN KUNJUNGANPASIEN B ON A.KD_PASIEN=B.KPKD_PASIEN "
        query += " WHERE  B.KPTGL_PERIKSA>= CONVERT(varchar,DATEADD(day, -1, GETDATE()),23) AND B.KPTGL_PERIKSA<= CONVERT(varchar,GETDATE(),23)  "
        query += " AND ISNULL(PKD_PASIEN_FHIR,'')='' AND LEN(ISNULL(NO_PENGENAL,''))=16 AND A.KD_ASAL_CABANG= %s "
        query += " ORDER BY KD_PASIEN ASC"
        result = Globals().getDataQuery(query, [kdCabang])

    for isianPasien in result:
        kdPasien = isianPasien["KD_PASIEN"]
        NO_PENGENAL = isianPasien["NO_PENGENAL"]
        url = getattr(
            env,
            "SATU_SEHAT_URL_DATA",
            "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
        ) + "/Patient?identifier=https://fhir.kemkes.go.id/id/nik|{}".format(
            NO_PENGENAL
        )
        payload = {}
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(getToken(request)),
            "User-Agent": "SIMKLINIK MEDISIMED",
        }
        # print(headers)
        # print(url)
        json_data = requests.get(url, data=payload, headers=headers)
        dataBridging = json.loads(json_data.text)
        # print("===response")
        # print(dataBridging)
        # print("===response")

        try:
            PKD_PASIEN_FHIR = dataBridging["entry"][0]["resource"]["id"]
            qupdatepasien = "UPDATE PASIEN SET PKD_PASIEN_FHIR='{}' WHERE KD_PASIEN='{}' and KD_ASAL_CABANG='{}' ".format(
                PKD_PASIEN_FHIR, kdPasien, kdCabang
            )
            Globals().executeQuery(qupdatepasien)
        except:
            print("===response Pasien eror")
            print(dataBridging)
            print(kdPasien)
            print("===response pasien eror")

    # proses kunjungan
    # kdCabang = request.session["kdCabang"]
    q = "select a.CABANG_ID,a.PERUSAHAAN,a.ALAMAT1,KOTA_ID,KOTA,KODE_POS,TELEPON,no_whatsapp,email,website,KONTAK,JABATAN,NPWP,TGLPENGUKUHAN,USING,a.ppkpelayanan,consid,secret,bpjs_userkey,userncc,passwordncc,ijinSIP,user_icare,password_icare,statusmjkn,client_id,organization_id,Secret_key,SS_FHIR_KD_CABANG,   "
    q += "b.KD_KELURAHAN,b.KELURAHAN,c.KD_KECAMATAN,c.KECAMATAN,isnull(d.KD_KABUPATEN,a.KOTA_ID) as KD_KABUPATEN,isnull(d.KABUPATEN,KOTA) as KABUPATEN,e.KD_PROPINSI,e.PROPINSIN from CABANG a "
    q += "left join KELURAHAN b on a.KOTA_ID=b.KD_KELURAHAN  "
    q += "left join KECAMATAN c on b.KD_KECAMATAN=c.KD_KECAMATAN "
    q += "left join KABUPATEN d on c.KD_KABUPATEN=d.KD_KABUPATEN "
    q += "left join PROPINSI e on d.KD_PROPINSI=e.KD_PROPINSI "
    q += "WHERE CABANG_ID= %s "
    resultCabang = Globals().getDataQuery(q, [kdCabang])
    if "tglAwal" in request.GET:
        tglAwal = request.GET["tglAwal"]
        tglAkhir = request.GET["tglAkhir"]
        query = "SELECT  dbo.EMR_GET_USER(KUNJ.KPKD_DOKTER) as NAMADOKTER,PL.FMPKLINIKN as POLIN,KUNJ.KPNO_TRANSAKSI as NOTRANS  "
        query += " ,ISNULL(PLSS.SSFHIR_KD_POLI,'-')  as KDPOLI_FHIR "
        query += " ,ISNULL(DOK.SSFHIR_KD_DOKTER,'-') as KD_KDDOKTER_FHIR "
        query += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,KUNJ.UPDATERS))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(KUNJ.UPDATERS,KUNJ.UPDATERS))) AS datetime)),126)+'+07:00' as TGLJAM_START"
        query += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,KUNJ.UPDATERS))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(KUNJ.UPDATERS,KUNJ.UPDATERS))) AS datetime)),126)+'+07:00' as TGLJAM_PROGRESS"
        query += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,KUNJ.UPDATERS))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(KUNJ.UPDATERS,KUNJ.UPDATERS))) AS datetime)),126)+'+07:00' as TGLJAM_END"
        query += " ,PS.NAMAPASIEN,ISNULL(PS.PKD_PASIEN_FHIR,'-') as KD_PASIEN_FHIR "
        query += " ,KUNJ.KPTGL_PERIKSA as TGLRS,KUNJ.KPKD_DOKTER as KDDOKTERRS,KUNJ.KPKD_POLY as POLIRS,KUNJ.KPKD_PASIEN as KDASIENRS "
        query += " FROM KUNJUNGANPASIEN KUNJ "
        query += " INNER JOIN POLIKLINIK PL ON KUNJ.KPKD_POLY=PL.FMPKLINIK_ID "
        query += " INNER JOIN POLIKLINIK_SATU_SEHAT PLSS ON PL.FMPKLINIK_ID=PLSS.SSFHIR_KLINIK_ID AND PLSS.SSFHIR_CABANG_ID=%s "
        query += " LEFT JOIN PASIEN PS ON KUNJ.KPKD_PASIEN=PS.KD_PASIEN AND PS.KD_ASAL_CABANG=%s "
        query += " LEFT JOIN DOKTER DOK ON KUNJ.KPKD_DOKTER=DOK.FMDDOKTER_ID AND DOK.KD_CABANG=%s "
        query += " WHERE "
        query += " CONVERT(date,KUNJ.KPTGL_PERIKSA)>=%s "
        query += " AND CONVERT(date,KUNJ.KPTGL_PERIKSA)<=%s "
        query += " AND ISNULL(DOK.SSFHIR_KD_DOKTER,'-')<>'-' "
        query += " AND ISNULL(PKD_PASIEN_FHIR,'')<>'' "
        query += " AND ISNULL(KUNJ.PSD_NO_TRANSAKSI_FHIR,'')='' "
        query += " AND KUNJ.KD_CABANG=%s "
        result = Globals().getDataQuery(
            query, [kdCabang, kdCabang, kdCabang, tglAwal, tglAkhir, kdCabang]
        )
    else:
        query = "SELECT  dbo.EMR_GET_USER(KUNJ.KPKD_DOKTER) as NAMADOKTER,PL.FMPKLINIKN as POLIN,KUNJ.KPNO_TRANSAKSI as NOTRANS  "
        query += " ,ISNULL(PLSS.SSFHIR_KD_POLI,'-')  as KDPOLI_FHIR "
        query += " ,ISNULL(DOK.SSFHIR_KD_DOKTER,'-') as KD_KDDOKTER_FHIR "
        query += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,KUNJ.UPDATERS))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(KUNJ.UPDATERS,KUNJ.UPDATERS))) AS datetime)),126)+'+07:00' as TGLJAM_START"
        query += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,KUNJ.UPDATERS))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(KUNJ.UPDATERS,KUNJ.UPDATERS))) AS datetime)),126)+'+07:00' as TGLJAM_PROGRESS"
        query += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,KUNJ.UPDATERS))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(KUNJ.UPDATERS,KUNJ.UPDATERS))) AS datetime)),126)+'+07:00' as TGLJAM_END"
        query += " ,PS.NAMAPASIEN,ISNULL(PS.PKD_PASIEN_FHIR,'-') as KD_PASIEN_FHIR "
        query += " ,KUNJ.KPTGL_PERIKSA as TGLRS,KUNJ.KPKD_DOKTER as KDDOKTERRS,KUNJ.KPKD_POLY as POLIRS,KUNJ.KPKD_PASIEN as KDASIENRS "
        query += " FROM KUNJUNGANPASIEN KUNJ "
        query += " INNER JOIN POLIKLINIK PL ON KUNJ.KPKD_POLY=PL.FMPKLINIK_ID "
        query += " INNER JOIN POLIKLINIK_SATU_SEHAT PLSS ON PL.FMPKLINIK_ID=PLSS.SSFHIR_KLINIK_ID AND PLSS.SSFHIR_CABANG_ID=%s "
        query += " LEFT JOIN PASIEN PS ON KUNJ.KPKD_PASIEN=PS.KD_PASIEN AND PS.KD_ASAL_CABANG=%s "
        query += " LEFT JOIN DOKTER DOK ON KUNJ.KPKD_DOKTER=DOK.FMDDOKTER_ID AND DOK.KD_CABANG=%s "
        query += " WHERE "
        query += " CONVERT(date,KUNJ.KPTGL_PERIKSA)>=CONVERT(varchar,DATEADD(day, -1, GETDATE()),23) "
        query += " AND CONVERT(date,KUNJ.KPTGL_PERIKSA)<=CONVERT(varchar,GETDATE(),23)  "
        query += " AND ISNULL(DOK.SSFHIR_KD_DOKTER,'-')<>'-' "
        query += " AND ISNULL(PKD_PASIEN_FHIR,'')<>'' "
        query += " AND ISNULL(KUNJ.PSD_NO_TRANSAKSI_FHIR,'')='' "
        query += " AND KUNJ.KD_CABANG=%s "
        result = Globals().getDataQuery(
            query, [kdCabang, kdCabang, kdCabang, kdCabang]
        )

    for isiankunjuanPasien in result:
        url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_ADA_LINK") + "/Encounter"

        payload = {
            "resourceType": "Encounter",
            "status": "arrived",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {
                "reference": "Patient/{}".format(isiankunjuanPasien["KD_PASIEN_FHIR"]),
                "display": "{}".format(isiankunjuanPasien["NAMAPASIEN"]),
            },
            "participant": [
                {
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                    "code": "ATND",
                                    "display": "attender",
                                }
                            ]
                        }
                    ],
                    "individual": {
                        "reference": "Practitioner/{}".format(
                            isiankunjuanPasien["KD_KDDOKTER_FHIR"]
                        ),
                        "display": "{}".format(isiankunjuanPasien["NAMADOKTER"]),
                    },
                }
            ],
            "period": {
                "start": "{}".format(isiankunjuanPasien["TGLJAM_START"]),
                "end": "{}".format(isiankunjuanPasien["TGLJAM_END"]),
            },
            "location": [
                {
                    "location": {
                        "display": "{}".format(isiankunjuanPasien["POLIN"]),
                        "reference": "Location/{}".format(
                            isiankunjuanPasien["KDPOLI_FHIR"]
                        ),
                    }
                }
            ],
            "statusHistory": [
                {
                    "period": {
                        "start": "{}".format(isiankunjuanPasien["TGLJAM_START"]),
                        "end": "{}".format(isiankunjuanPasien["TGLJAM_START"]),
                    },
                    "status": "arrived",
                },
                {
                    "period": {
                        "start": "{}".format(isiankunjuanPasien["TGLJAM_START"]),
                        "end": "{}".format(isiankunjuanPasien["TGLJAM_PROGRESS"]),
                    },
                    "status": "in-progress",
                },
                {
                    "period": {
                        "start": "{}".format(isiankunjuanPasien["TGLJAM_PROGRESS"]),
                        "end": "{}".format(isiankunjuanPasien["TGLJAM_END"]),
                    },
                    "status": "finished",
                },
            ],
            "serviceProvider": {
                "reference": "Organization/{}".format(
                    resultCabang[0]["organization_id"]
                )
            },
            "identifier": [
                {
                    "system": "http://sys-ids.kemkes.go.id/encounter/{}".format(
                        resultCabang[0]["organization_id"]
                    ),
                    "value": "{}".format(isiankunjuanPasien["NOTRANS"]),
                }
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE ENCOUNTER",
            "Authorization": "Bearer " + getToken(request),
        }
        # print(getToken(request))
        # print(headers)
        # print(payload)
        # exit()
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(payload))
            dataBridging = json.loads(json_data.text)
            # print("===response saveencounter")
            # print(dataBridging)
            # print("===response saveencounter")

        except:
            print("===response error")
            print("===response saveencounter")
            print(dataBridging)
            print(isiankunjuanPasien["NOTRANS"])
            print("===response saveencounter")

        # print("===response saveencounter")
        # print(dataBridging)
        # print("===response saveencounter")
        try:
            qupdatepasien = "UPDATE KUNJUNGANPASIEN SET PSD_NO_TRANSAKSI_FHIR='{}' WHERE KPNO_TRANSAKSI='{}' and KD_CABANG='{}' ".format(
                dataBridging["id"], isiankunjuanPasien["NOTRANS"], kdCabang
            )
            Globals().executeQuery(qupdatepasien)
        except:
            print("===response saveencounter update kunjungan")
            print(dataBridging)
            print("===response saveencounter  update kunjungan")
    # proses ICD 10
    query = "SELECT  MPNY.MRPKD_PENYAKIT,PLSS.PENYAKIT, PSD_NO_TRANSAKSI_FHIR,KUNJ.KPNO_TRANSAKSI as NOTRANS  ,PS.PKD_PASIEN_FHIR,PS.NAMAPASIEN "
    query += " ,KUNJ.KPTGL_PERIKSA as TGLINDO  "
    query += " FROM KUNJUNGANPASIEN KUNJ  "
    query += (
        " INNER JOIN MR_PENYAKIT MPNY ON MPNY.MRPNO_TRANSAKSI=KUNJ.KPNO_TRANSAKSI  "
    )
    query += " INNER JOIN PENYAKIT PLSS ON PLSS.KD_PENYAKIT=MPNY.MRPKD_PENYAKIT "
    query += " INNER JOIN PASIEN PS ON PS.KD_PASIEN=KUNJ.KPKD_PASIEN "
    query += " WHERE  "
    if "tglAwal" in request.GET:
        query += " CONVERT(date,KUNJ.KPTGL_PERIKSA)>=%s  "
        query += " AND CONVERT(date,KUNJ.KPTGL_PERIKSA)<=%s  "
        query += " AND ISNULL(KUNJ.PSD_NO_TRANSAKSI_FHIR,'')<>''  "
        query += " AND ISNULL(SS_FHIR_ID,'')='' AND KUNJ.KD_CABANG=%s "
        result = Globals().getDataQuery(query, [tglAwal, tglAkhir, kdCabang])
    else:
        query += " CONVERT(date,KUNJ.KPTGL_PERIKSA)>=CONVERT(varchar,DATEADD(day, -1, GETDATE()),23)  "
        query += " AND CONVERT(date,KUNJ.KPTGL_PERIKSA)<=CONVERT(varchar,GETDATE(),23)  "
        query += " AND ISNULL(KUNJ.PSD_NO_TRANSAKSI_FHIR,'')<>''  "
        query += " AND ISNULL(SS_FHIR_ID,'')='' AND KUNJ.KD_CABANG=%s "
        result = Globals().getDataQuery(query, [ kdCabang])
    for isianPoli in result:
        KD_PASIEN_FHIR = isianPoli["PKD_PASIEN_FHIR"]
        url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_INPUT") + "/Condition"
        payload = {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active",
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "encounter-diagnosis",
                            "display": "Encounter Diagnosis",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-10",
                        "code": "{}".format(isianPoli["MRPKD_PENYAKIT"]),
                        "display": "{}".format(isianPoli["PENYAKIT"]),
                    }
                ]
            },
            "subject": {
                "reference": "Patient/{}".format(KD_PASIEN_FHIR),
                "display": "{}".format(isianPoli["NAMAPASIEN"]),
            },
            "encounter": {
                "reference": "Encounter/{}".format(isianPoli["PSD_NO_TRANSAKSI_FHIR"]),
                "display": "Kunjungan {} di {}".format(
                    isianPoli["NAMAPASIEN"], isianPoli["TGLINDO"]
                ),
            },
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE CONDITION",
            "Authorization": "Bearer " + getToken(request),
        }
        json_data = requests.post(url, headers=headers, data=json.dumps(payload))
        dataBridging = json.loads(json_data.text)
        try:
            # print("===berhasil response condition")
            # print(dataBridging)
            # print("===response condition")
            qupdateICD10 = "UPDATE MR_PENYAKIT SET SS_FHIR_ID='{}' WHERE MRPNO_TRANSAKSI='{}' and KD_CABANG='{}' ".format(
                dataBridging["id"], isianPoli["NOTRANS"], kdCabang
            )
            Globals().executeQuery(qupdateICD10)
        except:
            print("===gagal Save response ICD 10 condition")
            print(dataBridging)
            print("===response ICD 10 condition")

    # proses ICD 9
    query = "SELECT MPNY.MRTKD_TINDAKAN,PLSS.FMI9KETERANGAN  "
    query += (
        " ,PSD_NO_TRANSAKSI_FHIR,KUNJ.KPNO_TRANSAKSI as NOTRANS , KUNJ.KPKD_PASIEN  "
    )
    query += " ,PS.PKD_PASIEN_FHIR,PS.NAMAPASIEN,ps.KD_PASIEN  "
    query += " ,KUNJ.KPTGL_PERIKSA as TGLINDO ,kunj.KD_CABANG "
    query += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,KUNJ.UPDATERS))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(KUNJ.UPDATERS,KUNJ.UPDATERS))) AS datetime)),126)+'+07:00' as JAMRS  "
    query += "  FROM KUNJUNGANPASIEN KUNJ   "
    query += (
        " INNER JOIN MR_TINDAKAN MPNY ON MPNY.MRTNOTRANSAKSI=KUNJ.KPNO_TRANSAKSI   "
    )
    query += " INNER JOIN MR_ICD9 PLSS ON PLSS.FMI9KODE=MPNY.MRTKD_TINDAKAN  "
    query += " INNER JOIN PASIEN PS ON PS.KD_PASIEN=MPNY.MRTKD_PASIEN  "
    if "tglAwal" in request.GET:
        query += " WHERE CONVERT(date,KUNJ.KPTGL_PERIKSA)>=%s   "
        query += " AND CONVERT(date,KUNJ.KPTGL_PERIKSA)<=%s   "
        query += " AND ISNULL(KUNJ.PSD_NO_TRANSAKSI_FHIR,'')<>''   "
        query += " AND ISNULL(MPNY.SS_FHIR_ID,'')=''  AND KUNJ.KD_CABANG=%s   "

        result = Globals().getDataQuery(query, [tglAwal, tglAkhir, kdCabang])
    else:
        query += " WHERE CONVERT(date,KUNJ.KPTGL_PERIKSA)>=CONVERT(varchar,DATEADD(day, -1, GETDATE()),23)  "
        query += " AND CONVERT(date,KUNJ.KPTGL_PERIKSA)<=CONVERT(varchar,GETDATE(),23)  "
        query += " AND ISNULL(KUNJ.PSD_NO_TRANSAKSI_FHIR,'')<>''   "
        query += " AND ISNULL(MPNY.SS_FHIR_ID,'')=''  AND KUNJ.KD_CABANG=%s   "

        result = Globals().getDataQuery(query, [kdCabang])
    
    for isianPoli in result:
        KD_PASIEN_FHIR = isianPoli["PKD_PASIEN_FHIR"]

        url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_INPUT") + "/Procedure"
        payload = {
            "resourceType": "Procedure",
            "status": "completed",
            "category": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "103693007",
                        "display": "Diagnostic procedure",
                    }
                ],
                "text": "Diagnostic procedure",
            },
            "code": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-9-cm",
                        "code": "{}".format(isianPoli["MRTKD_TINDAKAN"]),
                        "display": "{}".format(isianPoli["FMI9KETERANGAN"]),
                    }
                ]
            },
            "subject": {
                "reference": "Patient/{}".format(KD_PASIEN_FHIR),
                "display": "{}".format(isianPoli["NAMAPASIEN"]),
            },
            "encounter": {
                "reference": "Encounter/{}".format(isianPoli["PSD_NO_TRANSAKSI_FHIR"]),
                "display": "Kunjungan {} tgl {}".format(
                    isianPoli["NAMAPASIEN"], isianPoli["TGLINDO"]
                ),
            },
            "performedPeriod": {
                "start": "{}".format(isianPoli["JAMRS"]),
                "end": "{}".format(isianPoli["JAMRS"]),
                # "start": "{}T{}+07:00".format(isianPoli["TGLINDO"], isianPoli["JAMRS"]),
                # "end": "{}T{}+07:00".format(isianPoli["TGLINDO"], isianPoli["JAMRS"]),
            },
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE PROCEDURE",
            "Authorization": "Bearer " + getToken(request),
        }
        # print(headers)
        # print(payload)
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(payload))
            dataBridging = json.loads(json_data.text)
            # print("===Sukses Bridgging response ICD 9 condition")
            # print(dataBridging)
            # print("===Sukses Bridgging response condition ICD 9")

        except:
            print("===gagal  response ICD 9 condition")
            print(dataBridging)
            print("===response condition ICD 9")

        # print(kdPoli)
        try:
            qupdateICD9 = "UPDATE MR_TINDAKAN SET SS_FHIR_ID='{}' WHERE MRTNOTRANSAKSI='{}' and KD_CABANG='{}' ".format(
                dataBridging["id"], isianPoli["NOTRANS"], kdCabang
            )
            Globals().executeQuery(qupdateICD9)

        except:
            print("===gagal Save response ICD 9 condition")
            print(dataBridging)
            print("===response condition ICD 9")

    # TTV
    query = "SELECT KP.KPNO_TRANSAKSI,KP.PSD_NO_TRANSAKSI_FHIR  "
    query += " ,PP.KD_PASIEN,PP.NAMAPASIEN,PP.PKD_PASIEN_FHIR,DR.SSFHIR_KD_DOKTER "
    query += " ,DR.FMDDOKTERN "
    query += " ,CONVERT(varchar,KP.UPDATERS,8) as JAMRS_ASLI "
    query += " ,CONVERT(varchar,KP.KPTGL_PERIKSA,23) as TGLRS "
    query += " ,CONVERT(varchar,DATEADD(hour, -7, KP.UPDATERS),8) as JAMRS,(KP.KPTGL_PERIKSA) as TGLINDO "
    query += " ,CAST(ISNULL(CAST(SR.TTVSUHU AS int),'')AS varchar) as SUHU,IIF(SR.STATUS_TTV_SUHU IS NULL,'0','1')  as STATUS_SUHU "
    query += " ,ISNULL(SR.TTVNAFAS,'') as RR,IIF(SR.STATUS_TTV_RESPIRASI IS NULL,'0','1') as STATUS_RR "
    query += " ,ISNULL(SR.TTVNADI,'') as NADI,IIF(SR.STATUS_TTV_NADI IS NULL,'0','1') as STATUS_NADI "
    query += " ,ISNULL(SR.TTVO2,'') as SPO2,IIF(SR.STATUS_TTV_O2 IS NULL,'0','1') as STATUS_SPO2 "
    query += " ,ISNULL(SR.TTVTSISTOL,'') as SISTOL,ISNULL(SR.TTVDIASTOL,'') as DIASTOL,IIF(SR.STATUS_TTV_TENSI_SISTOLE IS NULL,'0','1')  as STATUS_SISTOLE "
    query += " ,ISNULL(SR.TTVTINGGI_BADAN,'') as TB,IIF(SR.STATUS_TTV_TB IS NULL,'0','1')  as STATUS_TB "
    query += " ,ISNULL(SR.TTVBERAT_BADAN,'') as BB,IIF(SR.STATUS_TTV_BB IS NULL,'0','1')  as STATUS_BB "
    query += " FROM KUNJUNGANPASIEN KP  "
    query += " LEFT JOIN PASIEN PP ON KP.KPKD_PASIEN=PP.KD_PASIEN "
    query += " LEFT JOIN DOKTER DR ON KP.KPKD_DOKTER=DR.FMDDOKTER_ID "
    query += " LEFT JOIN EMRRJ_TTV SR ON KP.KPNO_TRANSAKSI=SR.TTVNO_TRANSAKSI_RJ "
    query += " WHERE  "
    if "tglAwal" in request.GET:
        query += " CONVERT(date,kp.KPTGL_PERIKSA)>=%s  "
        query += " AND CONVERT(date,kp.KPTGL_PERIKSA)<=%s  "
        query += " AND ISNULL(KP.PSD_NO_TRANSAKSI_FHIR,'')<>''  "
        query += " AND DR.SSFHIR_KD_DOKTER IS NOT NULL "
        query += " AND KP.KD_CABANG=%s "
        query += " ORDER BY 1 DESC "
        result = Globals().getDataQuery(query, [tglAwal, tglAkhir, kdCabang])
    else:
        query += " CONVERT(date,kp.KPTGL_PERIKSA)>=CONVERT(varchar,DATEADD(day, -1, GETDATE()),23)   "
        query += " AND CONVERT(date,kp.KPTGL_PERIKSA)<=CONVERT(varchar,GETDATE(),23)  "
        query += " AND ISNULL(KP.PSD_NO_TRANSAKSI_FHIR,'')<>''  "
        query += " AND DR.SSFHIR_KD_DOKTER IS NOT NULL "
        query += " AND KP.KD_CABANG=%s "
        query += " ORDER BY 1 DESC "
        result = Globals().getDataQuery(query, [kdCabang])

    for isianPoli in result:
        # print(isianPoli["KD_PASIEN_FHIR"])
        KD_PASIEN_FHIR = isianPoli["PKD_PASIEN_FHIR"]
        STATUS_SUHU = isianPoli["STATUS_SUHU"]
        SUHUS = int(isianPoli["SUHU"])
        STATUS_RR = isianPoli["STATUS_RR"]
        RRS = int(isianPoli["RR"])
        STATUS_NADI = isianPoli["STATUS_NADI"]
        NADIS = int(isianPoli["NADI"])
        STATUS_SPO2 = isianPoli["STATUS_SPO2"]
        SPO2S = int(isianPoli["SPO2"])
        STATUS_SISTOLE = isianPoli["STATUS_SISTOLE"]
        SISTOLS = int(isianPoli["SISTOL"])
        DIASTOLS = int(isianPoli["DIASTOL"])
        STATUS_TB = isianPoli["STATUS_TB"]
        TBS = int(isianPoli["TB"])
        STATUS_BB = isianPoli["STATUS_BB"]
        BBS = int(isianPoli["BB"])
        url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_INPUT") + "/Observation"

        ################### SUHU
        if STATUS_SUHU == "0":
            try:
                payload = {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                    "display": "Vital Signs",
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8310-5",
                                "display": "Body temperature",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/{}".format(isianPoli["PKD_PASIEN_FHIR"])
                    },
                    "performer": [
                        {
                            "reference": "Practitioner/{}".format(
                                isianPoli["SSFHIR_KD_DOKTER"]
                            )
                        }
                    ],
                    "encounter": {
                        "reference": "Encounter/{}".format(
                            isianPoli["PSD_NO_TRANSAKSI_FHIR"]
                        ),
                        "display": "Pemeriksaan Fisik Suhu RJ atas Nama {} di tanggal {} {}".format(
                            isianPoli["NAMAPASIEN"],
                            isianPoli["TGLINDO"],
                            isianPoli["JAMRS_ASLI"],
                        ),
                    },
                    "effectiveDateTime": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "issued": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "valueQuantity": {
                        "value": SUHUS,
                        "unit": "degree Celsius",
                        "system": "http://unitsofmeasure.org",
                        "code": "Cel",
                    },
                }

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "SIMKLINIK MEDISIMED SAVE CONDITION",
                    "Authorization": "Bearer " + getToken(request),
                }
                # BRIDGING
                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                # BRIDGING
                qUpdateStatus = " UPDATE EMRRJ_TTV SET STATUS_TTV_SUHU=GETDATE() WHERE TTVNO_TRANSAKSI_RJ='{}' ".format(
                    isianPoli["KPNO_TRANSAKSI"]
                )
                Globals().executeQuery(qUpdateStatus)
            except:
                print("===gagal  response TTV SUHU condition")
                print(dataBridging)
                print("===response condition response TTV SUHU")

        ################### SUHU

        ################### RR
        if STATUS_RR == "0":
            try:
                payload = {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                    "display": "Vital Signs",
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "9279-1",
                                "display": "Respiratory rate",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/{}".format(isianPoli["PKD_PASIEN_FHIR"])
                    },
                    "performer": [
                        {
                            "reference": "Practitioner/{}".format(
                                isianPoli["SSFHIR_KD_DOKTER"]
                            )
                        }
                    ],
                    "encounter": {
                        "reference": "Encounter/{}".format(
                            isianPoli["PSD_NO_TRANSAKSI_FHIR"]
                        ),
                        "display": "Pemeriksaan Fisik RR RJ atas Nama {} di tanggal {} {}".format(
                            isianPoli["NAMAPASIEN"],
                            isianPoli["TGLINDO"],
                            isianPoli["JAMRS_ASLI"],
                        ),
                    },
                    "effectiveDateTime": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "issued": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "valueQuantity": {
                        "value": RRS,
                        "unit": "Breaths / minute",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min",
                    },
                }

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "SIMKLINIK MEDISIMED SAVE CONDITION",
                    "Authorization": "Bearer " + getToken(request),
                }
                # BRIDGING
                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                # BRIDGING
                qUpdateStatus = " UPDATE EMRRJ_TTV SET STATUS_TTV_RESPIRASI=GETDATE() WHERE TTVNO_TRANSAKSI_RJ='{}' ".format(
                    isianPoli["KPNO_TRANSAKSI"]
                )
                Globals().executeQuery(qUpdateStatus)
            except:
                print("===gagal  response TTV RESPIRASI condition")
                print(dataBridging)
                print("===response condition response TTV RESPIRASI")

            # RECORD SUDAH BRIDING
        ################### RR

        # ################### NADI
        if STATUS_NADI == "0":
            try:
                payload = {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                    "display": "Vital Signs",
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8867-4",
                                "display": "Heart rate",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/{}".format(isianPoli["PKD_PASIEN_FHIR"])
                    },
                    "performer": [
                        {
                            "reference": "Practitioner/{}".format(
                                isianPoli["SSFHIR_KD_DOKTER"]
                            )
                        }
                    ],
                    "encounter": {
                        "reference": "Encounter/{}".format(
                            isianPoli["PSD_NO_TRANSAKSI_FHIR"]
                        ),
                        "display": "Pemeriksaan Fisik NADI RJ atas Nama {} di tanggal {} {}".format(
                            isianPoli["NAMAPASIEN"],
                            isianPoli["TGLINDO"],
                            isianPoli["JAMRS_ASLI"],
                        ),
                    },
                    "effectiveDateTime": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "issued": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "valueQuantity": {
                        "value": NADIS,
                        "unit": "Breaths / minute",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min",
                    },
                }

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "SIMKLINIK MEDISIMED SAVE CONDITION",
                    "Authorization": "Bearer " + getToken(request),
                }
                # BRIDGING
                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                # BRIDGING
                qUpdateStatus = " UPDATE EMRRJ_TTV SET STATUS_TTV_NADI=GETDATE() WHERE TTVNO_TRANSAKSI_RJ='{}' ".format(
                    isianPoli["KPNO_TRANSAKSI"]
                )
                Globals().executeQuery(qUpdateStatus)
            except:
                print("===gagal  response TTV NADI condition")
                print(dataBridging)
                print("===response condition response TTV NADI")

        ################### NADI

        # ################### SPO2
        if STATUS_SPO2 == "0":
            try:
                payload = {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                    "display": "Vital Signs",
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "59408-5",
                                "display": "Oxygen saturation",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/{}".format(isianPoli["PKD_PASIEN_FHIR"])
                    },
                    "performer": [
                        {
                            "reference": "Practitioner/{}".format(
                                isianPoli["SSFHIR_KD_DOKTER"]
                            )
                        }
                    ],
                    "encounter": {
                        "reference": "Encounter/{}".format(
                            isianPoli["PSD_NO_TRANSAKSI_FHIR"]
                        ),
                        "display": "Pemeriksaan Fisik SPO2 RJ atas Nama {} di tanggal {} {}".format(
                            isianPoli["NAMAPASIEN"],
                            isianPoli["TGLINDO"],
                            isianPoli["JAMRS_ASLI"],
                        ),
                    },
                    "effectiveDateTime": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "issued": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "valueQuantity": {
                        "value": SPO2S,
                        "unit": "percent saturation",
                        "system": "http://unitsofmeasure.org",
                        "code": "%",
                    },
                }

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "SIMKLINIK MEDISIMED SAVE CONDITION",
                    "Authorization": "Bearer " + getToken(request),
                }
                # BRIDGING
                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                # BRIDGING
                qUpdateStatus = " UPDATE EMRRJ_TTV SET STATUS_TTV_O2=GETDATE() WHERE TTVNO_TRANSAKSI_RJ='{}' ".format(
                    isianPoli["KPNO_TRANSAKSI"]
                )
                Globals().executeQuery(qUpdateStatus)
            except:
                print("===gagal  response TTV SPO2 condition")
                print(dataBridging)
                print("===response condition response TTV SPO2")
        ################### SPO2

        # ################### TD
        if STATUS_SISTOLE == "0":
            # if len(int(isianPoli["TD"]).split("/")) > 2:
            try:
                payload = {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                    "display": "Vital Signs",
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "35094-2",
                                "display": "Blood pressure panel",
                            }
                        ],
                        "text": "Blood pressure systolic & diastolic",
                    },
                    "subject": {
                        "reference": "Patient/{}".format(isianPoli["PKD_PASIEN_FHIR"])
                    },
                    "performer": [
                        {
                            "reference": "Practitioner/{}".format(
                                isianPoli["SSFHIR_KD_DOKTER"]
                            )
                        }
                    ],
                    "encounter": {
                        "reference": "Encounter/{}".format(
                            isianPoli["PSD_NO_TRANSAKSI_FHIR"]
                        ),
                        "display": "Pemeriksaan Fisik TD RJ atas Nama {} di tanggal {} {}".format(
                            isianPoli["NAMAPASIEN"],
                            isianPoli["TGLINDO"],
                            isianPoli["JAMRS_ASLI"],
                        ),
                    },
                    "effectiveDateTime": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "issued": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "component": [
                        {
                            "code": {
                                "coding": [
                                    {
                                        "system": "http://loinc.org",
                                        "code": "8480-6",
                                        "display": "Systolic blood pressure",
                                    }
                                ]
                            },
                            "valueQuantity": {
                                "value": SISTOLS,
                                "unit": "mmHg",
                                "system": "http://unitsofmeasure.org",
                                "code": "mm[Hg]",
                            },
                        },
                        {
                            "code": {
                                "coding": [
                                    {
                                        "system": "http://loinc.org",
                                        "code": "8462-4",
                                        "display": "Diastolic blood pressure",
                                    }
                                ]
                            },
                            "valueQuantity": {
                                "value": DIASTOLS,
                                "unit": "mmHg",
                                "system": "http://unitsofmeasure.org",
                                "code": "mm[Hg]",
                            },
                        },
                    ],
                }
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "SIMKLINIK MEDISIMED SAVE CONDITION",
                    "Authorization": "Bearer " + getToken(request),
                }
                # BRIDGING

                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                # BRIDGING
                # print("===sukses  response TTV TENSI condition")
                # print(dataBridging)
                # print("===response condition response TTV TENSI")
                qUpdateStatus = " UPDATE EMRRJ_TTV SET STATUS_TTV_TENSI_SISTOLE=GETDATE() WHERE TTVNO_TRANSAKSI_RJ='{}' ".format(
                    isianPoli["KPNO_TRANSAKSI"]
                )
                Globals().executeQuery(qUpdateStatus)

                # RECORD SUDAH BRIDING

            except:
                print("===gagal  response TTV TENSI condition")
                print(dataBridging)
                print("===response condition response TTV TENSI")
            # else:
            #     print("===gagal  response TTV TENSI condition")
        ################### TD

        # ################### TB
        if STATUS_TB == "0":
            try:
                payload = {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                    "display": "Vital Signs",
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8302-2",
                                "display": "Body height",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/{}".format(isianPoli["PKD_PASIEN_FHIR"])
                    },
                    "performer": [
                        {
                            "reference": "Practitioner/{}".format(
                                isianPoli["SSFHIR_KD_DOKTER"]
                            )
                        }
                    ],
                    "encounter": {
                        "reference": "Encounter/{}".format(
                            isianPoli["PSD_NO_TRANSAKSI_FHIR"]
                        ),
                        "display": "Pemeriksaan Fisik Tinggi Badan atas Nama {} di tanggal {} {}".format(
                            isianPoli["NAMAPASIEN"],
                            isianPoli["TGLINDO"],
                            isianPoli["JAMRS_ASLI"],
                        ),
                    },
                    "effectiveDateTime": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "issued": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "valueQuantity": {
                        "value": TBS,
                        "unit": "centimeter",
                        "system": "http://unitsofmeasure.org",
                        "code": "cm",
                    },
                }

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "SIMKLINIK MEDISIMED SAVE OBSERVATION",
                    "Authorization": "Bearer " + getToken(request),
                }
                # BRIDGING
                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                # BRIDGING
                # print("===sukses  response TTV TB condition")
                # print(dataBridging)
                # print("===response condition response TTV TB")
                qUpdateStatus = " UPDATE EMRRJ_TTV SET STATUS_TTV_TB=GETDATE() WHERE TTVNO_TRANSAKSI_RJ='{}' ".format(
                    isianPoli["KPNO_TRANSAKSI"]
                )
                Globals().executeQuery(qUpdateStatus)

                # RECORD SUDAH BRIDING

            except:
                print("===gagal  response TTV TB condition")
                print(dataBridging)
                print("===response condition response TTV TB")
        ################### TB

        # ################### BB
        if STATUS_BB == "0":
            try:
                payload = {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                    "display": "Vital Signs",
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "29463-7",
                                "display": "Body Weight",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/{}".format(isianPoli["PKD_PASIEN_FHIR"])
                    },
                    "performer": [
                        {
                            "reference": "Practitioner/{}".format(
                                isianPoli["SSFHIR_KD_DOKTER"]
                            )
                        }
                    ],
                    "encounter": {
                        "reference": "Encounter/{}".format(
                            isianPoli["PSD_NO_TRANSAKSI_FHIR"]
                        ),
                        "display": "Pemeriksaan Fisik Berat Badan atas Nama {} di tanggal {} {}".format(
                            isianPoli["NAMAPASIEN"],
                            isianPoli["TGLINDO"],
                            isianPoli["JAMRS_ASLI"],
                        ),
                    },
                    "effectiveDateTime": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "issued": "{}T{}+07:00".format(
                        isianPoli["TGLRS"], isianPoli["JAMRS"]
                    ),
                    "valueQuantity": {
                        "value": BBS,
                        "unit": "kg",
                        "system": "http://unitsofmeasure.org",
                        "code": "kg",
                    },
                }

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "SIMKLINIK MEDISIMED SAVE OBSERVATION",
                    "Authorization": "Bearer " + getToken(request),
                }
                # BRIDGING
                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                # print("===sukses  response TTV BB condition")
                # print(dataBridging)
                # print("===response condition response TTV BB")
                qUpdateStatus = " UPDATE EMRRJ_TTV SET STATUS_TTV_BB=GETDATE() WHERE TTVNO_TRANSAKSI_RJ='{}' ".format(
                    isianPoli["KPNO_TRANSAKSI"]
                )
                Globals().executeQuery(qUpdateStatus)

                # RECORD SUDAH BRIDING

            except:
                print("===gagal  response TTV BB condition")
                print(dataBridging)
                print("===response condition response TTV BB")
        ################### BB
    res = {
        "success": True,
        "message": "Sukses Bridging ",
    }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def SrvIndoProses_satu_sehat(request):
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    if 'tglAwal' in request.GET:
        tglAwal = request.GET["tglAwal"]
        tglAkhir = request.GET["tglAkhir"]
        url = getattr(
            env,
            "SERVER_INDO",
            "",
        ) + "bridge_satu_sehat/proses_satu_sehat?kdCabang={}&tglAwal={}&tglAkhir={}".format(
            kdCabang, tglAwal, tglAkhir
        )
        headers = {
            "Content-Type": "application/json",
            # "Authorization": "Bearer {}".format(getToken(request)),
            "User-Agent": "SIMKLINIK MEDISIMED",
        }
    else:
        url = getattr(
            env,
            "SERVER_INDO",
            "",
        ) + "bridge_satu_sehat/proses_satu_sehat?kdCabang={}".format(
            kdCabang
        )
        headers = {
            "Content-Type": "application/json",
            # "Authorization": "Bearer {}".format(getToken(request)),
            "User-Agent": "SIMKLINIK MEDISIMED",
        }

    # print('url')
    # print(url)
    # print(headers)
    payload = {}
    json_data = {}
    json_data = requests.get(url)
    return HttpResponse(json_data, content_type="application/json")
