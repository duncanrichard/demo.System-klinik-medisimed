from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.db import connection
from django.db import connections
from calendar import monthrange
import datetime
from datetime import *

# from datetime import datetime
import json
import simplejson as json
from django.core import serializers
from django.db import transaction
from django.db import IntegrityError

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
import os
import json
from django.conf import settings
import decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.db import DatabaseError
from IMMODERMA.globals import Globals
from IMMODERMA.environment import env

# Create your views here.
import hmac
import OpenSSL
import hashlib
import binascii
from base64 import b64decode
from base64 import b64encode
from Crypto import Random
from Crypto.Cipher import AES
import json
import requests
import base64
from decimal import Decimal

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from base64 import b64encode, b64decode


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


def getOrganization(request):
    url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_ADA") + "/Organization/{}".format(
        getattr(env, "SATU_SEHAT_Organization", "BELUM_ADA")
    )
    # print(getToken(request))
    headers = {
        "Authorization": "Bearer " + getToken(request),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    json_data = requests.get(url, headers=headers)
    return HttpResponse(json_data.text, content_type="application/json")
    # return json_data.text
    # return json.loads(json_data.text)["access_token"]


def getOrganizationInternet(request, id):
    url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_ADA") + "/Organization/{}".format(
        id
    )
    # print(getToken(request))
    headers = {
        "Authorization": "Bearer " + getToken(request),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    json_data = requests.get(url, headers=headers)
    return json.loads(json_data.text)


def getIHSPatientNumber(request):
    # print('url')
    nik = request.GET["nik"]
    url = getattr(
        env,
        "SATU_SEHAT_URL_DATA",
        "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
    ) + "/Patient?identifier=https://fhir.kemkes.go.id/id/nik|{}".format(nik)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    # print('url')
    # print(url)
    # print(headers)
    payload = {}
    json_data = {}
    json_data = requests.get(url, data=payload, headers=headers)
    return HttpResponse(json_data, content_type="application/json")

def getIHSPatientName(request):
    # print('url')
    name = request.GET["name"]
    birthdate = request.GET["birthdate"]
    gender = request.GET["gender"]
    url = getattr(
        env,
        "SATU_SEHAT_URL_DATA",
        "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
    ) + "/Patient?name={}&birthdate={}&gender={}".format(name,birthdate,gender)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    # print('url')
    # print(url)
    # print(headers)
    payload = {}
    json_data = {}
    json_data = requests.get(url, data=payload, headers=headers)
    # print(json_data.text)
    return HttpResponse(json_data, content_type="application/json")

def getidKelurahan(request):
    idKelurahan = request.GET["idKelurahan"]
    q = "select a.KD_KELURAHAN,a.KELURAHAN,b.KD_KECAMATAN,b.KECAMATAN,c.KD_KABUPATEN,c.KABUPATEN,d.KD_PROPINSI,d.PROPINSIN "
    q +="from KELURAHAN a inner join KECAMATAN b on a.KD_KECAMATAN=b.KD_KECAMATAN "
    q +="inner join KABUPATEN c on b.KD_KABUPATEN=c.KD_KABUPATEN "
    q +="inner join PROPINSI d on c.KD_PROPINSI=d.KD_PROPINSI where a.KD_KELURAHAN=%s "
    result = Globals().getDataQuery(q,[idKelurahan])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getIHSPatientNumberNorm(request):
    # print('url')
    norm = request.GET["norm"]

    cursor = connection.cursor()
    q = "SELECT * FROM PASIEN A WHERE A.KD_PASIEN='{}'".format(norm)
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    nik = result[0]["NO_PENGENAL"]
    if len(result) > 0:
        url = getattr(
            env,
            "SATU_SEHAT_URL_DATA",
            "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
        ) + "/Patient?identifier=https://fhir.kemkes.go.id/id/nik|{}".format(nik)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(getToken(request)),
            "User-Agent": "SIMKLINIK MEDISIMED",
        }
        # print('url')
        # print(url)
        # print(headers)
        payload = {}
        json_data = {}
        json_data = requests.get(url, data=payload, headers=headers)
        # print(json_data)
        # print(json_data.status_code)
        # print(json.dumps(json_data))
        return HttpResponse(json_data, content_type="application/json")


def saveOrganization(request):
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    q = "select a.CABANG_ID,a.PERUSAHAAN,a.ALAMAT1,KOTA_ID,KOTA,KODE_POS,TELEPON,no_whatsapp,email,website,KONTAK,JABATAN,NPWP,TGLPENGUKUHAN,USING,a.ppkpelayanan,consid,secret,bpjs_userkey,userncc,passwordncc,ijinSIP,user_icare,password_icare,statusmjkn,client_id,organization_id,Secret_key,SS_FHIR_KD_CABANG,   "
    q += "b.KD_KELURAHAN,b.KELURAHAN,c.KD_KECAMATAN,c.KECAMATAN,isnull(d.KD_KABUPATEN,a.KOTA_ID) as KD_KABUPATEN,isnull(d.KABUPATEN,KOTA) as KABUPATEN,e.KD_PROPINSI,e.PROPINSIN from CABANG a "
    q += "left join KELURAHAN b on a.KOTA_ID=b.KD_KELURAHAN  "
    q += "left join KECAMATAN c on b.KD_KECAMATAN=c.KD_KECAMATAN "
    q += "left join KABUPATEN d on c.KD_KABUPATEN=d.KD_KABUPATEN "
    q += "left join PROPINSI e on d.KD_PROPINSI=e.KD_PROPINSI "
    q += "WHERE CABANG_ID= %s "
    result = Globals().getDataQuery(q, [kdCabang])
    url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_INPUT_URL") + "/Organization"
    instalasi = result[0]["PERUSAHAAN"]
    kdInstalasi = result[0]["organization_id"]
    payload = {
        "resourceType": "Organization",
        "active": True,
        "identifier": [
            {
                "use": "official",
                "system": "http://sys-ids.kemkes.go.id/organization/{}".format(
                    kdInstalasi
                ),
                "value": "{}".format(kdInstalasi),
            }
        ],
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                        "code": "dept",
                        "display": "Hospital Department",
                    }
                ]
            }
        ],
        "name": "" + instalasi,
        "telecom": [
            {
                "system": "phone",
                "value": "{}".format(result[0]["TELEPON"]),
                "use": "work",
            },
            {
                "system": "email",
                "value": "{}".format(result[0]["email"]),
                "use": "work",
            },
            {
                "system": "url",
                "value": "{}".format(result[0]["website"]),
                "use": "work",
            },
        ],
        "address": [
            {
                "use": "work",
                "type": "both",
                "line": ["{}".format(result[0]["ALAMAT1"])],
                "city": "{}".format(result[0]["KOTA_ID"]),
                "postalCode": "{}".format(result[0]["KODE_POS"]),
                "country": "ID",
                "extension": [
                    {
                        "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/administrativeCode",
                        "extension": [
                            {
                                "url": "province",
                                "valueCode": "{}".format(result[0]["KD_PROPINSI"]),
                            },
                            {
                                "url": "city",
                                "valueCode": "{}".format(result[0]["KD_KABUPATEN"]),
                            },
                            {
                                "url": "district",
                                "valueCode": "{}".format(result[0]["KD_KECAMATAN"]),
                            },
                            {
                                "url": "village",
                                "valueCode": "{}".format(result[0]["KD_KELURAHAN"]),
                            },
                        ],
                    }
                ],
            }
        ],
        "partOf": {"reference": "Organization/{}".format(result[0]["organization_id"])},
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SIMKLINIK MEDISIMED SAVE ORG",
        "Authorization": "Bearer " + getToken(request),
    }
    # print(url)
    # print(headers)
    # print(payload)
    json_data = requests.post(url, headers=headers, data=json.dumps(payload))
    dataBridging = json.loads(json_data.text)
    try:
        qInsertPoli = (
            "UPDATE CABANG SET SS_FHIR_KD_CABANG='{}' WHERE CABANG_ID= %s ".format(
                dataBridging["id"]
            )
        )
        Globals().executeQuery(qInsertPoli, [kdCabang])
        res = {
            "success": True,
            "message": dataBridging["id"],
        }
    except:
        print("===response")
        print(dataBridging)
        print("===response")
        res = {
            "success": False,
            "message": "gagal Bridging",
        }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def saveOrganization_SrvIndo(request):
    kdCabang = request.session["kdCabang"]
    url = getattr(
        env,
        "SERVER_INDO",
        "",
    ) + "/views_satu_sehat/saveOrganization?kdCabang={}".format(kdCabang)
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


def savePatient(request, norm=""):
    q = "SELECT  A.KD_PASIEN,A.PKD_PASIEN_FHIR  FROM PASIEN A WHERE ISNULL(A.PKD_PASIEN_FHIR,'')<>'' AND A.KD_PASIEN='{}'".format(
        norm
    )
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)

    if len(result) > 0:
        greeting("TIDAK INSERT PASIEN " + result[0]["PKD_PASIEN_FHIR"])
        json_data = json.dumps(
            {"success": True, "KD_PASIEN_FHIR": result[0]["PKD_PASIEN_FHIR"]},
            cls=DjangoJSONEncoder,
        )
    else:
        PKD_PASIEN_FHIR = "-"
        q = "SELECT  "
        q += " KEL.KELURAHAN"
        q += " ,KEC.KECAMATAN"
        q += " ,KAB.KABUPATEN,PRP.PROPINSIN"
        q += " ,convert(varchar,A.TGL_LAHIR,23) as TGL_LAHIR"
        q += " ,A.ALAMAT as ALAMAT,A.KD_PASIEN,A.NO_PENGENAL,A.NAMAPASIEN,A.TELEPON"
        q += " ,LEFT(A.KD_KELURAHAN,2) as province"
        q += " ,LEFT(A.KD_KELURAHAN,4) as city"
        q += " ,LEFT(A.KD_KELURAHAN,7) as district"
        q += " ,LEFT(A.KD_KELURAHAN,10) as village"
        q += " ,IIF(A.JENIS_KELAMIN='1','male','female') as JK"
        q += " FROM PASIEN A"
        q += " LEFT JOIN PROPINSI PRP ON LEFT(A.KD_KELURAHAN,2)=PRP.KD_PROPINSI"
        q += " LEFT JOIN KABUPATEN KAB ON LEFT(A.KD_KELURAHAN,4)=KAB.KD_KABUPATEN"
        q += " LEFT JOIN KECAMATAN KEC ON LEFT(A.KD_KELURAHAN,7)=KEC.KD_KECAMATAN"
        q += " LEFT JOIN KELURAHAN KEL ON LEFT(A.KD_KELURAHAN,10)=KEL.KD_KELURAHAN"
        q += " WHERE A.KD_PASIEN='{}'".format(norm)
        cursor.execute(q)
        result = Globals().dictfetchall(cursor)
        kdPasien = result[0]["KD_PASIEN"]
        namaPasien = result[0]["NAMAPASIEN"]
        KABUPATEN = result[0]["KABUPATEN"]
        province = result[0]["province"]
        city = result[0]["city"]
        district = result[0]["district"]
        village = result[0]["village"]
        TGL_LAHIR = result[0]["TGL_LAHIR"]
        JK = result[0]["JK"]
        NO_PENGENAL = result[0]["NO_PENGENAL"]
        TELEPON = result[0]["TELEPON"]
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
        # print(payload)
        json_data = requests.get(url, data=payload, headers=headers)
        dataBridging = json.loads(json_data.text)
        # print("===response")
        # print(dataBridging)
        # print("===response")
        # print(kdPoli)
        try:
            PKD_PASIEN_FHIR = dataBridging["entry"][0]["resource"]["id"]
            qInsertPoli = "INSERT INTO SATUSEHAT_PASIEN(PKD_PASIEN,PKD_PASIEN_FHIR) VALUES ('{}','{}')".format(
                kdPasien, PKD_PASIEN_FHIR
            )
            cursor.execute(qInsertPoli)
            greeting("INSERT PASIEN " + dataBridging["id"])
        except:
            print("===response")
            print(dataBridging)
            print("===response")
            greeting("TIDAK INSERT PASIEN ")

        json_datas = {}
        json_data = json.dumps(
            {"success": True, "KD_PASIEN_FHIR": PKD_PASIEN_FHIR}, cls=DjangoJSONEncoder
        )

    return json_data
    # return HttpResponse(json_data, content_type="application/json")


def saveEncounterKunjungan(request):
    cursor = connection.cursor()
    q = "SELECT CABANG.* "
    q += " ,KABUPATEN.KABUPATEN"
    q += " FROM CABANG"
    q += " LEFT JOIN KABUPATEN ON CABANG.SS_FHIR_kota=KABUPATEN.KD_KABUPATEN"
    cursor.execute(q)
    resultCabang = Globals().dictfetchall(cursor)
    cursor.close()

    cursor = connection.cursor()
    q = " SELECT dbo.EMR_GET_USER(KUNJ.KPKD_DOKTER) as NAMADOKTER,PL.FMPKLINIKN as POLIN,KUNJ.KPNO_TRANSAKSI as NOTRANS "
    q += " ,ISNULL(PL.SSFHIR_KD_POLI,'-')  as KDPOLI_FHIR"
    q += " ,ISNULL(DOK.SSFHIR_KD_DOKTER,'-') as KD_KDDOKTER_FHIR"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,CAST((CONVERT(varchar(10),CONVERT(date,KPTGL_PERIKSA),112) + ' ' +CONVERT(varchar(8),CONVERT(time,KUNJ.KPJAM_MASUK))) as datetime)),126)+'+07:00' as TGLJAM_START"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,CAST ((CONVERT(varchar(10),CONVERT(date,KPTGL_PERIKSA),112)+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_1,TI.taskid_2),KUNJ.KPJAM_MASUK)))) as datetime)),126)+'+07:00' as TGLJAM_PROGRESS"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,ISNULL(CAST(CONVERT(varchar(10),(ISNULL(CONVERT(date,KPTGL_KELUAR),CONVERT(date,KPTGL_PERIKSA))),112)+' '+(CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_5,TI.taskid_7),KUNJ.KPJAM_KELUAR)))) as datetime),CAST((CONVERT(varchar(10),CONVERT(date,KPTGL_PERIKSA),112) + ' ' +CONVERT(varchar(8),CONVERT(time,KUNJ.KPJAM_MASUK))) as datetime))),126)+'+07:00' as TGLJAM_END"
    q += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_1,TI.taskid_3),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_START"
    q += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_2,TI.taskid_4),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_PROGRESS"
    q += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_5,TI.taskid_7),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_END"
    q += " ,PS.NAMAPASIEN,ISNULL(PS.SSFHIR_KD_PASIEN,'-') as KD_PASIEN_FHIR"
    q += " ,KUNJ.KPTGL_PERIKSA as TGLRS,KUNJ.KPKD_DOKTER as KDDOKTERRS,KUNJ.KPKD_POLY as POLIRS,KUNJ.KPKD_PASIEN as KDASIENRS"
    q += " FROM KUNJUNGANPASIEN KUNJ"
    q += " INNER JOIN POLIKLINIK PL ON KUNJ.KPKD_POLY=PL.FMPKLINIK_ID"
    q += " LEFT JOIN PASIEN PS ON KUNJ.KPKD_PASIEN=PS.KD_PASIEN"
    q += "  LEFT JOIN DOKTER DOK ON KUNJ.KPKD_DOKTER=DOK.FMDDOKTER_ID "
    # q +=" LEFT JOIN SATUSEHAT_PASIEN PSN ON KUNJ.KPKD_PASIEN=PSN.PKD_PASIEN"
    # q +=" LEFT JOIN SATUSEHAT_POLIKLINIK POLI ON KUNJ.KPKD_POLY=POLI.KD_POLI"
    q += " LEFT JOIN PASIEN_RUJUKAN PRJ ON KUNJ.KPNO_TRANSAKSI=PRJ.FRPNOTRANSAKSIKJ"
    q += " LEFT JOIN TOMBOL_ANTRIAN.dbo.BPJS_TASKID TI ON  KUNJ.KPTGL_PERIKSA=TI.tanggal AND KUNJ.KPKD_POLY= TI.kode_poli"
    q += " AND PRJ.FRPNOANTRIDOKTER=TI.no "
    q += " WHERE"
    if "TGLPERIKSA" in request.GET:
        q += " CONVERT(date,KUNJ.KPTGL_PERIKSA)='{}'".format(request.GET["TGLPERIKSA"])
    else:
        q += " CONVERT(date,KUNJ.KPTGL_PERIKSA)=CONVERT(date,GETDATE())"
    q += " AND PS.NO_PENGENAL IS NOT NULL"
    q += " AND ISNULL(DOK.SSFHIR_KD_DOKTER,'-')<>'-'"
    q += " AND KUNJ.KPNO_TRANSAKSI NOT IN (SELECT PKU.PSD_NO_TRANSAKSI_RS FROM SATUSEHAT_KUNJUNGAN PKU "
    q += " WHERE PKU.PSD_KD_DOKTER=KUNJ.KPKD_DOKTER "
    q += " AND PKU.PSD_KD_POLI=KUNJ.KPKD_POLY "
    q += " AND PKU.PSD_KD_DOKTER=KUNJ.KPKD_DOKTER"
    q += " AND PKU.PSD_NO_TRANSAKSI_RS=KUNJ.KPNO_TRANSAKSI)"
    q += " AND PL.FMPKLINIK_ID NOT IN('PK019','PK018')"
    q += " AND len(PS.NO_PENGENAL)>10"

    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    cursor.close()
    # print(q)
    counter = 0
    for isianPoli in result:
        if counter == 0:
            greeting("Laporan ADD KUNJUNGAN FHIR...")

        # print(isianPoli["KD_PASIEN_FHIR"])
        KD_PASIEN_FHIR = "-"
        KD_PASIEN_FHIR = isianPoli["KD_PASIEN_FHIR"]
        if KD_PASIEN_FHIR == "-":
            KD_PASIEN_FHIR = "-"
            dataPasien = json.loads(savePatient(request, isianPoli["KDASIENRS"]))
            # print(dataPasien['KD_PASIEN_FHIR'])
            KD_PASIEN_FHIR = dataPasien["KD_PASIEN_FHIR"]
            greeting("PASIEN BARU " + KD_PASIEN_FHIR)
        else:
            greeting("PASIEN LAMA " + KD_PASIEN_FHIR)
        # return 0
        # namaDokter="ANNI NURHADIYATI DRG"
        # kdDokter="IF002"
        url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_ADA_LINK") + "/Encounter"

        payload = {
            "resourceType": "Encounter",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {
                "reference": "Patient/{}".format(KD_PASIEN_FHIR),
                "display": "{}".format(isianPoli["NAMAPASIEN"]),
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
                            isianPoli["KD_KDDOKTER_FHIR"]
                        ),
                        "display": "{}".format(isianPoli["NAMADOKTER"]),
                    },
                }
            ],
            "period": {
                "start": "{}".format(isianPoli["TGLJAM_START"]),
                "end": "{}".format(isianPoli["TGLJAM_END"]),
            },
            "location": [
                {
                    "location": {
                        "display": "{}".format(isianPoli["POLIN"]),
                        "reference": "Location/{}".format(isianPoli["KDPOLI_FHIR"]),
                    }
                }
            ],
            "statusHistory": [
                {
                    "period": {
                        "start": "{}".format(isianPoli["TGLJAM_START"]),
                        "end": "{}".format(isianPoli["TGLJAM_START"]),
                    },
                    "status": "arrived",
                },
                {
                    "period": {
                        "start": "{}".format(isianPoli["TGLJAM_START"]),
                        "end": "{}".format(isianPoli["TGLJAM_PROGRESS"]),
                    },
                    "status": "in-progress",
                },
                {
                    "period": {
                        "start": "{}".format(isianPoli["TGLJAM_PROGRESS"]),
                        "end": "{}".format(isianPoli["TGLJAM_END"]),
                    },
                    "status": "finished",
                },
            ],
            "serviceProvider": {
                "reference": "Organization/{}".format(
                    resultCabang[0]["SS_FHIR_KD_CABANG"]
                )
            },
            "identifier": [
                {
                    "system": "http://sys-ids.kemkes.go.id/encounter/{}".format(
                        resultCabang[0]["SS_FHIR_KD_CABANG"]
                    ),
                    "value": "{}".format(isianPoli["NOTRANS"]),
                }
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE ENCOUNTER",
            "Authorization": "Bearer " + getToken(request),
        }
        # print(headers)
        # print(payload)
        # exit()
        try:
            if KD_PASIEN_FHIR != "-":
                json_data = requests.post(
                    url, headers=headers, data=json.dumps(payload)
                )
                dataBridging = json.loads(json_data.text)
                print("===response saveencounter")
                print(dataBridging)
                print("===response saveencounter")
                greeting(
                    "Berhasil Bridging {}\n {} ({}) \n {} {}".format(
                        isianPoli["TGLRS"],
                        isianPoli["NOTRANS"],
                        dataBridging["id"],
                        isianPoli["NAMAPASIEN"],
                        isianPoli["POLIN"],
                    )
                )
            else:
                greeting(
                    " GAGAL  BRIDING{}\n {} \n {} {}".format(
                        isianPoli["TGLRS"],
                        isianPoli["NOTRANS"],
                        isianPoli["NAMAPASIEN"],
                        isianPoli["POLIN"],
                    )
                )
        except:
            print("===response error")
            print("===response saveencounter")
            print(dataBridging)
            print("===response saveencounter")
            greeting(
                " GAGAL  BRIDING{}\n {} \n {} {}".format(
                    isianPoli["TGLRS"],
                    isianPoli["NOTRANS"],
                    isianPoli["NAMAPASIEN"],
                    isianPoli["POLIN"],
                )
            )

        # print("===response saveencounter")
        # print(dataBridging)
        # print("===response saveencounter")
        try:
            greeting(
                "Berhasil Save Bridging DB {} ({})".format(
                    isianPoli["NOTRANS"], dataBridging["id"]
                )
            )
            cursor = connection.cursor()
            qInsertPoli = "INSERT INTO SATUSEHAT_KUNJUNGAN(PSD_NO_TRANSAKSI_RS,PSD_NO_TRANSAKSI_FHIR,PSD_TGL,PSD_KD_DOKTER,PSD_KD_POLI,PSDCREATED_AT) "
            qInsertPoli += "VALUES ('{}','{}','{}','{}','{}',GETDATE())".format(
                isianPoli["NOTRANS"],
                dataBridging["id"],
                isianPoli["TGLRS"],
                isianPoli["KDDOKTERRS"],
                isianPoli["POLIRS"],
            )
            cursor.execute(qInsertPoli)
            cursor.close()
        except:
            greeting(
                "GAGAL INSERT KARENA GAGAL BRIDGING {}\n {} \n {} {}".format(
                    isianPoli["TGLRS"],
                    isianPoli["NOTRANS"],
                    isianPoli["NAMAPASIEN"],
                    isianPoli["POLIN"],
                )
            )
            print("===response dokter")
            print(dataBridging)
            print("===response dokter")
        counter += 1

    return HttpResponse({"success": True}, content_type="application/json")


def updateEncounterKunjungan(request):
    cursor = connection.cursor()
    q = "SELECT CABANG.* "
    q += " ,KABUPATEN.KABUPATEN"
    q += " FROM CABANG"
    q += " LEFT JOIN KABUPATEN ON CABANG.SS_FHIR_kota=KABUPATEN.KD_KABUPATEN"
    cursor.execute(q)
    resultCabang = Globals().dictfetchall(cursor)
    cursor.close()

    cursor = connection.cursor()
    q = " SELECT dbo.EMR_GET_USER(KUNJ.KPKD_DOKTER) as NAMADOKTER,PL.FMPKLINIKN as POLIN,KUNJ.KPNO_TRANSAKSI as NOTRANS "
    q += " ,ISNULL(PL.SSFHIR_KD_POLI,'-')  as KDPOLI_FHIR"
    q += " ,ISNULL(DOK.SSFHIR_KD_DOKTER,'-') as KD_KDDOKTER_FHIR"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,CAST((CONVERT(varchar(10),CONVERT(date,KPTGL_PERIKSA),112) + ' ' +CONVERT(varchar(8),CONVERT(time,KUNJ.KPJAM_MASUK))) as datetime)),126)+'+07:00' as TGLJAM_START"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,CAST ((CONVERT(varchar(10),CONVERT(date,KPTGL_PERIKSA),112)+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_1,TI.taskid_2),KUNJ.KPJAM_MASUK)))) as datetime)),126)+'+07:00' as TGLJAM_PROGRESS"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,ISNULL(CAST(CONVERT(varchar(10),(ISNULL(CONVERT(date,KPTGL_KELUAR),CONVERT(date,KPTGL_PERIKSA))),112)+' '+(CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_5,TI.taskid_7),KUNJ.KPJAM_KELUAR)))) as datetime),CAST((CONVERT(varchar(10),CONVERT(date,KPTGL_PERIKSA),112) + ' ' +CONVERT(varchar(8),CONVERT(time,KUNJ.KPJAM_MASUK))) as datetime))),126)+'+07:00' as TGLJAM_END"
    q += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_1,TI.taskid_3),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_START"
    q += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_2,TI.taskid_4),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_PROGRESS"
    q += " ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_5,TI.taskid_7),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_END"
    q += " ,PS.NAMAPASIEN,ISNULL(PS.SSFHIR_KD_PASIEN,'-') as KD_PASIEN_FHIR"
    q += " ,KUNJ.KPTGL_PERIKSA as TGLRS,KUNJ.KPKD_DOKTER as KDDOKTERRS,KUNJ.KPKD_POLY as POLIRS,KUNJ.KPKD_PASIEN as KDASIENRS"
    q += " FROM KUNJUNGANPASIEN KUNJ"
    q += " INNER JOIN POLIKLINIK PL ON KUNJ.KPKD_POLY=PL.FMPKLINIK_ID"
    q += " LEFT JOIN PASIEN PS ON KUNJ.KPKD_PASIEN=PS.KD_PASIEN"
    q += "  LEFT JOIN DOKTER DOK ON KUNJ.KPKD_DOKTER=DOK.FMDDOKTER_ID "
    # q +=" LEFT JOIN SATUSEHAT_PASIEN PSN ON KUNJ.KPKD_PASIEN=PSN.PKD_PASIEN"
    # q +=" LEFT JOIN SATUSEHAT_POLIKLINIK POLI ON KUNJ.KPKD_POLY=POLI.KD_POLI"
    q += " LEFT JOIN PASIEN_RUJUKAN PRJ ON KUNJ.KPNO_TRANSAKSI=PRJ.FRPNOTRANSAKSIKJ"
    q += " LEFT JOIN TOMBOL_ANTRIAN.dbo.BPJS_TASKID TI ON  KUNJ.KPTGL_PERIKSA=TI.tanggal AND KUNJ.KPKD_POLY= TI.kode_poli"
    q += " AND PRJ.FRPNOANTRIDOKTER=TI.no "
    q += " WHERE"
    if "TGLPERIKSA" in request.GET:
        q += " CONVERT(date,KUNJ.KPTGL_PERIKSA)='{}'".format(request.GET["TGLPERIKSA"])
    else:
        q += " CONVERT(date,KUNJ.KPTGL_PERIKSA)=CONVERT(date,GETDATE())"
    q += " AND PS.NO_PENGENAL IS NOT NULL"
    q += " AND ISNULL(DOK.SSFHIR_KD_DOKTER,'-')<>'-'"
    q += " AND KUNJ.KPNO_TRANSAKSI NOT IN (SELECT PKU.PSD_NO_TRANSAKSI_RS FROM SATUSEHAT_KUNJUNGAN PKU "
    q += " WHERE PKU.PSD_KD_DOKTER=KUNJ.KPKD_DOKTER "
    q += " AND PKU.PSD_KD_POLI=KUNJ.KPKD_POLY "
    q += " AND PKU.PSD_KD_DOKTER=KUNJ.KPKD_DOKTER"
    q += " AND PKU.PSD_NO_TRANSAKSI_RS=KUNJ.KPNO_TRANSAKSI)"
    q += " AND PL.FMPKLINIK_ID NOT IN('PK019','PK018')"
    q += " AND KUNJ.KPNO_TRANSAKSI  IN (SELECT SI.SS_NO_TRANS_RS  FROM SATUSEHAT_ICD10 SI)"

    # q ="  SELECT dbo.EMR_GET_USER(KUNJ.KPKD_DOKTER) as NAMADOKTER,SK.PSD_NO_TRANSAKSI_FHIR,PL.FMPKLINIKN as POLIN,KUNJ.KPNO_TRANSAKSI as NOTRANS "
    # q +=" ,ISNULL(POLI.USERID,'-') as KDPOLI_FHIR"
    # q +=" ,ISNULL(DOK.SS_KD_DOKTER,'-') as KD_KDDOKTER_FHIR"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_1,TI.taskid_3),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_START"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_2,TI.taskid_4),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_PROGRESS"
    # q +=" ,CONVERT(varchar,DATEADD(HOUR, -7,CAST(CONVERT(varchar(10),CONVERT(date,getdate()))+' '+CONVERT(varchar(8),CONVERT(time,ISNULL(ISNULL(TI.taskid_5,TI.taskid_7),getdate()))) AS datetime)),126)+'+07:00' as TGLJAM_END"
    # q +=" ,PS.NAMAPASIEN,ISNULL(PSN.PKD_PASIEN_FHIR,'-') as KD_PASIEN_FHIR"
    # q +=" ,KUNJ.KPTGL_PERIKSA as TGLRS,KUNJ.KPKD_DOKTER as KDDOKTERRS,KUNJ.KPKD_POLY as POLIRS,KUNJ.KPKD_PASIEN as KDASIENRS"
    # q +=" FROM KUNJUNGANPASIEN KUNJ"
    # q +=" INNER JOIN POLIKLINIK PL ON KUNJ.KPKD_POLY=PL.FMPKLINIK_ID"
    # q +=" INNER JOIN SATUSEHAT_KUNJUNGAN SK ON KUNJ.KPNO_TRANSAKSI=SK.PSD_NO_TRANSAKSI_RS"
    # q +=" LEFT JOIN PASIEN PS ON KUNJ.KPKD_PASIEN=PS.KD_PASIEN"
    # q +=" LEFT JOIN SATUSEHAT_DOKTER DOK ON KUNJ.KPKD_DOKTER=DOK.KD_DOKTER"
    # q +=" LEFT JOIN SATUSEHAT_PASIEN PSN ON KUNJ.KPKD_PASIEN=PSN.PKD_PASIEN"
    # q +=" LEFT JOIN SATUSEHAT_POLIKLINIK POLI ON KUNJ.KPKD_POLY=POLI.KD_POLI"
    # q +=" LEFT JOIN PASIEN_RUJUKAN PRJ ON KUNJ.KPNO_TRANSAKSI=PRJ.FRPNOTRANSAKSIKJ"
    # q +=" LEFT JOIN TOMBOL_ANTRIAN.dbo.BPJS_TASKID TI ON  KUNJ.KPTGL_PERIKSA=TI.tanggal AND KUNJ.KPKD_POLY= TI.kode_poli"
    # q +=" AND PRJ.FRPNOANTRIDOKTER=TI.no "
    # q +=" WHERE"
    # if 'TGLPERIKSA' in request.GET:
    #     q +=" CONVERT(date,KUNJ.KPTGL_PERIKSA)='{}'".format(request.GET['TGLPERIKSA'])
    # else:
    #     q +=" CONVERT(date,KUNJ.KPTGL_PERIKSA)=CONVERT(date,GETDATE())"
    # q +=" AND DOK.SS_KD_DOKTER<>'-'"
    # q +=" AND KUNJ.KPNO_TRANSAKSI  IN (SELECT PKU.PSD_NO_TRANSAKSI_RS FROM SATUSEHAT_KUNJUNGAN PKU "
    # q +=" WHERE PKU.PSD_KD_DOKTER=KUNJ.KPKD_DOKTER "
    # q +=" AND PKU.PSD_KD_POLI=KUNJ.KPKD_POLY "
    # q +=" AND PKU.PSD_KD_DOKTER=KUNJ.KPKD_DOKTER"
    # q +=" AND PKU.PSD_NO_TRANSAKSI_RS=KUNJ.KPNO_TRANSAKSI)"
    # q +=" AND PL.FMPKLINIK_ID NOT IN('PK019','PK018')"
    # q +=" AND KUNJ.KPNO_TRANSAKSI  IN (SELECT SI.SS_NO_TRANS_RS  FROM SATUSEHAT_ICD10 SI)"
    # q +=" AND KUNJ.KPNO_TRANSAKSI  NOT IN ('KRJ001221011-002','KRJ023221011-001')"
    # print(q)
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    # print(q)
    counter = 0
    for isianPoli in result:
        if counter == 0:
            greeting("Laporan ADD KUNJUNGAN FHIR...")

        # print(isianPoli["KD_PASIEN_FHIR"])
        KD_PASIEN_FHIR = isianPoli["KD_PASIEN_FHIR"]
        if KD_PASIEN_FHIR == "-":
            dataPasien = json.loads(savePatient(request, isianPoli["KDASIENRS"]))
            # print(dataPasien['KD_PASIEN_FHIR'])
            KD_PASIEN_FHIR = dataPasien["KD_PASIEN_FHIR"]
            greeting("PASIEN BARU " + KD_PASIEN_FHIR)
        else:
            greeting("PASIEN LAMA " + KD_PASIEN_FHIR)

        PSD_NO_TRANSAKSI_FHIR = isianPoli["PSD_NO_TRANSAKSI_FHIR"]
        url = getattr(
            env, "SATU_SEHAT_URL_DATA", "BELUM_ADA_LINK"
        ) + "/Encounter/{}".format(PSD_NO_TRANSAKSI_FHIR)

        listDiagnosis = []

        cursorICD = connection.cursor()
        qCariICD10Lain = " SELECT A.*,B.PENYAKIT FROM SATUSEHAT_ICD10 A  "
        qCariICD10Lain += " LEFT JOIN PENYAKIT B ON A.SS_ICD10=B.KD_PENYAKIT"
        qCariICD10Lain += " LEFT JOIN MR_PENYAKIT MPNY ON A.SS_ICD10=MPNY.MRPKD_PASIEN"
        qCariICD10Lain += " WHERE A.SS_NO_TRANS_RS='{}'".format(isianPoli["NOTRANS"])
        qCariICD10Lain += " ORDER BY MPNY.MRPSTAT_DIAG DESC"
        cursorICD.execute(qCariICD10Lain)
        dcariICD10 = Globals().dictfetchall(cursorICD)
        listIcd10 = []
        isianNO = 1
        for isianICD10 in dcariICD10:
            listDiagnosis.append(
                {
                    "condition": {
                        "reference": "Condition/{}".format(isianICD10["SS_FHIR_ID"]),
                        "display": "{}".format(isianICD10["PENYAKIT"]),
                    },
                    "use": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                                "code": "DD",
                                "display": "Discharge diagnosis",
                            }
                        ]
                    },
                    "rank": isianNO,
                }
            )
            isianNO = isianNO + 1

        payload = {
            "resourceType": "Encounter",
            "id": "{}".format(PSD_NO_TRANSAKSI_FHIR),
            "identifier": [
                {
                    "system": "http://sys-ids.kemkes.go.id/encounter/{}".format(
                        resultCabang[0]["SS_FHIR_KD_CABANG"]
                    ),
                    "value": "{}".format(isianPoli["NOTRANS"]),
                }
            ],
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {
                "reference": "Patient/{}".format(KD_PASIEN_FHIR),
                "display": "{}".format(isianPoli["NAMAPASIEN"]),
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
                            isianPoli["KD_KDDOKTER_FHIR"]
                        ),
                        "display": "{}".format(isianPoli["NAMADOKTER"]),
                    },
                }
            ],
            "period": {
                "start": "{}".format(isianPoli["TGLJAM_START"]),
                "end": "{}".format(isianPoli["TGLJAM_END"]),
            },
            "location": [
                {
                    "location": {
                        "display": "{}".format(isianPoli["POLIN"]),
                        "reference": "Location/{}".format(isianPoli["KDPOLI_FHIR"]),
                    }
                }
            ],
            "diagnosis": listDiagnosis,
            "statusHistory": [
                {
                    "period": {
                        "start": "{}".format(isianPoli["TGLJAM_START"]),
                        "end": "{}".format(isianPoli["TGLJAM_START"]),
                    },
                    "status": "arrived",
                },
                {
                    "period": {
                        "start": "{}".format(isianPoli["TGLJAM_START"]),
                        "end": "{}".format(isianPoli["TGLJAM_PROGRESS"]),
                    },
                    "status": "in-progress",
                },
                {
                    "period": {
                        "start": "{}".format(isianPoli["TGLJAM_PROGRESS"]),
                        "end": "{}".format(isianPoli["TGLJAM_END"]),
                    },
                    "status": "finished",
                },
            ],
            "serviceProvider": {
                "reference": "Organization/{}".format(
                    resultCabang[0]["SS_FHIR_KD_CABANG"]
                )
            },
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED PUT ENCOUNTER",
            "Authorization": "Bearer " + getToken(request),
        }
        print(headers)
        print(payload)
        try:
            json_data = requests.put(url, headers=headers, data=json.dumps(payload))
            dataBridging = json.loads(json_data.text)
            print("===response saveencounter")
            print(dataBridging)
            print("===response saveencounter")
            greeting(
                "Berhasil Bridging {}\n {} ({}) \n {} {}".format(
                    isianPoli["TGLRS"],
                    isianPoli["NOTRANS"],
                    PSD_NO_TRANSAKSI_FHIR,
                    isianPoli["NAMAPASIEN"],
                    isianPoli["POLIN"],
                )
            )
        except:
            print("===response error")
            print("===response saveencounter")
            print(dataBridging)
            print("===response saveencounter")
            greeting(
                " GAGAL  BRIDING{}\n {} \n {} {}".format(
                    isianPoli["TGLRS"],
                    isianPoli["NOTRANS"],
                    isianPoli["NAMAPASIEN"],
                    isianPoli["POLIN"],
                )
            )

        # print("===response saveencounter")
        # print(dataBridging)
        # print("===response saveencounter")
        try:
            greeting(
                "Berhasil UPDATE Bridging DB {} ({})".format(
                    isianPoli["NOTRANS"], PSD_NO_TRANSAKSI_FHIR
                )
            )
            qInsertPoli = (
                "UPDATE SATUSEHAT_ICD10 SET SATUSEHAT_ICD10.SS_PUT_ENCOUNTER=GETDATE() "
            )
            qInsertPoli += "WHERE SATUSEHAT_ICD10.SS_NO_TRANS='{}'".format(
                PSD_NO_TRANSAKSI_FHIR
            )
            cursor.execute(qInsertPoli)

        except:
            greeting(
                "GAGAL INSERT KARENA GAGAL BRIDGING {}\n {} \n {} {}".format(
                    isianPoli["TGLRS"],
                    isianPoli["NOTRANS"],
                    isianPoli["NAMAPASIEN"],
                    isianPoli["POLIN"],
                )
            )
            print("===response dokter")
            print(dataBridging)
            print("===response dokter")
        counter += 1

    return HttpResponse({"success": True}, content_type="application/json")


def saveLocationPoli(request):
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    q = "select a.CABANG_ID,a.PERUSAHAAN,a.ALAMAT1,KOTA_ID,KOTA,KODE_POS,TELEPON,no_whatsapp,email,website,KONTAK,JABATAN,NPWP,TGLPENGUKUHAN,USING,a.ppkpelayanan,consid,secret,bpjs_userkey,userncc,passwordncc,ijinSIP,user_icare,password_icare,statusmjkn,client_id,organization_id,Secret_key,SS_FHIR_KD_CABANG,   "
    q += "b.KD_KELURAHAN,b.KELURAHAN,c.KD_KECAMATAN,c.KECAMATAN,isnull(d.KD_KABUPATEN,a.KOTA_ID) as KD_KABUPATEN,isnull(d.KABUPATEN,KOTA) as KABUPATEN,e.KD_PROPINSI,e.PROPINSIN,SS_FHIR_longitude,SS_FHIR_latitude from CABANG a "
    q += "left join KELURAHAN b on a.KOTA_ID=b.KD_KELURAHAN  "
    q += "left join KECAMATAN c on b.KD_KECAMATAN=c.KD_KECAMATAN "
    q += "left join KABUPATEN d on c.KD_KABUPATEN=d.KD_KABUPATEN "
    q += "left join PROPINSI e on d.KD_PROPINSI=e.KD_PROPINSI "
    q += "WHERE CABANG_ID= %s "
    resultCabang = Globals().getDataQuery(q, [kdCabang])

    q = " select a.FMPKLINIK_ID,a.FMPKLINIKN,a.FMPKODEBPJS,b.SSFHIR_KLINIK_ID,b.SSFHIR_KD_POLI from POLIKLINIK a "
    q += " left join POLIKLINIK_SATU_SEHAT b on a.FMPKLINIK_ID=b.SSFHIR_KLINIK_ID and b.SSFHIR_CABANG_ID=%s "
    q += " WHERE b.SSFHIR_KD_POLI  IS NULL order by FMPKLINIK_ID "
    result = Globals().getDataQuery(q, [kdCabang])

    for isianPoli in result:
        namaPoli = isianPoli["FMPKLINIKN"]
        kdPoli = isianPoli["FMPKLINIK_ID"]
        url = getattr(env, "SATU_SEHAT_URL_DATA", "BELUM_INPUT_URL") + "/Location"
        payload = {
            "resourceType": "Location",
            "identifier": [
                {
                    "system": "http://sys-ids.kemkes.go.id/location/{}".format(
                    resultCabang[0]["organization_id"]
                ),
                    "value": "{}".format(kdPoli),
                }
            ],
            "status": "active",
            "name": "{}".format(namaPoli),
            "description": "Ruang {}".format(namaPoli),
            "mode": "instance",
            "telecom": [
                {
                    "system": "phone",
                    "value": "{}".format(resultCabang[0]["TELEPON"]),
                    "use": "work",
                },
                {
                    "system": "fax",
                    "value": "{}".format(resultCabang[0]["TELEPON"]),
                    "use": "work",
                },
                {
                    "system": "email",
                    "value": "{}".format(resultCabang[0]["email"]),
                    "use": "work",
                },
                {
                    "system": "url",
                    "value": "{}".format(resultCabang[0]["website"]),
                    "use": "work",
                },
            ],
            "address": {
                "use": "work",
                "line": [
                    "{}".format(resultCabang[0]["ALAMAT1"]),
                ],
                "city": "{}".format(resultCabang[0]["KABUPATEN"]),
                "postalCode": "{}".format(resultCabang[0]["KODE_POS"]),
                "country": "ID",
                "extension": [
                    {
                        "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/administrativeCode",
                        "extension": [
                            {
                                "url": "province",
                                "valueCode": "{}".format(
                                    resultCabang[0]["KD_PROPINSI"]
                                ),
                            },
                            {
                                "url": "city",
                                "valueCode": "{}".format(
                                    resultCabang[0]["KD_KABUPATEN"]
                                ),
                            },
                            {
                                "url": "district",
                                "valueCode": "{}".format(
                                    resultCabang[0]["KD_KECAMATAN"]
                                ),
                            },
                            {
                                "url": "village",
                                "valueCode": "{}".format(
                                    resultCabang[0]["KD_KELURAHAN"]
                                ),
                            },
                            {"url": "rt", "valueCode": "1"},
                            {"url": "rw", "valueCode": "2"},
                        ],
                    }
                ],
            },
            "physicalType": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
                        "code": "ro",
                        "display": "Room",
                    }
                ]
            },
            "position": {
                "longitude": float(
                    (resultCabang[0]["SS_FHIR_longitude"]).replace(",", ".")
                ),
                "latitude": float(
                    (resultCabang[0]["SS_FHIR_latitude"]).replace(",", ".")
                ),
                "altitude": 0,
            },
            "managingOrganization": {
                "reference": "Organization/{}".format(
                    resultCabang[0]["organization_id"]
                )
            },
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE LOC",
            "Authorization": "Bearer " + getToken(request),
        }
        # print(headers)
        # print(payload)
        json_data = requests.post(url, headers=headers, data=json.dumps(payload))
        dataBridging = json.loads(json_data.text)
        # print("===response")
        # print(dataBridging)
        # print("===response")
        # print(kdPoli)
        try:
            q = "SELECT * FROM POLIKLINIK_SATU_SEHAT WHERE SSFHIR_KLINIK_ID='{}' and SSFHIR_CABANG_ID='{}' ".format(
                kdPoli, kdCabang
            )
            result = Globals().getDataQuery(q)
            if len(result) > 0:
                qInsertPoli = "UPDATE POLIKLINIK_SATU_SEHAT SET SSFHIR_KD_POLI='{}' WHERE FMPKLINIK_ID='{}' and SSFHIR_CABANG_ID='{}' ".format(
                    dataBridging["id"], kdPoli, kdCabang
                )
                Globals().executeQuery(qInsertPoli)
            else:
                qInsertPoli = "INSERT INTO POLIKLINIK_SATU_SEHAT (SSFHIR_KD_POLI,SSFHIR_KLINIK_ID,SSFHIR_CABANG_ID) VALUES (%s,%s,%s)"
                Globals().executeQuery(
                    qInsertPoli, [dataBridging["id"], kdPoli, kdCabang]
                )

        except:
            print("===response_rr")
            print(dataBridging)
            print("===response_rr")

    res = {
        "success": True,
        "message": "Sukses Bridging",
    }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def SrvIndoSaveLocationPoli(request):
    kdCabang = request.session["kdCabang"]
    url = getattr(
        env,
        "SERVER_INDO",
        "",
    ) + "/views_satu_sehat/saveLocationPoli?kdCabang={}".format(kdCabang)
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


def getLocationPoli(request):
    # Organization=json.loads(getOrganization(request))
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    q = "select a.CABANG_ID,a.PERUSAHAAN,a.ALAMAT1,KOTA_ID,KOTA,KODE_POS,TELEPON,no_whatsapp,email,website,KONTAK,JABATAN,NPWP,TGLPENGUKUHAN,USING,a.ppkpelayanan,consid,secret,bpjs_userkey,userncc,passwordncc,ijinSIP,user_icare,password_icare,statusmjkn,client_id,organization_id,Secret_key,SS_FHIR_KD_CABANG,   "
    q += "b.KD_KELURAHAN,b.KELURAHAN,c.KD_KECAMATAN,c.KECAMATAN,isnull(d.KD_KABUPATEN,a.KOTA_ID) as KD_KABUPATEN,isnull(d.KABUPATEN,KOTA) as KABUPATEN,e.KD_PROPINSI,e.PROPINSIN,SS_FHIR_longitude,SS_FHIR_latitude from CABANG a "
    q += "left join KELURAHAN b on a.KOTA_ID=b.KD_KELURAHAN  "
    q += "left join KECAMATAN c on b.KD_KECAMATAN=c.KD_KECAMATAN "
    q += "left join KABUPATEN d on c.KD_KABUPATEN=d.KD_KABUPATEN "
    q += "left join PROPINSI e on d.KD_PROPINSI=e.KD_PROPINSI "
    q += "WHERE CABANG_ID= %s "
    resultCabang = Globals().getDataQuery(q, [kdCabang])

    q = " select a.FMPKLINIK_ID,a.FMPKLINIKN,a.FMPKODEBPJS,b.SSFHIR_KLINIK_ID,b.SSFHIR_KD_POLI from POLIKLINIK a "
    q += " left join POLIKLINIK_SATU_SEHAT b on a.FMPKLINIK_ID=b.SSFHIR_KLINIK_ID and b.SSFHIR_CABANG_ID=%s "
    q += " WHERE b.SSFHIR_KD_POLI  IS NULL order by FMPKLINIK_ID "
    result = Globals().getDataQuery(q, [kdCabang])

    for isianPoli in result:
        namaPoli = isianPoli["FMPKLINIKN"]
        kdPoli = isianPoli["FMPKLINIK_ID"]
        url = getattr(
            env, "SATU_SEHAT_URL_DATA", "BELUM_INPUT_URL"
        ) + "/Location?organization={}".format(resultCabang[0]["organization_id"])
        payload = {}
        # print(url)
        # print(payload)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE LOC",
            "Authorization": "Bearer " + getToken(request),
        }
        json_data = requests.get(url, data=payload, headers=headers)
        dataBridging = json.loads(json_data.text)
        print("===response1")
        print(dataBridging)
        print("===response")
        print(kdPoli)
        try:
            for isianPolis in dataBridging["entry"]:
                print(isianPolis["resource"]["name"])
                print(namaPoli)
                if isianPolis["resource"]["name"] == namaPoli:
                    q = "SELECT * FROM POLIKLINIK_SATU_SEHAT WHERE SSFHIR_KLINIK_ID='{}' and SSFHIR_CABANG_ID='{}' ".format(
                        kdPoli, kdCabang
                    )
                result = Globals().getDataQuery(q)
                if len(result) > 0:
                    qInsertPoli = "UPDATE POLIKLINIK_SATU_SEHAT SET SSFHIR_KD_POLI='{}' WHERE FMPKLINIK_ID='{}' and SSFHIR_CABANG_ID='{}' ".format(
                        dataBridging["id"], kdPoli, kdCabang
                    )
                    Globals().executeQuery(qInsertPoli)
                else:
                    qInsertPoli = "INSERT INTO POLIKLINIK_SATU_SEHAT (SSFHIR_KD_POLI,SSFHIR_KLINIK_ID,SSFHIR_CABANG_ID) VALUES (%s,%s,%s)"
                    Globals().executeQuery(
                        qInsertPoli, [dataBridging["id"], kdPoli, kdCabang]
                    )
        except:
            print("===response_rr")
            print(dataBridging)
            print("===response_rr")

    res = {
        "success": True,
        "message": "Sukses Bridging",
    }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getLocationorganization(request):
    # Organization=json.loads(getOrganization(request))
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    q = "select a.CABANG_ID,a.PERUSAHAAN,a.ALAMAT1,KOTA_ID,KOTA,KODE_POS,TELEPON,no_whatsapp,email,website,KONTAK,JABATAN,NPWP,TGLPENGUKUHAN,USING,a.ppkpelayanan,consid,secret,bpjs_userkey,userncc,passwordncc,ijinSIP,user_icare,password_icare,statusmjkn,client_id,organization_id,Secret_key,SS_FHIR_KD_CABANG,   "
    q += "b.KD_KELURAHAN,b.KELURAHAN,c.KD_KECAMATAN,c.KECAMATAN,isnull(d.KD_KABUPATEN,a.KOTA_ID) as KD_KABUPATEN,isnull(d.KABUPATEN,KOTA) as KABUPATEN,e.KD_PROPINSI,e.PROPINSIN,SS_FHIR_longitude,SS_FHIR_latitude from CABANG a "
    q += "left join KELURAHAN b on a.KOTA_ID=b.KD_KELURAHAN  "
    q += "left join KECAMATAN c on b.KD_KECAMATAN=c.KD_KECAMATAN "
    q += "left join KABUPATEN d on c.KD_KABUPATEN=d.KD_KABUPATEN "
    q += "left join PROPINSI e on d.KD_PROPINSI=e.KD_PROPINSI "
    q += "WHERE CABANG_ID= %s "
    resultCabang = Globals().getDataQuery(q, [kdCabang])
    url = getattr(
        env, "SATU_SEHAT_URL_DATA", "BELUM_INPUT_URL"
    ) + "/Location?organization={}".format(resultCabang[0]["SS_FHIR_KD_CABANG"])
    payload = {}
    # print(headers)
    # print(payload)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SIMKLINIK MEDISIMED SAVE LOC",
        "Authorization": "Bearer " + getToken(request),
    }
    json_data = requests.get(url, data=payload, headers=headers)
    dataBridging = json.loads(json_data.text)

    for isianPoli in dataBridging["entry"]:
        id_Poli = isianPoli["resource"]["id"]
        for i in isianPoli["resource"]["identifier"]:
            kdPoli = i["value"]
            try:
                q = "SELECT * FROM POLIKLINIK_SATU_SEHAT WHERE SSFHIR_KLINIK_ID='{}' and SSFHIR_CABANG_ID='{}' ".format(
                    kdPoli, kdCabang
                )
                result = Globals().getDataQuery(q)
                if len(result) > 0:
                    qInsertPoli = "UPDATE POLIKLINIK_SATU_SEHAT SET SSFHIR_KD_POLI='{}' WHERE SSFHIR_KLINIK_ID='{}' and SSFHIR_CABANG_ID='{}' ".format(
                        id_Poli, kdPoli, kdCabang
                    )
                    Globals().executeQuery(qInsertPoli)
                else:
                    qInsertPoli = "INSERT INTO POLIKLINIK_SATU_SEHAT (SSFHIR_KD_POLI,SSFHIR_KLINIK_ID,SSFHIR_CABANG_ID) VALUES (%s,%s,%s)"
                    Globals().executeQuery(qInsertPoli, [id_Poli, kdPoli, kdCabang])
            except:
                print("===response_rr")
                # print(dataBridging)
                print("===response_rr")

    res = {
        "success": True,
        "message": "Sukses Bridging",
    }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def savePractitionerDokter(request):
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    q = "SELECT * FROM DOKTER WHERE FMDSTATUS='0' AND DOKTER.SSFHIR_KD_DOKTER IS NULL AND len(DOKTER.FMDNIP)=16 and DOKTER.KD_CABANG= %s"
    result = Globals().getDataQuery(q, [kdCabang])
    kdDokterSS = ""

    for isianDokter in result:
        namaDokter = isianDokter["FMDDOKTERN"]
        kdDokter = isianDokter["FMDDOKTER_ID"]
        FMDOKTER_NIK = isianDokter["FMDNIP"]
        url = getattr(
            env, "SATU_SEHAT_URL_DATA", "BELUM_ADA"
        ) + "/Practitioner?identifier=https://fhir.kemkes.go.id/id/nik|{}".format(
            FMDOKTER_NIK
        )
        payload = {}

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE DOKTER",
            "Authorization": "Bearer " + getToken(request),
        }
        # print(url)
        # print(headers)
        # print(payload)
        json_data = requests.get(url, headers=headers)
        # print("===response dokter")
        # print(json_data)
        dataBridging = json.loads(json_data.text)
        # print("===response dokter")
        # print(dataBridging)
        # print(dataBridging["entry"][0]["resource"]["id"])
        # print("===response dokter")
        # print(FMDOKTER_NIK)
        try:
            if len(dataBridging["entry"]) > 0:
                kdDokterSS = dataBridging["entry"][0]["resource"]["id"]
                cursor = connection.cursor()
                qInsertPoli = "UPDATE DOKTER SET SSFHIR_KD_DOKTER='{}' where FMDDOKTER_ID='{}' AND SSFHIR_KD_DOKTER IS NULL and DOKTER.KD_CABANG='{}' ".format(
                    kdDokterSS, kdDokter, kdCabang
                )
                cursor.execute(qInsertPoli)
                cursor.close()
        except:
            print("===GAGAL")
            print(dataBridging)
            print("===response dokter")

    res = {
        "success": True,
        "message": "Sukses Bridging",
        "id": kdDokterSS,
    }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def savePractitionerDokter_SrvIndo(request):
    kdCabang = request.session["kdCabang"]
    url = getattr(
        env,
        "SERVER_INDO",
        "",
    ) + "views_satu_sehat/savePractitionerDokter?kdCabang={}".format(kdCabang)
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    # print('url')
    print(url)
    # print(headers)
    payload = {}
    json_data = {}
    json_data = requests.get(url)
    return HttpResponse(json_data, content_type="application/json")


def getPractitionerDokter(request):
    # Organization=getOrganization(request)
    # Organization=json.loads(getOrganization(request))
    # print(Organization)
    cursor = connection.cursor()
    q = "SELECT * FROM DOKTER WHERE FMDSTATUS='0' AND DOKTER.SSFHIR_KD_DOKTER IS NULL AND DOKTER.FMDNIP IS NOT NULL"
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)

    for isianDokter in result:
        namaDokter = isianDokter["FMDDOKTERN"]
        kdDokter = isianDokter["FMDDOKTER_ID"]
        FMDOKTER_NIK = isianDokter["FMDNIP"]
        # namaDokter="ANNI NURHADIYATI DRG"
        # kdDokter="IF002"
        url = getattr(
            env, "SATU_SEHAT_URL_DATA", "BELUM_ADA"
        ) + "/Practitioner?identifier=https://fhir.kemkes.go.id/id/nik|{}".format(
            FMDOKTER_NIK
        )
        payload = {}

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SIMKLINIK MEDISIMED SAVE DOKTER",
            "Authorization": "Bearer " + getToken(request),
        }
        # print(url)
        # print(headers)
        # print(payload)
        json_data = requests.get(url, headers=headers)
        # print("===response dokter")
        # print(json_data)
        dataBridging = json.loads(json_data.text)
        # print("===response dokter")
        # print(dataBridging)
        # print("===response dokter")
        # print(FMDOKTER_NIK)
        try:
            if len(dataBridging["entry"]) > 0:
                kdDokterSS = dataBridging["entry"][0]["resource"]["id"]
                cursor = connection.cursor()
                qInsertPoli = "UPDATE DOKTER SET SSFHIR_KD_DOKTER='{}' where FMDDOKTER_ID='{}' AND SSFHIR_KD_DOKTER IS NULL".format(
                    kdDokterSS, kdDokter
                )
                cursor.execute(qInsertPoli)
                cursor.close()
        except:
            print("===gagal")
            # print(dataBridging)
            # print("===response dokter")

    res = {
        "success": True,
        "message": "Sukses Bridging",
    }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def greeting(proses="Laporan ADD KUNJUNGAN..."):
    print(proses)
    # url = 'https://api.telegram.org/'
    # tokens_telegram = getattr(env, 'BOT_TOKEN_TELEGRAM_PUSDOKKES', [])
    # ids_telegram = getattr(env, 'BOT_USER_ID_TELEGRAM_PUSDOKKES', [])

    # for telegram in tokens_telegram:
    #     for user in ids_telegram:
    #         requests.get(url + 'bot' + telegram + '/sendMessage?chat_id=' + user + '&parse_mode=MarkdownV2&text=```\n' + proses + '\n```')


##--- Kondisi untuk pengiriman ICD10
def saveConditionICD10(request):
    cursor = connection.cursor()
    q = " SELECT PKN.PSD_NO_TRANSAKSI_RS,PKN.PSD_NO_TRANSAKSI_FHIR "
    q += " ,PASIEN.NAMAPASIEN,PP.PKD_PASIEN_FHIR,MRP.MRPKD_PENYAKIT,PNY.PENYAKIT"
    q += " ,KP.KPTGL_PERIKSA as TGLRS,dbo.tanggalIndo(KP.KPTGL_PERIKSA) as TGLINDO"
    q += " FROM SATUSEHAT_KUNJUNGAN PKN"
    q += " LEFT JOIN KUNJUNGANPASIEN KP ON KP.KPNO_TRANSAKSI=PKN.PSD_NO_TRANSAKSI_RS"
    q += " LEFT JOIN PASIEN ON KP.KPKD_PASIEN=PASIEN.KD_PASIEN"
    q += " INNER JOIN SATUSEHAT_PASIEN PP ON KP.KPKD_PASIEN=PP.PKD_PASIEN"
    q += " INNER JOIN MR_PENYAKIT MRP ON PKN.PSD_NO_TRANSAKSI_RS=MRP.MRPNO_TRANSAKSI"
    q += " INNER JOIN PENYAKIT PNY ON PNY.KD_PENYAKIT=MRP.MRPKD_PENYAKIT"
    q += " WHERE "
    if "KPNO_TRANSAKSI" in request.GET:
        q += " KP.KPNO_TRANSAKSI='{}'".format(request.GET["KPNO_TRANSAKSI"])
    else:
        if "TGLPERIKSA" in request.GET:
            q += "  CONVERT(date,PKN.PSD_TGL)='{}'".format(request.GET["TGLPERIKSA"])
        else:
            q += " CONVERT(date,PKN.PSD_TGL)=CONVERT(date,GETDATE())  "
    # q +=" AND MRP.MRPSTAT_DIAG='5' "
    # q +=" AND PKN.PSDCREATED_AT_CONDITION IS NULL "
    q += " AND PKN.PSD_NO_TRANSAKSI_FHIR NOT IN(SELECT SS_NO_TRANS FROM SATUSEHAT_ICD10)  "
    q += " ORDER BY MRP.MRPSTAT_DIAG DESC "
    # q +=" GROUP BY PKN.PSD_NO_TRANSAKSI_RS "
    # q +=",PASIEN.NAMAPASIEN,PP.PKD_PASIEN_FHIR"
    # q +=",MRP.MRPKD_PENYAKIT,PNY.PENYAKIT,KP.KPTGL_PERIKSA"
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    # print(q)
    counter = 0
    for isianPoli in result:
        if counter == 0:
            greeting("Laporan ADD CONDITION FHIR...")

        # print(isianPoli["KD_PASIEN_FHIR"])
        KD_PASIEN_FHIR = isianPoli["PKD_PASIEN_FHIR"]
        # if KD_PASIEN_FHIR=="-":
        #     dataPasien=json.loads(savePatient(request,isianPoli["KDASIENRS"]))
        #     # print(dataPasien['KD_PASIEN_FHIR'])
        #     KD_PASIEN_FHIR=dataPasien['KD_PASIEN_FHIR']
        #     greeting("PASIEN BARU "+KD_PASIEN_FHIR)
        # else:
        #     greeting("PASIEN LAMA "+KD_PASIEN_FHIR)
        # return 0
        # namaDokter="ANNI NURHADIYATI DRG"
        # kdDokter="IF002"
        # cursorICD = connection.cursor()
        # qCariICD10Lain=" SELECT A.MRPKD_PENYAKIT,B.PENYAKIT,A.MRPSTAT_DIAG FROM MR_PENYAKIT A "
        # qCariICD10Lain+=" LEFT JOIN PENYAKIT B ON A.MRPKD_PENYAKIT=B.KD_PENYAKIT"
        # qCariICD10Lain+=" where A.MRPNO_TRANSAKSI='{}'".format(isianPoli["PSD_NO_TRANSAKSI_RS"])
        # qCariICD10Lain+=" AND A.MRPSTAT_DIAG='5'"
        # qCariICD10Lain+=" ORDER BY A.MRPSTAT_DIAG DESC"
        # cursorICD.execute(qCariICD10Lain)
        # dcariICD10 = Globals().dictfetchall(cursorICD)
        # listIcd10 = []
        # for isianICD10 in dcariICD10:
        #     listIcd10.append({
        #         "system": "http://hl7.org/fhir/sid/icd-10",
        #         "code": "{}".format(isianICD10["MRPKD_PENYAKIT"]),
        #         "display": "{}".format(isianICD10["PENYAKIT"])
        #     })
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
        # print(headers)
        # print(payload)
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(payload))
            dataBridging = json.loads(json_data.text)
            greeting(
                "Berhasil Bridging CONDITION {}\n {} ({}) \n {}".format(
                    isianPoli["TGLRS"],
                    isianPoli["PSD_NO_TRANSAKSI_RS"],
                    dataBridging["id"],
                    isianPoli["NAMAPASIEN"],
                )
            )
        except:
            greeting(
                "Berhasil Bridging CONDITION {}\n {} \n {}".format(
                    isianPoli["TGLRS"],
                    isianPoli["PSD_NO_TRANSAKSI_RS"],
                    isianPoli["NAMAPASIEN"],
                )
            )

        # print(kdPoli)
        try:
            # print("===berhasil response condition")
            # print(dataBridging)
            # print("===response condition")
            greeting(
                "Berhasil Save CONDITION {} {} ({})".format(
                    isianPoli["PSD_NO_TRANSAKSI_RS"],
                    isianPoli["MRPKD_PENYAKIT"],
                    dataBridging["id"],
                )
            )
            cursor = connection.cursor()
            # qInsertPoli=" DELETE FROM SATUSEHAT_ICD10 WHERE PSD_ICD10='{}',PSD_ICD10_FHIR='{}' ".format(isianPoli["MRPKD_PENYAKIT"],dataBridging["id"])
            # cursor.execute(qInsertPoli)
            qInsertPoli = " INSERT INTO SATUSEHAT_ICD10(SS_NO_TRANS_RS,SS_NO_TRANS, SS_ICD10, SS_FHIR_ID, PCREATED_AT) "
            qInsertPoli += " VALUES('{}','{}','{}','{}',GETDATE()) ".format(
                isianPoli["PSD_NO_TRANSAKSI_RS"],
                isianPoli["PSD_NO_TRANSAKSI_FHIR"],
                isianPoli["MRPKD_PENYAKIT"],
                dataBridging["id"],
            )
            # print(qInsertPoli)
            cursor.execute(qInsertPoli)
        except:
            greeting(
                "GAGAL Save Bridging CONDITION {} {} ({})".format(
                    isianPoli["PSD_NO_TRANSAKSI_RS"],
                    isianPoli["MRPKD_PENYAKIT"],
                    isianPoli["NAMAPASIEN"],
                )
            )
            # print("===gagal Save response condition")
            # print(dataBridging)
            # print("===response condition")
        counter += 1

    # return HttpResponse({'success':True}, content_type="application/json")
    res = {
        "success": True,
        "message": "Sukses Bridging",
    }

    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getCondition(request):
    payload = {}
    id = request.GET["id"]
    url = getattr(
        env,
        "SATU_SEHAT_URL_DATA",
        "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
    ) + "/Condition/{}".format(id)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    json_datas = requests.get(url, data=payload, headers=headers)
    return HttpResponse(json_datas, content_type="application/json")


def getConditions(request, id):
    payload = {}
    # id=request.GET['id']
    url = getattr(
        env,
        "SATU_SEHAT_URL_DATA",
        "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
    ) + "/Condition/{}".format(id)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    json_datas = requests.get(url, data=payload, headers=headers)
    return json.loads(json_datas.text)
    # return HttpResponse(json_datas, content_type="application/json")


def getOrganization(request, id):
    payload = {}
    # id=request.GET['id']
    url = getattr(
        env,
        "SATU_SEHAT_URL_DATA",
        "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
    ) + "/Organization/{}".format(id)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    json_datas = requests.get(url, data=payload, headers=headers)
    return json.loads(json_datas.text)
    # return HttpResponse(json_datas, content_type="application/json")


def getLokasi(request, id):
    payload = {}
    # id=request.GET['id']
    url = getattr(
        env,
        "SATU_SEHAT_URL_DATA",
        "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
    ) + "/Location/{}".format(id)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    json_datas = requests.get(url, data=payload, headers=headers)
    return json.loads(json_datas.text)
    # return HttpResponse(json_datas, content_type="application/json")


def getHistoryPasien(request):
    # print('url')
    json_data = []
    payload = {}
    norm = request.GET["norm"]
    cursor = connection.cursor()
    q = "SELECT * FROM SATUSEHAT_PASIEN A WHERE A.PKD_PASIEN='{}'".format(norm)
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    NORM_SATUSEHAT = result[0]["PKD_PASIEN_FHIR"]
    # print(NORM_SATUSEHAT)
    if int(len(result)) > 0:
        url = getattr(
            env,
            "SATU_SEHAT_URL_DATA",
            "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1",
        ) + "/Encounter?subject={}".format(NORM_SATUSEHAT)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(getToken(request)),
            "User-Agent": "SIMKLINIK MEDISIMED",
        }
        json_datas = requests.get(url, data=payload, headers=headers)
        # print(json_datas)
        dataHistory = json.loads(json_datas.text)["entry"]
        # dataHistory=json_datas
        json_data = []
        for isianHistory in dataHistory:
            id_rumah_sakit = isianHistory["resource"]["serviceProvider"][
                "reference"
            ].split("/")[1]
            nama_rs = getOrganizationInternet(request, id_rumah_sakit)["name"]
            print(id_rumah_sakit)
            diagnosis = ""
            listDiagnosis = []
            for isianDiagnosa in isianHistory["resource"]["diagnosis"]:
                # print(isianDiagnosa)
                idDiagnosis = (isianDiagnosa["condition"]["reference"]).split("/")[1]
                diagnosis += " {} {} ;".format(
                    getConditions(request, idDiagnosis)["code"]["coding"][0]["code"],
                    getConditions(request, idDiagnosis)["code"]["coding"][0]["display"],
                )
                # print(getConditions(request,idDiagnosis)['code']['coding'][0]['code'])
                listDiagnosis.append(
                    {
                        "idDiagnosis": idDiagnosis,
                        "kdDiagnosa": getConditions(request, idDiagnosis)["code"][
                            "coding"
                        ][0]["code"],
                        "diagnosa": getConditions(request, idDiagnosis)["code"][
                            "coding"
                        ][0]["display"],
                    }
                )

            json_data.append(
                {
                    "idKunjunganSS_RS": isianHistory["resource"]["identifier"][0][
                        "value"
                    ],
                    "idKunjunganSS": isianHistory["resource"]["id"],
                    "poli": isianHistory["resource"]["location"][0]["location"][
                        "display"
                    ],
                    "dokter": isianHistory["resource"]["participant"][0]["individual"][
                        "display"
                    ],
                    "tglKunjungan": isianHistory["resource"]["period"]["start"],
                    # 'diagnosis':diagnosis,
                    "diagnosis": listDiagnosis,
                    "nama_rs": nama_rs,
                    "id_rumah_sakit": id_rumah_sakit,
                }
            )

        # print(json_data.text)
        # json_data=dataHistory
    # print(json_data)
    json_data_list = []
    json_data_list.append(json_data)
    json_data = json.dumps(json_data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


# KYC
def format_message(data):
    data_as_base64 = base64.b64encode(data).decode('utf-8')
    formatted_message = f"-----BEGIN ENCRYPTED MESSAGE-----\r\n{data_as_base64}-----END ENCRYPTED MESSAGE-----"
    return formatted_message
def generate_key():
	private_key = rsa.generate_private_key(
		public_exponent=65537,
		key_size=2048,
		backend=default_backend()
	)
	public_key = private_key.public_key().public_bytes(
		encoding=serialization.Encoding.PEM,
		format=serialization.PublicFormat.SubjectPublicKeyInfo
	).decode('utf-8')
	private_key_pem = private_key.private_bytes(
		encoding=serialization.Encoding.PEM,
		format=serialization.PrivateFormat.TraditionalOpenSSL,
		encryption_algorithm=serialization.NoEncryption()
	).decode('utf-8')

	return {
		'publicKey': public_key,
		'privateKey': private_key_pem
	}

def import_rsa_key(pem):
	pem_header = '-----BEGIN PUBLIC KEY-----'
	pem_footer = '-----END PUBLIC KEY-----'
	pem_contents = pem.replace(pem_header, '').replace(pem_footer, '').strip()
	binary_der_string = b64decode(pem_contents)
	return serialization.load_der_public_key(binary_der_string, backend=default_backend())

def generate_symmetric_key():
	return os.urandom(32)

def aes_encrypt(data, symmetric_key):
	iv = os.urandom(12)
	cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(iv), backend=default_backend())
	encryptor = cipher.encryptor()
	ciphertext = encryptor.update(data) + encryptor.finalize()
	tag = encryptor.tag
	return iv + ciphertext + tag

def aes_decrypt(encrypted_data, symmetric_key):
	iv = encrypted_data[:12]
	tag = encrypted_data[-16:]
	ciphertext = encrypted_data[12:-16]
	cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(iv, tag), backend=default_backend())
	decryptor = cipher.decryptor()
	return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_message(message, pub_pem):
    from cryptography.hazmat.primitives.asymmetric import padding
    aes_key = generate_symmetric_key()
    server_key = import_rsa_key(pub_pem)
    wrapped_aes_key = server_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_message = aes_encrypt(message.encode('utf-8'), aes_key)
    payload = wrapped_aes_key + encrypted_message
    return format_message(payload)

def decrypt_message(message, private_key):
    # print(message)
    from cryptography.hazmat.primitives.asymmetric import padding
    begin_tag = '-----BEGIN ENCRYPTED MESSAGE-----'
    end_tag = '-----END ENCRYPTED MESSAGE-----'

    # Fetch the part of the PEM string between begin_tag and end_tag
    message_contents = message[len(begin_tag) + 1: -len(end_tag) - 2]

    # print(message_contents)

    # Base64 decode the string to get the binary data
    binary_der_string = b64decode(message_contents)

    # Split the binary data into wrapped key and encrypted message
    wrapped_key_length = 256
    wrapped_key = binary_der_string[:wrapped_key_length]
    encrypted_message = binary_der_string[wrapped_key_length:]

    # Unwrap the key using RSA private key
    private_key = serialization.load_pem_private_key(
        private_key.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    aes_key = private_key.decrypt(
        wrapped_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the encrypted message using the unwrapped key
    decrypted_message = aes_decrypt(encrypted_message, aes_key)

    return decrypted_message

def decrypt_message1(message, private_key):
    from cryptography.hazmat.primitives.asymmetric import padding
    begin_tag = '-----BEGIN ENCRYPTED MESSAGE-----'
    end_tag = '-----END ENCRYPTED MESSAGE-----'
    message_contents = message[len(begin_tag) + 1: -len(end_tag) - 2]
    binary_der_string = b64decode(message_contents)
    wrapped_key_length = 256
    wrapped_key = binary_der_string[:wrapped_key_length]
    encrypted_message = binary_der_string[wrapped_key_length:]
    # print(encrypted_message)
    # print(private_key)
    aes_key = private_key.decrypt(
        wrapped_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    decrypted_message = aes_decrypt(encrypted_message, aes_key)
    return decrypted_message.decode('utf-8')

def generate_url(agen, nik_agen,request):
    key_pair = generate_key()
    public_key = key_pair['publicKey']
    private_key = key_pair['privateKey']
    # print(private_key)
    access_token = getToken(request)  # Replace with your token retrieval logic
    # api_url = 'https://api-satusehat.kemkes.go.id/kyc/v1/generate-url'
    api_url=getattr(env,"SATU_SEHAT_URL_KYC","https://api-satusehat-dev.dto.kemkes.go.id/kyc/v1",)+ "/generate-url"
    pub_pem = '''
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxLwvebfOrPLIODIxAwFp
    4Qhksdtn7bEby5OhkQNLTdClGAbTe2tOO5Tiib9pcdruKxTodo481iGXTHR5033I
    A5X55PegFeoY95NH5Noj6UUhyTFfRuwnhtGJgv9buTeBa4pLgHakfebqzKXr0Lce
    /Ff1MnmQAdJTlvpOdVWJggsb26fD3cXyxQsbgtQYntmek2qvex/gPM9Nqa5qYrXx
    8KuGuqHIFQa5t7UUH8WcxlLVRHWOtEQ3+Y6TQr8sIpSVszfhpjh9+Cag1EgaMzk+
    HhAxMtXZgpyHffGHmPJ9eXbBO008tUzrE88fcuJ5pMF0LATO6ayXTKgZVU0WO/4e
    iQIDAQAB
    -----END PUBLIC KEY-----
    '''
    data = {
    'agent_name': agen,
    'agent_nik': nik_agen,
    'public_key': public_key
    }
    json_data = json.dumps(data)
    encrypted_payload = encrypt_message(json_data, pub_pem)
    headers = {
        'Content-Type': 'text/plain',
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.post(api_url, data=encrypted_payload, headers=headers)
    decrypted_response = decrypt_message(response.text, private_key)
    return decrypted_response

def getUrlKYC(request):
    if "kdCabang" in request.GET:
        kdCabang = request.GET["kdCabang"]
    else:
        kdCabang = request.session["kdCabang"]
    
    nama_pasien=request.GET["nama"]
    nik_pasien=request.GET["nik"]
    access_token=getToken(request)
    dataKYC=generate_url(nama_pasien, nik_pasien ,request)
    # print(dataKYC)
    json_datas=dataKYC
    return HttpResponse(json_datas, content_type="application/json")

def SrvIndogetUrlKYC(request):
    kdCabang = request.session["kdCabang"]
    nama_pasien=request.GET["nama"]
    nik_pasien=request.GET["nik"]
    url = getattr(
        env,
        "SERVER_INDO",
        "",
    ) + "views_satu_sehat/getUrlKYC?nama={}&nik={}&kdCabang={}".format(nama_pasien,nik_pasien,kdCabang)
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer {}".format(getToken(request)),
        "User-Agent": "SIMKLINIK MEDISIMED",
    }
    # print('url')
    # print(url)
    payload = {}
    json_data = {}
    json_data = requests.get(url)
    # print(json_data.text)
    return HttpResponse(json_data, content_type="application/json")
# KYC