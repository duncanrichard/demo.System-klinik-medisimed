from IMMODERMA.globals import Globals
from IMMODERMA.environment import env

import os
import json
import bcrypt
from pprint import pprint
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder
import requests
import hmac, hashlib
import base64
import urllib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import lzstring
from django.db import connection
from django.db import connections


def kunjunganRujukanBridging(request, noKartu, tanggal):
    kdApp = "095"
    qBPJS = "SELECT * FROM CABANG WHERE CABANG_ID=%s"
    cabang = Globals().getDataQuery(qBPJS, [request.session["kdCabang"]])
    # # pprints(cabang[0])
    # consid = cabang[0]['consid']
    # # consid = '22714'
    # secret = cabang[0]['secret']
    # # secret = '7tWA2BFC3E'
    # tStamp = int(datetime.today().timestamp())
    # tStamp = str(tStamp)
    # message = consid+"&"+tStamp
    # signature = hmac.new(bytes(secret,'UTF-8'),bytes(message,'UTF-8'), hashlib.sha256).digest()
    # # pprints(signature)
    # encodeSignature = base64.b64encode(signature)
    # #binasehat 0173b055 Binasehat-02
    # authorization = base64.b64encode(bytes(cabang[0]['userncc']+':'+cabang[0]['passwordncc']+':'+kdApp,'UTF-8'))
    # url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/kunjungan/peserta/{}".format(noKartu)
    # headers = {'X-Cons-ID': consid, 'X-Timestamp': tStamp, 'X-Signature': encodeSignature.decode('UTF-8'), 'Content-Type': 'Application/JSON','X-authorization': 'Basic '+authorization.decode('UTF-8'),'Accept': '*/*'}
    PCARE_STATUS = getattr(env, "PCARE_STATUS", "PROD")
    BPJS_USERPCARE1 = getattr(env, "BPJS_USERPCARE1", cabang[0]["userncc"])
    url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
    url = url_pcare + "/kunjungan/peserta/{}".format(noKartu)
    # res = requests.get(url,headers=headers)
    datas = bridgeBPJS(request, url, "get")
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    prints("------------------")
    prints(url)
    # prints(headers)
    prints(datas)
    prints("------------------")
    # prints(cabang[0]['userncc'])
    noRujukan = "-"
    # print('dataRujukan')
    # print(datas)
    # print('dataRujukan')
    if datas["metaData"]["code"] == 200:
        for dataRujukan in datas["response"]["list"]:
            # #print(dataRujukan)
            PCARE_STATUS = getattr(env, "PCARE_STATUS", "PROD")
            if PCARE_STATUS == "DEV":
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"] == BPJS_USERPCARE1
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    # prints(dataRujukan['noKunjungan'])
                    noRujukan = "{}".format(dataRujukan["noKunjungan"])
            else:
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"]
                    == cabang[0]["userncc"]
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    # prints(dataRujukan['noKunjungan'])
                    noRujukan = "{}".format(dataRujukan["noKunjungan"])

    return noRujukan


def cekDiagnosaTACC(diagnosa):
    # kdApp = '095'

    # cursor = connection.cursor()
    # q = "select * from CABANG"
    # cursor.execute(q)
    # cabang = Globals().dictfetchall(cursor)
    # # pprints(cabang[0])
    # consid = cabang[0]['consid']
    # # consid = '22714'
    # secret = cabang[0]['secret']
    # # secret = '7tWA2BFC3E'
    # tStamp = int(datetime.today().timestamp())
    # tStamp = str(tStamp)
    # message = consid+"&"+tStamp
    # signature = hmac.new(bytes(secret,'UTF-8'),bytes(message,'UTF-8'), hashlib.sha256).digest()
    # # pprints(signature)
    # encodeSignature = base64.b64encode(signature)
    # #binasehat 0173b055 Binasehat-02
    # authorization = base64.b64encode(bytes(cabang[0]['userncc']+':'+cabang[0]['passwordncc']+':'+kdApp,'UTF-8'))
    # url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/diagnosa/{}/0/100".format(diagnosa)
    # headers = {'X-Cons-ID': consid, 'X-Timestamp': tStamp, 'X-Signature': encodeSignature.decode('UTF-8'), 'Content-Type': 'Application/JSON','X-authorization': 'Basic '+authorization.decode('UTF-8'),'Accept': '*/*'}
    # res = requests.get(url,headers=headers)

    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/diagnosa/{}/0/100".format(diagnosa)
    method = "get"
    datas = bridgeBPJS(request, url, method)
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    # print('datas')
    # print(datas)
    statusTACC = "0"
    if datas["metaData"]["code"] == 200:
        for dataListTACC in datas["response"]["list"]:
            if (
                dataListTACC["kdDiag"] == diagnosa
                and dataListTACC["nonSpesialis"] == True
            ):
                statusTACC = "1"

    return statusTACC


def cekDiagnosaTACCS(request):
    kdApp = "095"
    diagnosa = request.GET["diagnosa"]
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # pprints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    # pprints(signature)
    encodeSignature = base64.b64encode(signature)
    # binasehat 0173b055 Binasehat-02
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = (
        "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/diagnosa/{}/0/100".format(
            diagnosa
        )
    )
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    res = requests.get(url, headers=headers)
    datas = res.json()
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    prints(datas)
    statusTACC = "0"
    response = {"success": False, "message": " _ "}
    if datas["metaData"]["code"] == 200:
        for dataListTACC in datas["response"]["list"]:
            if dataListTACC["kdDiag"] == diagnosa:
                response = {
                    "success": True,
                    "message": "%s_%s"
                    % (dataListTACC["kdDiag"], dataListTACC["nmDiag"]),
                }

    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def jenisPelayananBridgingPCARE(noKartu, noKunjungan):
    kdApp = "095"

    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # pprints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    # pprints(signature)
    encodeSignature = base64.b64encode(signature)
    # binasehat 0173b055 Binasehat-02
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/kunjungan/peserta/{}".format(
        noKartu
    )
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    res = requests.get(url, headers=headers)
    datas = res.json()
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    # prints(cabang[0]['userncc'])
    nmTkp = "-"
    if datas["metaData"]["code"] == 200:
        # prints(datas['response']['list'])
        for dataRujukan in datas["response"]["list"]:
            # prints(dataRujukan['noKunjungan'])
            # prints(noKunjungan)
            if dataRujukan["noKunjungan"] == noKunjungan:
                nmTkp = "{}".format(dataRujukan["tkp"]["nmTkp"])

    return nmTkp


def getkunjunganRujukanBridging(request):
    # kdApp = '095'
    noKartu = request.GET["noKartu"]
    tanggal = request.GET["tanggal"]
    # cursor = connection.cursor()
    # q = "select * from CABANG"
    # cursor.execute(q)
    # cabang = Globals().dictfetchall(cursor)
    # # pprints(cabang[0])
    # consid = cabang[0]['consid']
    # # consid = '22714'
    # secret = cabang[0]['secret']
    # # secret = '7tWA2BFC3E'
    # tStamp = int(datetime.today().timestamp())
    # tStamp = str(tStamp)
    # message = consid+"&"+tStamp
    # signature = hmac.new(bytes(secret,'UTF-8'),bytes(message,'UTF-8'), hashlib.sha256).digest()
    # # pprints(signature)
    # encodeSignature = base64.b64encode(signature)
    # #binasehat 0173b055 Binasehat-02
    # authorization = base64.b64encode(bytes(cabang[0]['userncc']+':'+cabang[0]['passwordncc']+':'+kdApp,'UTF-8'))
    # url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/kunjungan/peserta/{}".format(noKartu)
    # headers = {'X-Cons-ID': consid, 'X-Timestamp': tStamp, 'X-Signature': encodeSignature.decode('UTF-8'), 'Content-Type': 'Application/JSON','X-authorization': 'Basic '+authorization.decode('UTF-8'),'Accept': '*/*'}
    # res = requests.get(url,headers=headers)
    # datas = res.json()
    # res = requests.get(url,headers=headers)
    url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
    url = url_pcare + "/kunjungan/peserta/{}".format(noKartu)
    datas = bridgeBPJS(request, url, "get")
    # print(datas)
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    # print(json_data)
    response = []
    noRujukan = "-"
    if datas["metaData"]["code"] == 200:
        for dataRujukan in datas["response"]["list"]:
            PCARE_STATUS = getattr(env, "PCARE_STATUS", "PROD")
            if PCARE_STATUS == "DEV":
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"] == BPJS_USERPCARE1
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    response = dataRujukan
            else:
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"]
                    == cabang[0]["userncc"]
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    response = dataRujukan

    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getDataPickerPCAREBPJS(request):
    kdApp = "095"

    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # prints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    # pprints(signature)
    encodeSignature = base64.b64encode(signature)
    # binasehat 0173b055 Binasehat-02

    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    if "type" in request.GET:
        if request.GET["type"] == "refKhusus":
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            url = url_pcare + "/spesialis/khusus"
            data = bridgeBPJS(request, url, "get")
            # prints()
            response = []
            if data["metaData"]["code"] == 200:
                response = data["response"]["list"]
        elif request.GET["type"] == "refSpesialis":
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            url = url_pcare + "/spesialis"
            data = bridgeBPJS(request, url, "get")
            response = []
            if data["metaData"]["code"] == 200:
                response = data["response"]["list"]
        elif request.GET["type"] == "refSubspesialis":
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            url = url_pcare + "/spesialis/{}/subspesialis".format(
                request.GET["kdSpesialis"]
            )
            data = bridgeBPJS(request, url, "get")
            # response=data['response']['list']
            response = []
            if data["metaData"]["code"] == 200:
                response = data["response"]["list"]
        elif request.GET["type"] == "refSarana":
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            url = url_pcare + "/spesialis/sarana"
            data = bridgeBPJS(request, url, "get")
            # response=data['response']['list']
            response = []
            if data["metaData"]["code"] == 200:
                response = data["response"]["list"]
        elif request.GET["type"] == "getFaskesRujukanSubSpes":
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            kdSarana = ""
            if request.GET["kdSarana"] == "-":
                kdSarana = "9"
            else:
                kdSarana = request.GET["kdSarana"]
            url = (
                url_pcare
                + "/spesialis/rujuk/subspesialis/{}/sarana/{}/tglEstRujuk/{}".format(
                    request.GET["kdSubSpesialis"], kdSarana, request.GET["tglEstRujuk"]
                )
            )
            data = bridgeBPJS(request, url, "get")
            # response=data['response']['list']
            response = []
            if data["metaData"]["code"] == 200:
                response = data["response"]["list"]
        elif request.GET["type"] == "getFaskesRujukanKhusus1":
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            url = (
                url_pcare
                + "/spesialis/rujuk/khusus/{}/noKartu/{}/tglEstRujuk/{}".format(
                    request.GET["kdKhusus"],
                    request.GET["noKartu"],
                    request.GET["tglEstRujuk"],
                )
            )
            data = bridgeBPJS(request, url, "get")
            # response=data['response']['list']
            response = []
            if data["metaData"]["code"] == 200:
                response = data["response"]["list"]
        elif request.GET["type"] == "getFaskesRujukanKhusus2":
            # hema dan thala
            # url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/spesialis/"
            # url += "rujuk/khusus/{}/subspesialis/{}/noKartu/{}/tglEstRujuk/{}".format(request.GET['kdKhusus'],request.GET['kdSubSpesialis'],request.GET['noKartu'],request.GET['tglEstRujuk'])
            # res = requests.get(url,headers=headers)
            # data = res.json()
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            url = (
                url_pcare
                + "/spesialis/rujuk/khusus/{}/subspesialis/{}/noKartu/{}/tglEstRujuk/{}".format(
                    request.GET["kdKhusus"],
                    request.GET["kdSubSpesialis"],
                    request.GET["noKartu"],
                    request.GET["tglEstRujuk"],
                )
            )
            data = bridgeBPJS(request, url, "get")
            # response=data['response']['list']
            response = []
            if data["metaData"]["code"] == 200:
                response = data["response"]["list"]
        elif request.GET["type"] == "getDataRujukan":
            response = []
            if request.GET["noRujukan"] != "-":
                url_pcare = getattr(
                    env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
                )
                url = url_pcare + "/kunjungan/rujukan/{}".format(
                    request.GET["noRujukan"]
                )
                response = bridgeBPJS(request, url, "get")
            # if response["metaData"]["code"]!=200:
            # 	if len(request.GET['noRujukan'])<19:
            # 		response={'success':False,'message':'no kunjungan tidak boleh kurang dari 19 digits'}
            # 	else:
            # 		response={'success':False,'message':'no kunjungan tidak valid!'}

            # #print(response)
        elif request.GET["type"] == "getMCU":
            # hema dan thala
            # url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/mcu/kunjungan/{}".format(request.GET['noRujukan'])
            # res = requests.get(url,headers=headers)
            # data = res.json()
            response = []
            if request.GET["noRujukan"] != "-":
                url_pcare = getattr(
                    env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
                )
                url = url_pcare + "/mcu/kunjungan/{}".format(request.GET["noRujukan"])
                data = bridgeBPJS(request, url, "get")
                # response=data['response']['list']
                if data["metaData"]["code"] == 200:
                    response = data["response"]["list"]
        elif request.GET["type"] == "getDataKunjunganKlinik":
            # get Data rujukan klinik
            cursorKunjunganKlinikBrd = connection.cursor()
            qKunjunganKlinikBrd = "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' ".format(
                request.GET["MRDNO_TRANSAKSI"]
            )
            cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
            response = Globals().dictfetchall(cursorKunjunganKlinikBrd)
        elif request.GET["type"] == "getDataKlinikLayananNonKapitasi":
            # get Data layanan non kapitasi
            cursorKunjunganKlinikBrd = connection.cursor()
            qKunjunganKlinikBrd = "SELECT * FROM MR_KLINIK_PELAYANAN_NONKAPITASI where MRDNO_TRANSAKSI='{}' ".format(
                request.GET["MRDNO_TRANSAKSI"]
            )
            cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
            response = Globals().dictfetchall(cursorKunjunganKlinikBrd)
    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def delHasilLabBridgingBPJSLab(request):
    kdApp = "095"
    response = {}
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # pprints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    encodeSignature = base64.b64encode(signature)
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/mcu/{}/kunjungan/{}".format(
        request.POST["kdMCU"], request.POST["noKunjungan"]
    )
    # prints(url)
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    res1 = requests.delete(url, headers=headers)
    # prints(res1)
    datas1 = res1.json()
    # prints(datas1)
    if datas1["metaData"]["code"] == 200:
        response = {"success": True, "message": "Berhasil Hapus"}
    else:
        response = {"success": False, "message": datas1["metaData"]["message"]}
    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def crudBridgingBPJSLab(request):
    kdApp = "095"
    response = {}
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # pprints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    encodeSignature = base64.b64encode(signature)
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/mcu"
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }

    if request.POST["kdMCU"] == "0":
        payload = {
            "kdMCU": 0,
            "noKunjungan": request.POST["noKunjungan"],
            "kdProvider": cabang[0]["userncc"],
            "tglPelayanan": request.POST["tglPelayanan"],
            "tekananDarahSistole": request.POST["tekananDarahSistole"],
            "tekananDarahDiastole": request.POST["tekananDarahDiastole"],
            "radiologiFoto": request.POST["radiologiFoto"],
            "darahRutinHemo": request.POST["darahRutinHemo"],
            "darahRutinLeu": request.POST["darahRutinLeu"],
            "darahRutinErit": request.POST["darahRutinErit"],
            "darahRutinLaju": request.POST["darahRutinLaju"],
            "darahRutinHema": request.POST["darahRutinHema"],
            "darahRutinTrom": request.POST["darahRutinTrom"],
            "lemakDarahHDL": request.POST["lemakDarahHDL"],
            "lemakDarahLDL": request.POST["lemakDarahLDL"],
            "lemakDarahChol": request.POST["lemakDarahChol"],
            "lemakDarahTrigli": request.POST["lemakDarahTrigli"],
            "gulaDarahSewaktu": request.POST["gulaDarahSewaktu"],
            "gulaDarahPuasa": request.POST["gulaDarahPuasa"],
            "gulaDarahPostPrandial": request.POST["gulaDarahPostPrandial"],
            "gulaDarahHbA1c": request.POST["gulaDarahHbA1c"],
            "fungsiHatiSGOT": request.POST["fungsiHatiSGOT"],
            "fungsiHatiSGPT": request.POST["fungsiHatiSGPT"],
            "fungsiHatiGamma": request.POST["fungsiHatiGamma"],
            "fungsiHatiProtKual": request.POST["fungsiHatiProtKual"],
            "fungsiHatiAlbumin": request.POST["fungsiHatiAlbumin"],
            "fungsiGinjalCrea": request.POST["fungsiGinjalCrea"],
            "fungsiGinjalUreum": request.POST["fungsiGinjalUreum"],
            "fungsiGinjalAsam": request.POST["fungsiGinjalAsam"],
            "fungsiJantungABI": request.POST["fungsiJantungABI"],
            "fungsiJantungEKG": request.POST["fungsiJantungEKG"],
            "fungsiJantungEcho": request.POST["fungsiJantungEcho"],
            "funduskopi": request.POST["funduskopi"],
            "pemeriksaanLain": request.POST["pemeriksaanLain"],
            "keterangan": request.POST["keterangan"],
        }
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        # prints(res)
        datas = res.json()
        # prints(datas)
        if datas["metaData"]["code"] == 201:
            response = {"success": True, "message": "Berhasil Insert"}
        else:
            response = {"success": False, "message": datas["metaData"]["message"]}
    else:
        payload = {
            "kdMCU": request.POST["kdMCU"],
            "noKunjungan": request.POST["noKunjungan"],
            "kdProvider": cabang[0]["userncc"],
            "tglPelayanan": request.POST["tglPelayanan"],
            "tekananDarahSistole": request.POST["tekananDarahSistole"],
            "tekananDarahDiastole": request.POST["tekananDarahDiastole"],
            "radiologiFoto": request.POST["radiologiFoto"],
            "darahRutinHemo": request.POST["darahRutinHemo"],
            "darahRutinLeu": request.POST["darahRutinLeu"],
            "darahRutinErit": request.POST["darahRutinErit"],
            "darahRutinLaju": request.POST["darahRutinLaju"],
            "darahRutinHema": request.POST["darahRutinHema"],
            "darahRutinTrom": request.POST["darahRutinTrom"],
            "lemakDarahHDL": request.POST["lemakDarahHDL"],
            "lemakDarahLDL": request.POST["lemakDarahLDL"],
            "lemakDarahChol": request.POST["lemakDarahChol"],
            "lemakDarahTrigli": request.POST["lemakDarahTrigli"],
            "gulaDarahSewaktu": request.POST["gulaDarahSewaktu"],
            "gulaDarahPuasa": request.POST["gulaDarahPuasa"],
            "gulaDarahPostPrandial": request.POST["gulaDarahPostPrandial"],
            "gulaDarahHbA1c": request.POST["gulaDarahHbA1c"],
            "fungsiHatiSGOT": request.POST["fungsiHatiSGOT"],
            "fungsiHatiSGPT": request.POST["fungsiHatiSGPT"],
            "fungsiHatiGamma": request.POST["fungsiHatiGamma"],
            "fungsiHatiProtKual": request.POST["fungsiHatiProtKual"],
            "fungsiHatiAlbumin": request.POST["fungsiHatiAlbumin"],
            "fungsiGinjalCrea": request.POST["fungsiGinjalCrea"],
            "fungsiGinjalUreum": request.POST["fungsiGinjalUreum"],
            "fungsiGinjalAsam": request.POST["fungsiGinjalAsam"],
            "fungsiJantungABI": request.POST["fungsiJantungABI"],
            "fungsiJantungEKG": request.POST["fungsiJantungEKG"],
            "fungsiJantungEcho": request.POST["fungsiJantungEcho"],
            "funduskopi": request.POST["funduskopi"],
            "pemeriksaanLain": request.POST["pemeriksaanLain"],
            "keterangan": request.POST["keterangan"],
        }

        res1 = requests.put(url, data=json.dumps(payload), headers=headers)
        # prints(json.dumps(payload))
        # prints(res1)
        # # prints(headers)
        datas1 = res1.json()
        # prints(datas1)
        if datas1["metaData"]["code"] == 200:
            response = {"success": True, "message": "Berhasil Insert"}
        else:
            response = {"success": False, "message": datas1["metaData"]["message"]}

    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getBridgingBPJSObat(request):
    kdApp = "095"
    response = {}
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # pprints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    encodeSignature = base64.b64encode(signature)
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = (
        "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/obat/kunjungan/{}".format(
            request.GET["noKunjungan"]
        )
    )
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    res = requests.get(url, headers=headers)
    # prints(res)
    datas = res.json()
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def delBridgingBPJSObat(request):
    kdApp = "095"
    response = {}
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # pprints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    encodeSignature = base64.b64encode(signature)
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = (
        "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/obat/kunjungan/{}".format(
            request.GET["noKunjungan"]
        )
    )
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    res = requests.get(url, headers=headers)
    # prints(res)
    datas = res.json()
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    if datas["metaData"]["code"] == 200:
        for dataObat in datas["response"]["list"]:
            url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/obat/{}/kunjungan/{}".format(
                dataObat["kdObatSK"], request.GET["noKunjungan"]
            )
            headers = {
                "X-Cons-ID": consid,
                "X-Timestamp": tStamp,
                "X-Signature": encodeSignature.decode("UTF-8"),
                "Content-Type": "Application/JSON",
                "X-authorization": "Basic " + authorization.decode("UTF-8"),
                "Accept": "*/*",
            }
            deleteObat = requests.delete(url, headers=headers)
            prints(deleteObat.json())
        # if dataRujukan['providerPelayanan']['kdProvider']==cabang[0]['userncc'] and dataRujukan['tglKunjungan']==tanggal:
        # 	response=dataRujukan

    datas = res.json()
    json_data = json.dumps(datas, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def crudBridgingBPJSObat(noTrans, noKunjungan):
    kdApp = "095"
    response = {}
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    # pprints(cabang[0])
    consid = cabang[0]["consid"]
    # consid = '22714'
    secret = cabang[0]["secret"]
    # secret = '7tWA2BFC3E'
    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()

    # DELETE OBAT BRIDGING
    encodeSignature = base64.b64encode(signature)
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = (
        "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/obat/kunjungan/{}".format(
            noKunjungan
        )
    )
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    res = requests.get(url, headers=headers)
    # prints("DELETE OBAT BRIDGING")
    deldatas = res.json()
    if deldatas["metaData"]["code"] == 200:
        for dataObat in deldatas["response"]["list"]:
            url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/obat/{}/kunjungan/{}".format(
                dataObat["kdObatSK"], noKunjungan
            )
            headers = {
                "X-Cons-ID": consid,
                "X-Timestamp": tStamp,
                "X-Signature": encodeSignature.decode("UTF-8"),
                "Content-Type": "Application/JSON",
                "X-authorization": "Basic " + authorization.decode("UTF-8"),
                "Accept": "*/*",
            }
            deleteObat = requests.delete(url, headers=headers)
            # prints(deleteObat.json())

    encodeSignature = base64.b64encode(signature)
    authorization = base64.b64encode(
        bytes(
            cabang[0]["userncc"] + ":" + cabang[0]["passwordncc"] + ":" + kdApp, "UTF-8"
        )
    )
    url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/obat/kunjungan"
    headers = {
        "X-Cons-ID": consid,
        "X-Timestamp": tStamp,
        "X-Signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
    }
    response = {"success": True, "message": "Berhasil Bridging"}
    q = " SELECT FDRBRG_ID,FDRBRGN,FDRSATUAN,CAST(FDRQTY as int) as FDRQTY,CAST(FDRDOSIS as int) as FDRDOSIS,CAST(FDRDOSIS2 as int) as FDRDOSIS2,FDRRACIK_ID"
    q += " FROM ERESEPDOKTERD as E1 "
    q += " LEFT JOIN ERESEPDOKTER as E2 ON E1.FDRBUKTI_ID=E2.FHRNO_TRANSAKSI"
    q += " WHERE E2.FHRBUKTI_ID='{}' AND E1.FDRRACIK_ID ='NULL'".format(noTrans)
    # prints(q)
    cursor.execute(q)
    listdataNonRacik = Globals().dictfetchall(cursor)
    # prints(listdataNonRacik)
    for dataNonRacik in listdataNonRacik:
        payload = {
            "kdObatSK": 0,
            "noKunjungan": noKunjungan,
            "racikan": False,
            "kdRacikan": None,
            "obatDPHO": False,
            "kdObat": dataNonRacik["FDRBRG_ID"],
            "signa1": dataNonRacik["FDRDOSIS"],
            "signa2": dataNonRacik["FDRDOSIS2"],
            "jmlObat": dataNonRacik["FDRQTY"],
            "jmlPermintaan": 0,
            "nmObatNonDPHO": dataNonRacik["FDRBRGN"],
        }
        # prints(payload)
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        # prints(res)
        datas = res.json()
        # prints(datas)
        if datas["metaData"]["code"] != 201:
            response = {"success": False, "message": datas["metaData"]["message"]}
            json_data = json.dumps(response, cls=DjangoJSONEncoder)
            return HttpResponse(json_data, content_type="application/json")

    q = " SELECT FDRBRG_ID,FDRBRGN,FDRSATUAN,CAST(FDRQTY AS int) as FDRQTY,CAST(FDRDOSIS AS int) as FDRDOSIS,CAST(FDRDOSIS2 AS int) as FDRDOSIS2,FDRRACIK_ID,CAST(FERCKNQTY AS int) as FERCKNQTY"
    q += " FROM ERESEPDOKTERD as E1 "
    q += " LEFT JOIN ERESEPDOKTER as E2 ON E1.FDRBUKTI_ID=E2.FHRNO_TRANSAKSI"
    q += " LEFT JOIN ERESEPRACIK as E3 ON E1.FDRRACIK_ID=E3.FERRACIK_ID"
    q += " WHERE E2.FHRBUKTI_ID='{}' AND E1.FDRRACIK_ID <>'NULL' ".format(noTrans)
    cursor.execute(q)
    listdataRacik = Globals().dictfetchall(cursor)
    # # prints(headers)
    # prints(q)
    for dataRacik in listdataRacik:
        payload = {
            "kdObatSK": 0,
            "noKunjungan": noKunjungan,
            "racikan": True,
            "kdRacikan": "R.{}".format(dataRacik["FDRRACIK_ID"][-2:]),
            "obatDPHO": False,
            "kdObat": dataRacik["FDRBRG_ID"],
            "signa1": dataRacik["FDRDOSIS"],
            "signa2": dataRacik["FDRDOSIS2"],
            "jmlObat": dataRacik["FDRQTY"],
            "jmlPermintaan": dataRacik["FERCKNQTY"],
            "nmObatNonDPHO": dataRacik["FDRBRGN"],
        }
        # prints(payload)
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        # prints(res)
        datas = res.json()
        # prints(datas)
        if datas["metaData"]["code"] != 201:
            response = {"success": False, "message": datas["metaData"]["message"]}
            json_data = json.dumps(response, cls=DjangoJSONEncoder)
            return HttpResponse(json_data, content_type="application/json")

    # json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return response


def bridgingPcare(request):
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)

    # #print(request.POST)
    qPoli = "SELECT * FROM POLIKLINIK where FMPKLINIK_ID='{}'".format(
        request.POST["MRDKD_UNIT"]
    )
    cursorPoli = connection.cursor()
    cursorPoli.execute(qPoli)
    dataPoli = Globals().dictfetchall(cursorPoli)
    FMPKODEBPJS = dataPoli[0]["FMPKODEBPJS"]

    url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
    url = url_pcare + "/peserta/noka/{}".format(request.POST["noBPJS"])
    dataPeserta = bridgeBPJS(request, url, "get")

    # print('bridgingPcare()')
    # print(dataPeserta)
    if dataPeserta:
        if dataPeserta["response"]["kdProviderPst"]["kdProvider"]:
            kdProviderPeserta = dataPeserta["response"]["kdProviderPst"]["kdProvider"]
        else:
            kdProviderPeserta = cabang[0]["userncc"]
        # print('request.POST.items()')
        # print(request.POST.items())
        # payload = {
        # 	"kdProviderPeserta": kdProviderPeserta,
        # 	"tglDaftar": request.POST['MRDTGL_DIAGNOSA'],
        # 	"noKartu": request.POST['noBPJS'],
        # 	"kdPoli": FMPKODEBPJS,
        # 	"keluhan": None,
        # 	"kunjSakit": True,
        # 	"sistole": 110,
        # 	"diastole": 90,
        # 	"beratBadan": 80,
        # 	"tinggiBadan": 170,
        # 	"respRate": 0,
        # 	"lingkarPerut": 0,
        # 	"heartRate": 0,
        # 	"rujukBalik": 0,
        # 	"kdTkp": "10"
        # }

        payload = {
            "tglDaftar": request.POST["MRDTGL_DIAGNOSA"],
            "noKartu": request.POST["noBPJS"],
            "kdPoli": FMPKODEBPJS,
            "keluhan": request.POST["FMSKLU"],
            "kunjSakit": True,
            "sistole": int(request.POST["sistole"]),
            "diastole": int(request.POST["diastole"]),
            "beratBadan": int(request.POST["FMSBB"]),
            "tinggiBadan": int(request.POST["FMSTB"]),
            "respRate": int(request.POST["FMSRR"]),
            "lingkarPerut": int(request.POST["LingkarPerut"]),
            "heartRate": int(request.POST["FMSNADI"]),
            "rujukBalik": 0,
            "kdTkp": "10",
        }
        # print('kirim pendaftaran')
        # print(payload)
        url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
        url = url_pcare + "/pendaftaran"
        res = bridgeBPJS(request, url, "post", payload)
        if res is not None:
            prints(res)
        else:
            prints("gagal daftar")
            # print(res)


def bridgingPostRujukanSpesialis(request):
    if len(request.POST["noBPJS"]) < 13:
        return "No BPJS tidak boleh kurang dari 13 digits"

    if len(request.POST["noBPJS"]) > 13:
        return "No BPJS tidak valid"
    # daftars=bridgingPcare(request)
    # cursor = connection.cursor()
    # q = "select * from CABANG"
    # cursor.execute(q)
    # cabang = Globals().dictfetchall(cursor)
    qPoli = "SELECT * FROM POLIKLINIK where FMPKLINIK_ID='{}'".format(
        request.POST["MRDKD_UNIT"]
    )
    cursorPoli = connection.cursor()
    cursorPoli.execute(qPoli)
    dataPoli = Globals().dictfetchall(cursorPoli)
    FMPKODEBPJS = dataPoli[0]["FMPKODEBPJS"]

    alasanTacc = None
    kdTacc = request.POST["kdTacc"]
    if request.POST["kdTacc"] == "":
        kdTacc = "0"
    if request.POST["alasanTacc"] == "":
        alasanTacc = None
    if kdTacc == "1":
        # alasanTacc=["< 3 Hari", ">= 3 - 7 Hari", ">= 7 Hari"][int(request.POST['alasanTacc'])]
        alasanTacc = ["< 3 Hari", ">= 3 - 7 Hari", ">= 7 Hari"]
    if kdTacc == "2":
        # alasanTacc=["< 1 Bulan", ">= 1 Bulan s/d < 12 Bulan", ">= 1 Tahun s/d < 5 Tahun",">= 5 Tahun s/d < 12 Tahun", ">= 12 Tahun s/d < 55 Tahun", ">= 55 Tahun"][int(request.POST['alasanTacc'])]
        alasanTacc = [
            "< 1 Bulan",
            ">= 1 Bulan s/d < 12 Bulan",
            ">= 1 Tahun s/d < 5 Tahun",
            ">= 5 Tahun s/d < 12 Tahun",
            ">= 12 Tahun s/d < 55 Tahun",
            ">= 55 Tahun",
        ]
    if kdTacc == "3":
        alasanTacc = request.POST["alasanTacc"]
    if kdTacc == "4":
        # alasanTacc=request.POST['alasanTacc']
        alasanTacc = ["< 3 Hari", ">= 3 - 7 Hari", ">= 7 Hari"]
    # if kdTacc=="":
    # 	kdTacc="0"

    # q = "SELECT * FROM BPJS_SEP where FMNOTRANSAKSI='{}' and FMNO_KARTU='{}' and FMTGL_SEP=CONVERT(datetime,'{}',105)".format(request.POST['MRDNO_TRANSAKSI'],request.POST['noBPJS'],request.POST['MRDTGL_DIAGNOSA'])
    # q = "SELECT * FROM MR_DIAGNOSA where MRDNO_TRANSAKSI='{}' AND MRD_NORUJUKAN IS NOT NULL".format(request.POST['notrans'])
    # cursor.execute(q)
    # dataPCARE = Globals().dictfetchall(cursor)

    # cursorqDdataPenyakit = connection.cursor()
    # qDdataPenyakit = "SELECT * FROM MR_PENYAKIT where MRPNO_TRANSAKSI='{}' AND MRPTGL_MASUK=CONVERT(datetime,'{}',105) AND MR_PENYAKIT.MRPSTAT_DIAG='5' ".format(request.POST['notrans'],request.POST['MRDTGL_DIAGNOSA'])
    # cursorqDdataPenyakit.execute(qDdataPenyakit)
    # dataPenyakit = Globals().dictfetchall(cursorqDdataPenyakit)
    qDdataPenyakit = "SELECT * FROM MR_PENYAKIT where MRPNO_TRANSAKSI='{}'  AND MR_PENYAKIT.MRPSTAT_DIAG='5' ".format(
        request.POST["notrans"]
    )
    dataPenyakit = Globals().getDataQuery(qDdataPenyakit, [])
    # print('dataPenyakit')
    # print(qDdataPenyakit)
    # print(dataPenyakit)

    # cursorqDdataPenyakit2 = connection.cursor()
    # qDdataPenyakit2 = "SELECT * FROM MR_PENYAKIT where MRPNO_TRANSAKSI='{}' AND MRPTGL_MASUK=CONVERT(datetime,'{}',105) AND MR_PENYAKIT.MRPSTAT_DIAG<>'5' ".format(request.POST['notrans'],request.POST['MRDTGL_DIAGNOSA'])
    # cursorqDdataPenyakit2.execute(qDdataPenyakit2)
    # dataPenyakit2 = Globals().dictfetchall(cursorqDdataPenyakit2)
    qDdataPenyakit2 = "SELECT * FROM MR_PENYAKIT where MRPNO_TRANSAKSI='{}' AND MR_PENYAKIT.MRPSTAT_DIAG<>'5' ".format(
        request.POST["notrans"]
    )
    dataPenyakit2 = Globals().getDataQuery(qDdataPenyakit2, [])
    # print(qDdataPenyakit2)
    # prints(dataPenyakit2)
    # prints(len(dataPenyakit2))
    if int(len(dataPenyakit2)) > 0:
        dataPenyakit2s = dataPenyakit2[0]["MRPKD_PENYAKIT"]
        if int(len(dataPenyakit2)) > 1:
            dataPenyakit3s = dataPenyakit2[1]["MRPKD_PENYAKIT"]
        else:
            dataPenyakit3s = None
    else:
        dataPenyakit2s = None
        dataPenyakit3s = None

    # prints(dataPenyakit2s)
    # prints(dataPenyakit3s)
    # cursorqDdataDokter = connection.cursor()
    # qDdataDokter = "SELECT * FROM DOKTER where FMDDOKTER_ID='{}' ".format(request.POST['MRDKD_DOKTER'])
    # cursorqDdataDokter.execute(qDdataDokter)
    # dataDokter = Globals().dictfetchall(cursorqDdataDokter)
    qDdataDokter = "SELECT * FROM DOKTER where FMDDOKTER_ID='{}' ".format(
        request.POST["MRDKD_DOKTER"]
    )
    dataDokter = Globals().getDataQuery(qDdataDokter, [])

    # prints(dataPCARE)

    noKunjungan = None
    # if int(len(dataPCARE))>0:
    # 	noKunjungan=dataPCARE[0]['MRD_NORUJUKAN']
    if int(len(dataPenyakit)) > 0:
        dataPenyakit = dataPenyakit[0]["MRPKD_PENYAKIT"]
    if int(len(dataDokter)) > 0:
        FMDDOKTER_ID_BPJS = dataDokter[0]["FMDDOKTER_ID_BPJS"]
    if FMDDOKTER_ID_BPJS:
        suksesambilid = "true"
    else:
        FMDDOKTER_ID_BPJS = "130309"
        # "tglDaftar": request.POST['MRDTGL_DIAGNOSA'],
    rujukLanjut = None
    subSpesialis = None
    khusus = None
    if request.POST["StatusPulang"] == "4":
        if request.POST["opsiRujuk_rbs"] == "1":
            khusus = {
                "kdKhusus": request.POST["kondisiKhususKategori"],
                "kdSubSpesialis": None,
                "catatan": request.POST["catatanRujukan"],
            }

        if request.POST["opsiRujuk_rbs"] == "2":
            subSpesialis = {
                "kdSubSpesialis1": request.POST["spesialisRujukan"],
                "kdSarana": request.POST["rujukanSarana"],
            }

        rujukLanjut = {
            "kdppk": request.POST["ppkRujukan"],
            "tglEstRujuk": request.POST["tglRujukan"],
            "subSpesialis": subSpesialis,
            "khusus": khusus,
        }

    try:
        payload = {
            "noKunjungan": noKunjungan,
            "noKartu": request.POST["noBPJS"],
            "tglDaftar": request.POST["MRDTGL_DIAGNOSA"],
            "kdPoli": FMPKODEBPJS,
            "keluhan": request.POST["CPTD_KELUHANUTAMA"],
            "kdSadar": request.POST["TTVKESADARAN"],
            "sistole": int(request.POST["TTVTSISTOL"]),
            "diastole": int(request.POST["TTVDIASTOL"]),
            "beratBadan": int(request.POST["TTVBERAT_BADAN"]),
            "tinggiBadan": int(request.POST["TTVTINGGI_BADAN"]),
            "respRate": int(request.POST["TTVNAFAS"]),
            "heartRate": int(request.POST["TTVNADI"]),
            "lingkarPerut": int(request.POST["TTV_LINGKAR_PERUT"]),
            "terapi": request.POST["TERAPI"],
            "kdStatusPulang": request.POST["StatusPulang"],
            "tglPulang": request.POST["MRDTGL_DIAGNOSA"],
            "kdDokter": FMDDOKTER_ID_BPJS,
            "kdDiag1": dataPenyakit,
            "kdDiag2": dataPenyakit2s,
            "kdDiag3": dataPenyakit3s,
            "kdPoliRujukInternal": None,
            "rujukLanjut": rujukLanjut,
            "kdTacc": int(kdTacc),
            "alasanTacc": alasanTacc,
        }
    except:
        restHasil = {
            "success": False,
            "messages": "\n TETAPI TIDAK TERSAVE PCARE KARENA: \n KELUHAN,TTV BELUM LENGKAP",
        }
        return restHasil
    # print('payload kunjungan')
    # print(payload)
    # url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/kunjungan"
    url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
    url = url_pcare + "/kunjungan"

    # headers = {'X-Cons-ID': consid, 'X-Timestamp': tStamp, 'X-Signature': encodeSignature.decode('UTF-8'), 'Content-Type': 'Application/JSON','X-authorization': 'Basic '+authorization.decode('UTF-8'),'Accept': '*/*'}
    # prints('-----------')
    # prints(url)
    # # prints(headers)
    # prints(payload)
    # prints('-----------')
    # prints(int(len(dataPCARE)))

    # curCariNoRujukan = connection.cursor()
    # curCariNoRujukan.execute(qCariNoRujukan)
    # dataCariNoRujukan = Globals().dictfetchall(curCariNoRujukan)
    qCariNoRujukan = "SELECT ISNULL(a.noKunjungan,'-') as noKunjungan FROM MR_KUNJUNGAN_KLINIK_BRIDGING a where a.MRDNO_TRANSAKSI='{}' and ISNULL(a.noKunjungan,'-')<>'-'  and ISNULL(a.noKunjungan,'-')<>'None' ".format(
        request.POST["notrans"]
    )
    dataCariNoRujukan = Globals().getDataQuery(qCariNoRujukan, [])
    if len(dataCariNoRujukan) > 0:
        noKunjungan = dataCariNoRujukan[0]["noKunjungan"]
    else:
        noKunjungan = kunjunganRujukanBridging(
            request, request.POST["noBPJS"], request.POST["MRDTGL_DIAGNOSA"]
        )
    # return "No BPJS tidak valid"
    # print('noKunjungan')
    # print(noKunjungan)
    # return noKunjungan
    # return 0

    restHasil = {"success": True, "messages": "OK"}
    if noKunjungan != "-":
        # # prints(headers)
        # print('update Kunjungan')
        # print(noKunjungan)
        payload = {
            "noKunjungan": noKunjungan,
            "noKartu": request.POST["noBPJS"],
            "tglDaftar": request.POST["MRDTGL_DIAGNOSA"],
            "kdPoli": FMPKODEBPJS,
            "keluhan": request.POST["CPTD_KELUHANUTAMA"],
            "kdSadar": request.POST["TTVKESADARAN"],
            "sistole": int(request.POST["TTVTSISTOL"]),
            "diastole": int(request.POST["TTVDIASTOL"]),
            "beratBadan": int(request.POST["TTVBERAT_BADAN"]),
            "tinggiBadan": int(request.POST["TTVTINGGI_BADAN"]),
            "respRate": int(request.POST["TTVNAFAS"]),
            "heartRate": int(request.POST["TTVNADI"]),
            "lingkarPerut": int(request.POST["TTV_LINGKAR_PERUT"]),
            "terapi": "catatan",
            "kdStatusPulang": request.POST["StatusPulang"],
            "tglPulang": request.POST["MRDTGL_DIAGNOSA"],
            "kdDokter": FMDDOKTER_ID_BPJS,
            "kdDiag1": dataPenyakit,
            "kdDiag2": dataPenyakit2s,
            "kdDiag3": dataPenyakit3s,
            "kdPoliRujukInternal": None,
            "rujukLanjut": rujukLanjut,
            "kdTacc": int(kdTacc),
            "alasanTacc": alasanTacc,
        }

        try:
            # print('put')
            # print(url)
            res1 = bridgeBPJS(request, url, "put", payload)
            prints("---------------------------")
            prints(url)
            prints(payload)
            prints(res1)
            prints("---------------------------")

            if res1:
                datas1 = res1
                # print(datas1)

            # prints(datas1)
            if noKunjungan != "-":
                q = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET noKunjungan='{}' where MRDNO_TRANSAKSI='{}'".format(
                    noKunjungan, request.POST["notrans"]
                )
                # prints(q)
                Globals().executeQuery(q, [])
                # cursor.execute(q)

            # prints("here")

        except requests.exceptions.RequestException as e:
            prints(e)
            raise

    else:
        try:
            print("insert Kunjungan")
            print(noKunjungan)
            res = bridgeBPJS(request, url, "post", payload)
            prints(res)
            prints(res)
            prints("---------------------------")
            prints(url)
            prints(payload)
            prints("---------------------------")
            if res:
                datas = res
                print("datas")
                print(datas)
                print(url)
                print(payload)

                # prints(datas)
                if datas["metaData"]["code"] == 201:
                    # q = "INSERT INTO BPJS_SEP(FMNOTRANSAKSI,FMNOSEP,FMNO_KARTU,FMNAMA_PESERTA)VALUES('{}','{}','{}','{}')".format(request.POST['MRDNO_TRANSAKSI'],datas['response']['message'],request.POST['noBPJS'],request.POST['noBPJS'])
                    # # prints(q)
                    # cursor.execute(q)
                    noKunjungan = datas["response"][0]["message"]
                    q = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET noKunjungan='{}' where MRDNO_TRANSAKSI='{}'".format(
                        noKunjungan, request.POST["notrans"]
                    )
                    # cursor.execute(q)
                    Globals().executeQuery(q, [])
                else:
                    respon = []
                    # print('sini')
                    # print(datas)
                    # print(len(datas['response']))
                    if len(datas["response"]) == 0:
                        # print('sini')
                        msgE = "\n TETAPI TIDAK TERSAVE PCARE KARENA \n {}".format(
                            datas["metaData"]["message"]
                        )
                        restHasil = {"success": False, "messages": msgE}
                        return restHasil

                    if datas["metaData"]["code"] == 0:
                        msgE = (
                            "\n TETAPI TIDAK TERSAVE PCARE KARENA ICD10 BELUM DI ISI "
                        )
                        restHasil = {"success": False, "messages": msgE}
                    else:
                        msgE = "\n TETAPI TIDAK TERSAVE PCARE KARENA: "

                        if len(datas["response"]) > 0:
                            for x in datas["response"]:
                                msgE += "\n- {} {} ".format(x["field"], x["message"])
                        restHasil = {"success": False, "messages": msgE}

            else:
                prints("gagal post")
                prints(res)
        except requests.exceptions.RequestException as e:
            prints(e)
            raise

    qKunjunganKlinikBrd = (
        "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' ".format(
            request.POST["notrans"]
        )
    )
    dataKunjunganKlinikBrd = Globals().getDataQuery(qKunjunganKlinikBrd, [])
    if int(len(dataKunjunganKlinikBrd)) > 0:
        qKunjunganKlinikBrd = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING "
        qKunjunganKlinikBrd += " SET  opsiRujuk_rbs='%s', jenisRujukan_rbs='%s', rujukanSarana='%s', ppkRujukan='%s', ppkRujukanN='%s', spesialisRujukan='%s', spesialisRujukanN='%s', catatanRujukan='%s', tglRujukan='%s', kondisiKhususKategori='%s',noKunjungan='%s',kdTacc='%s',alasanTacc='%s',StatusPulang='%s',KD_CABANG='%s' "
        inputan = (
            request.POST["opsiRujuk_rbs"],
            request.POST["jenisRujukan_rbs"],
            request.POST["rujukanSarana"],
            request.POST["ppkRujukan"],
            request.POST["ppkRujukanN"],
            request.POST["spesialisRujukan"],
            request.POST["spesialisRujukanN"],
            request.POST["catatanRujukan"],
            request.POST["tglRujukan"],
            request.POST["kondisiKhususKategori"],
            noKunjungan,
            kdTacc,
            request.POST["alasanTacc"],
            request.POST["StatusPulang"],
            request.session["kdCabang"],
        )
        qKunjunganKlinikBrd = qKunjunganKlinikBrd % inputan
        qKunjunganKlinikBrd += " where MRDNO_TRANSAKSI='{}' ".format(
            request.POST["notrans"]
        )
        Globals().executeQuery(qKunjunganKlinikBrd, [])
    else:
        qKunjunganKlinikBrd = "INSERT INTO MR_KUNJUNGAN_KLINIK_BRIDGING(MRDNO_TRANSAKSI,opsiRujuk_rbs, jenisRujukan_rbs, rujukanSarana, ppkRujukan, ppkRujukanN, spesialisRujukan, spesialisRujukanN, catatanRujukan, tglRujukan, kondisiKhususKategori,noKunjungan,kdTacc,alasanTacc,StatusPulang,KD_CABANG) "
        qKunjunganKlinikBrd += "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') "
        inputan = (
            request.POST["notrans"],
            request.POST["opsiRujuk_rbs"],
            request.POST["jenisRujukan_rbs"],
            request.POST["rujukanSarana"],
            request.POST["ppkRujukan"],
            request.POST["ppkRujukanN"],
            request.POST["spesialisRujukan"],
            request.POST["spesialisRujukanN"],
            request.POST["catatanRujukan"],
            request.POST["tglRujukan"],
            request.POST["kondisiKhususKategori"],
            noKunjungan,
            kdTacc,
            request.POST["alasanTacc"],
            request.POST["StatusPulang"],
            request.session["kdCabang"],
        )
        qKunjunganKlinikBrd = qKunjunganKlinikBrd % inputan
        # cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
        Globals().executeQuery(qKunjunganKlinikBrd, [])
        # else:
        # 	# pprints("gagal")
        # 	# prints(datas)

    # return datas
    return restHasil


def convBulan(intbulan):
    bulan = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "Mei",
        "Jun",
        "Jul",
        "Ags",
        "Sep",
        "Okt",
        "Nov",
        "Des",
    ]
    intbulan = int(intbulan) - 1
    return bulan[intbulan]


def calculateAge(birthDate):
    today = date.today()
    age = (
        today.year
        - birthDate.year
        - ((today.month, today.day) < (birthDate.month, birthDate.day))
    )
    return age


def printSuratRujukanPCAREBPJS(request):
    kdApp = "095"

    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    kdCabang = cabang[0]["CABANG_ID"]

    # prints(data)
    code = None
    cursorKunjunganKlinikBrd = connection.cursor()
    qKunjunganKlinikBrd = "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' AND RESPONSE IS NOT NULL".format(
        request.GET["no_transaksi"]
    )
    cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
    dqKunjunganKlinikBrd = Globals().dictfetchall(cursorKunjunganKlinikBrd)
    # print(dqKunjunganKlinikBrd)
    # prints()
    if int(len(dqKunjunganKlinikBrd)) == 0:
        url_pcare = getattr(
            env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
        )
        url = url_pcare + "/kunjungan/rujukan/{}".format(request.GET["noRujukan"])
        data = bridgeBPJS(request, url, "get")
        code = data["metaData"]["code"]
    else:
        code = int(dqKunjunganKlinikBrd[0]["CODE"])
        data = json.loads(dqKunjunganKlinikBrd[0]["RESPONSE"])
    # code = 400

    # #print('code')
    # #print(code)

    cursorKunjunganKlinikBrd = connection.cursor()
    qKunjunganKlinikBrd = (
        "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' ".format(
            request.GET["no_transaksi"]
        )
    )
    cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
    dqKunjunganKlinikBrd = Globals().dictfetchall(cursorKunjunganKlinikBrd)

    if code == 200:
        cursorKunjunganKlinikBrd = connection.cursor()
        qKunjunganKlinikBrd = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET RESPONSE='{}',CODE='{}' where MRDNO_TRANSAKSI='{}' ".format(
            json.dumps(data), code, request.GET["no_transaksi"]
        )
        cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
        # print(qKunjunganKlinikBrd)

        user = Globals().input(request.GET, "user_id")
        no_trans = Globals().input(request.GET, "no_transaksi")
        noRujukan = Globals().input(request.GET, "noRujukan")
        jenisPrint = Globals().input(request.GET, "jenisPrint")
        logo_url = (
            os.path.abspath(os.path.dirname(__name__)) + "\static\img\logobpjs.png"
        )

        fktp = "{} ({})".format(
            data["response"]["ppk"]["nmPPK"], data["response"]["ppk"]["kdPPK"]
        )
        kabkota = "{} ({})".format(
            data["response"]["ppk"]["kc"]["dati"]["nmDati"],
            data["response"]["ppk"]["kc"]["dati"]["kdDati"],
        )
        nmRs = dqKunjunganKlinikBrd[0]["ppkRujukanN"]
        nmDiag = "{} ({})".format(
            data["response"]["diag1"]["nmDiag"], data["response"]["diag1"]["kdDiag"]
        )
        tglAkhirRujuk = data["response"]["tglAkhirRujuk"]
        tglAkhirRujuk = "%s %s %s" % (
            tglAkhirRujuk.split("-")[0],
            convBulan(tglAkhirRujuk.split("-")[1]),
            tglAkhirRujuk.split("-")[2],
        )

        tglLahir = data["response"]["tglLahir"]
        umur = "{} ".format(
            calculateAge(
                date(
                    int(tglLahir.split("-")[2]),
                    int(tglLahir.split("-")[1]),
                    int(tglLahir.split("-")[0]),
                )
            )
        )
        tglLahir = "%s %s %s" % (
            tglLahir.split("-")[0],
            convBulan(tglLahir.split("-")[1]),
            tglLahir.split("-")[2],
        )

        tglEstRujuk = data["response"]["tglEstRujuk"]
        if tglEstRujuk is None:
            tglEstRujuk = data["response"]["tglKunjungan"]
        tglEstRujuk = "%s %s %s" % (
            tglEstRujuk.split("-")[0],
            convBulan(tglEstRujuk.split("-")[1]),
            tglEstRujuk.split("-")[2],
        )
        catatan = ""
        if data["response"]["catatan"] is None:
            catatan = ""
        else:
            catatan = data["response"]["catatan"]

        pisa = "{} ".format(data["response"]["pisa"])
        pisa += "{} ".format(data["response"]["ketPisa"])
        sex = "{} ".format(data["response"]["sex"])
        catatanRujuk = ""
        if data["response"]["catatanRujuk"] is None:
            catatanRujuk = ""
        else:
            catatanRujuk = data["response"]["catatanRujuk"]

        salamsjw = "Salam sejawat,{}".format(tglEstRujuk)
        nmDokter = data["response"]["dokter"]["nmDokter"]
        nmPoli = data["response"]["poli"]["nmPoli"]
        if nmPoli is None:
            nmPoli = ""

        jadwalPcare = data["response"]["jadwal"]
        if jadwalPcare is None:
            jadwalPcare = ""
        inputan = {
            "nmKR": data["response"]["ppk"]["kc"]["kdKR"]["nmKR"],
            "nmKC": data["response"]["ppk"]["kc"]["nmKC"],
            "noRujukan": noRujukan,
            "fktp": fktp,
            "kabkota": kabkota,
            "nmPoli": nmPoli,
            "nmRs": nmRs,
            "nmPst": data["response"]["nmPst"],
            "nokaPst": data["response"]["nokaPst"],
            "nmDiag": nmDiag,
            "jadwal": jadwalPcare,
            "tglAkhirRujuk": tglAkhirRujuk,
            "catatan": catatan,
            "umur": umur,
            "tglLahir": tglLahir,
            "status": pisa,
            "sex": sex,
            "catatanRujuk": catatanRujuk,
            "tglEstRujuk": tglEstRujuk,
            "salamsjw": salamsjw,
            "nmDokter": nmDokter,
            "logo": logo_url,
        }
        # print(inputan)
        if jenisPrint == "1":
            pdf_file = Globals().generateReportDB(
                "EMR/SuratRujukanPCAREBPJS.jrxml",
                "SuratRujukanPCAREBPJS" + no_trans,
                user,
                inputan,
            )
        elif jenisPrint == "2":
            pdf_file = Globals().generateReportDB(
                "EMR/SuratRujukanKunjBalikPCAREBPJS.jrxml",
                "SuratRujukanKunjBalikPCAREBPJS" + no_trans,
                user,
                inputan,
            )
        else:
            pdf_file = Globals().generateReportDB(
                "EMR/SuratKunjunganPCAREBPJS.jrxml",
                "SuratKunjunganPCAREBPJS" + no_trans,
                user,
                inputan,
            )
        # Directory LOCAL
        # pdf_file = Globals().generateReportDB('EMR/BillRJ.jrxml','bill_rj_'+no_trans,user,{'NO_TRANSAKSI':no_trans,'NAMA_RS':nama_rs,'ALAMAT_RS':alamat_rs,'logo':'D:/MEDISIMED/simrs_klinik/static/img/logo-bina-sehat.jpg'})
        # pdf_file = Globals().generateReportDB('EMR/coba.jrxml','kd_antrian_'+no_trans,user)
        pdf_file = {"success": True, "message": pdf_file["pdf"]}
        json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")
    else:
        if code == 4123:
            msgError = "Silahkan Simpan data kunjungan terlebih dahulu!"
        elif code == 412:
            msgError = "{} ".format(data["response"][0]["message"])
        else:
            msgError = "Server BPJS sedang maintenance {}".format(
                data["metaData"]["message"]
            )
        pdf_file = {"success": False, "message": msgError}
        json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")


def printSuratKunjunganPCAREBPJS(request):
    cursor = connection.cursor()
    q = "select * from CABANG"
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)
    kdCabang = cabang[0]["CABANG_ID"]
    code = None
    tanggal = Globals().input(request.GET, "tanggal")
    noKartu = Globals().input(request.GET, "noKartu")

    cursorKunjunganKlinikBrd = connection.cursor()
    qKunjunganKlinikBrd = "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' AND RESPONSE_KUN_PESERTA IS NOT NULL".format(
        request.GET["no_transaksi"]
    )
    cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
    dqKunjunganKlinikBrd = Globals().dictfetchall(cursorKunjunganKlinikBrd)
    # prints(dqKunjunganKlinikBrd)
    # prints()
    if int(len(dqKunjunganKlinikBrd)) == 0:
        url_pcare = getattr(
            env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
        )
        url = url_pcare + "/kunjungan/peserta/{}".format(noKartu)
        datas = bridgeBPJS(request, url, "get")
        qKunjunganKlinikBrd = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET RESPONSE_KUN_PESERTA='{}' where MRDNO_TRANSAKSI='{}'".format(
            json.dumps(datas), request.GET["no_transaksi"]
        )
        cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
        code = datas["metaData"]["code"]
        # print('bridging')
    else:
        datas = json.loads(dqKunjunganKlinikBrd[0]["RESPONSE_KUN_PESERTA"])
        code = 4123
        # print('engga bridging')

    data = datas
    # #print('data')
    # #print(data)
    PCARE_STATUS = getattr(env, "PCARE_STATUS", "PROD")
    BPJS_USERPCARE1 = getattr(env, "BPJS_USERPCARE1", cabang[0]["userncc"])
    kdProvider = ""
    nmProvider = ""
    kdDiag = ""
    nmDiag = ""
    if code == 200:
        urutan = 0
        for dataRujukan in datas["response"]["list"]:
            PCARE_STATUS = getattr(env, "PCARE_STATUS", "PROD")
            if PCARE_STATUS == "DEV":
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"] is not None
                    and dataRujukan["providerPelayanan"]["kdProvider"]
                    == BPJS_USERPCARE1
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    data = dataRujukan
                    kdProvider = dataRujukan["providerPelayanan"]["kdProvider"]
                    nmProvider = dataRujukan["providerPelayanan"]["nmProvider"]
                    kdDiag = dataRujukan["diagnosa1"]["kdDiag"]
                    nmDiag = dataRujukan["diagnosa1"]["nmDiag"]
                    nmPoli = dataRujukan["poli"]["nmPoli"]

            else:
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"] is not None
                    and dataRujukan["providerPelayanan"]["kdProvider"]
                    == cabang[0]["userncc"]
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    data = dataRujukan
                    kdProvider = dataRujukan["providerPelayanan"]["kdProvider"]
                    nmProvider = dataRujukan["providerPelayanan"]["nmProvider"]
                    kdDiag = dataRujukan["diagnosa1"]["kdDiag"]
                    nmDiag = dataRujukan["diagnosa1"]["nmDiag"]
                    nmPoli = dataRujukan["poli"]["nmPoli"]
            urutan = urutan + 1
    else:
        cursor = connection.cursor()
        q = "select * from CABANG"
        cursor.execute(q)
        cabang = Globals().dictfetchall(cursor)
        data = datas
        urutan = 0
        for dataRujukan in datas["response"]["list"]:
            PCARE_STATUS = getattr(env, "PCARE_STATUS", "PROD")
            if PCARE_STATUS == "DEV":
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"] is not None
                    and dataRujukan["providerPelayanan"]["kdProvider"]
                    == BPJS_USERPCARE1
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    data = dataRujukan
                    kdProvider = dataRujukan["providerPelayanan"]["kdProvider"]
                    nmProvider = dataRujukan["providerPelayanan"]["nmProvider"]
                    kdDiag = dataRujukan["diagnosa1"]["kdDiag"]
                    nmDiag = dataRujukan["diagnosa1"]["nmDiag"]
                    nmPoli = dataRujukan["poli"]["nmPoli"]
                    catatan = dataRujukan["catatan"]

            else:
                if (
                    dataRujukan["providerPelayanan"]["kdProvider"] is not None
                    and dataRujukan["providerPelayanan"]["kdProvider"]
                    == cabang[0]["userncc"]
                    and dataRujukan["tglKunjungan"] == tanggal
                ):
                    data = dataRujukan
                    kdProvider = dataRujukan["providerPelayanan"]["kdProvider"]
                    nmProvider = dataRujukan["providerPelayanan"]["nmProvider"]
                    kdDiag = dataRujukan["diagnosa1"]["kdDiag"]
                    nmDiag = dataRujukan["diagnosa1"]["nmDiag"]
                    nmPoli = dataRujukan["poli"]["nmPoli"]
                    catatan = dataRujukan["catatan"]
            urutan = urutan + 1
    # prints(data)
    cursorKunjunganKlinikBrd = connection.cursor()
    qKunjunganKlinikBrd = (
        "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' ".format(
            request.GET["no_transaksi"]
        )
    )
    cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
    dqKunjunganKlinikBrd = Globals().dictfetchall(cursorKunjunganKlinikBrd)
    # prints(dqKunjunganKlinikBrd)
    # prints()
    if int(len(dqKunjunganKlinikBrd)) == 0:
        code = 4123
    # code = 400
    # code =data['metaData']['code']
    # prints(data)

    if int(len(data) > 0):
        user = Globals().input(request.GET, "user_id")
        no_trans = Globals().input(request.GET, "no_transaksi")
        noRujukan = Globals().input(request.GET, "noRujukan")
        jenisPrint = Globals().input(request.GET, "jenisPrint")
        logo_url = (
            os.path.abspath(os.path.dirname(__name__)) + "\static\img\logobpjs.png"
        )

        fktp = "{} ({})".format(nmProvider, kdProvider)
        kabkota = "{} ({})".format(cabang[0]["nmDati"], cabang[0]["kdDati"])
        nmRs = dqKunjunganKlinikBrd[0]["ppkRujukanN"]
        nmRs = "-"
        nmDiag = "{} ({})".format(nmDiag, kdDiag)
        tglAkhirRujuk = "-"
        # tglAkhirRujuk='%s %s %s' % (tglAkhirRujuk.split('-')[0],convBulan(tglAkhirRujuk.split('-')[1]),tglAkhirRujuk.split('-')[2])

        tglLahir = Globals().input(request.GET, "tgllahir")
        umur = "{} ".format(
            calculateAge(
                date(
                    int(tglLahir.split("-")[2]),
                    int(tglLahir.split("-")[1]),
                    int(tglLahir.split("-")[0]),
                )
            )
        )
        tglLahir = "%s %s %s" % (
            tglLahir.split("-")[0],
            convBulan(tglLahir.split("-")[1]),
            tglLahir.split("-")[2],
        )

        tglEstRujuk = tanggal
        tglEstRujuk = "%s %s %s" % (
            tglEstRujuk.split("-")[0],
            convBulan(tglEstRujuk.split("-")[1]),
            tglEstRujuk.split("-")[2],
        )
        catatan = ""

        cursorKunjunganKlinikBrd = connection.cursor()
        qKunjunganKlinikBrd = "SELECT CONVERT(varchar,TGL_LAHIR,5) as TGL_LAHIR,(CASE WHEN P.JENIS_KELAMIN='1' THEN 'L' ELSE 'P' END) as 'JK',P.NAMAPASIEN,P.KD_PASIEN,P.ALAMAT,P.NO_PENGENAL,P.TELEPON FROM PASIEN as P LEFT JOIN KUNJUNGANPASIEN as MD ON MD.KPKD_PASIEN=P.KD_PASIEN WHERE KPNO_TRANSAKSI='{}' ".format(
            request.GET["no_transaksi"]
        )
        cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
        dqKunjunganKlinikBrd = Globals().dictfetchall(cursorKunjunganKlinikBrd)

        pisa = "{} ".format(" 1 ")
        pisa += "{} ".format(" Utama/Tanggungan ")
        sex = "{} ".format(dqKunjunganKlinikBrd[0]["JK"])
        catatanRujuk = "-"
        # if data['response']['catatanRujuk'] is None:
        # 	catatanRujuk=""
        # else:
        # 	catatanRujuk=data['response']['catatanRujuk']
        # print(data)
        # print(data)
        cursor = connection.cursor()
        q = "select * from CABANG"
        cursor.execute(q)
        cabang = Globals().dictfetchall(cursor)

        salamsjw = "Salam sejawat,{}".format(tglEstRujuk)
        try:
            nmDokter = data["dokter"]["nmDokter"]
        except:
            for dataRujukan in data["response"]["list"]:
                nmDokter = dataRujukan["dokter"]["nmDokter"]

        # print(cabang)
        if cabang[0]["nmKC"] is not None:
            nmKc = cabang[0]["nmKC"]
        else:
            nmKc = ""

        if cabang[0]["nmKR"] is None:
            nmKR = ""
        else:
            nmKR = cabang[0]["nmKR"]
            kdProvider = dataRujukan["providerPelayanan"]["kdProvider"]
            nmProvider = dataRujukan["providerPelayanan"]["nmProvider"]
            kdDiag = dataRujukan["diagnosa1"]["kdDiag"]
            nmDiag = dataRujukan["diagnosa1"]["nmDiag"]
            nmPoli = dataRujukan["poli"]["nmPoli"]

        inputan = {
            "nmKR": nmKR,
            "nmKC": nmKc,
            "noRujukan": noRujukan,
            "fktp": fktp,
            "kabkota": kabkota,
            "nmPoli": nmPoli,
            "nmRs": nmRs,
            "nmPst": dqKunjunganKlinikBrd[0]["NAMAPASIEN"],
            "nokaPst": noKartu,
            "nmDiag": nmDiag,
            "jadwal": "-",
            "tglAkhirRujuk": tglAkhirRujuk,
            "catatan": catatan,
            "umur": umur,
            "tglLahir": tglLahir,
            "status": pisa,
            "sex": sex,
            "catatanRujuk": catatanRujuk,
            "tglEstRujuk": tglEstRujuk,
            "salamsjw": salamsjw,
            "nmDokter": nmDokter,
            "logo": logo_url,
        }

        if jenisPrint == "1":
            pdf_file = Globals().generateReportDB(
                "EMR/SuratRujukanPCAREBPJS.jrxml",
                "SuratRujukanPCAREBPJS" + no_trans,
                user,
                inputan,
            )
        elif jenisPrint == "2":
            pdf_file = Globals().generateReportDB(
                "EMR/SuratRujukanKunjBalikPCAREBPJS.jrxml",
                "SuratRujukanKunjBalikPCAREBPJS" + no_trans,
                user,
                inputan,
            )
        else:
            pdf_file = Globals().generateReportDB(
                "EMR/SuratKunjunganPCAREBPJS.jrxml",
                "SuratKunjunganPCAREBPJS" + no_trans,
                user,
                inputan,
            )
        # Directory LOCAL
        # pdf_file = Globals().generateReportDB('EMR/BillRJ.jrxml','bill_rj_'+no_trans,user,{'NO_TRANSAKSI':no_trans,'NAMA_RS':nama_rs,'ALAMAT_RS':alamat_rs,'logo':'D:/MEDISIMED/simrs_klinik/static/img/logo-bina-sehat.jpg'})
        # pdf_file = Globals().generateReportDB('EMR/coba.jrxml','kd_antrian_'+no_trans,user)
        pdf_file = {"success": True, "message": pdf_file["pdf"]}
        json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")
    else:
        if code == 4123:
            msgError = "Silahkan Simpan data kunjungan terlebih dahulu!"
        # elif code==412:
        # 	msgError='{} '.format(data['response'][0]['message'])
        else:
            msgError = "Server BPJS sedang maintenance {}".format(
                data["metaData"]["message"]
            )
        pdf_file = {"success": False, "message": msgError}
        json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")


def printSuratSPPPCAREBPJS(request):
    kdApp = "095"

    # cursor = connection.cursor()
    # q = "select * from CABANG"
    # cursor.execute(q)
    # cabang = Globals().dictfetchall(cursor)
    # kdCabang=cabang[0]['CABANG_ID']
    noKartu = Globals().input(request.GET, "noKartu")
    tanggal = Globals().input(request.GET, "tanggal")

    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/kunjungan/peserta/{}".format(noKartu)
    datas = bridgeBPJS(request, url, "get")
    # code=datas['metaData']['code']

    if datas["metaData"]["code"] == 200:
        for dataRujukan in datas["response"]["list"]:
            if (
                dataRujukan["providerPelayanan"]["kdProvider"] == cabang[0]["userncc"]
                and dataRujukan["tglKunjungan"] == tanggal
            ):
                data = dataRujukan
    else:
        data = datas
    # prints(data)
    code = None

    # prints(dqKunjunganKlinikBrd)
    # prints()

    # code =datas['metaData']['code']
    # prints(data)
    if int(len(data) > 0):
        user = Globals().input(request.GET, "user_id")
        no_trans = Globals().input(request.GET, "no_transaksi")
        noRujukan = Globals().input(request.GET, "noRujukan")
        logo_url = (
            os.path.abspath(os.path.dirname(__name__)) + "\static\img\logobpjs.png"
        )

        cursorKunjunganKlinikBrd = connection.cursor()
        qKunjunganKlinikBrd = "SELECT CONVERT(varchar,P.TGL_LAHIR,5) as TGL_LAHIR,(CASE WHEN P.JENIS_KELAMIN='1' THEN 'L' ELSE 'P' END) as 'JK',P.NAMAPASIEN,P.KD_PASIEN,P.ALAMAT,P.NO_PENGENAL,P.TELEPON FROM PASIEN as P LEFT JOIN KUNJUNGANPASIEN as MD ON MD.KPKD_PASIEN=P.KD_PASIEN WHERE KPNO_TRANSAKSI='{}' ".format(
            request.GET["no_transaksi"]
        )
        cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
        dqKunjunganKlinikBrd = Globals().dictfetchall(cursorKunjunganKlinikBrd)

        fktp = "{} ({})".format(
            data["providerPelayanan"]["nmProvider"],
            data["providerPelayanan"]["kdProvider"],
        )
        nmPPK = "{} - {}".format(
            data["providerPelayanan"]["kdProvider"],
            data["providerPelayanan"]["nmProvider"],
        )
        tglLahir = dqKunjunganKlinikBrd[0]["TGL_LAHIR"]
        umur = "{} Tahun".format(
            calculateAge(
                date(
                    int(tglLahir.split("-")[2]),
                    int(tglLahir.split("-")[1]),
                    int(tglLahir.split("-")[0]),
                )
            )
        )
        tglLahir = "%s %s %s" % (
            tglLahir.split("-")[0],
            convBulan(tglLahir.split("-")[1]),
            tglLahir.split("-")[2],
        )

        tglEstRujuk = data["tglEstRujuk"]
        tglEstRujuk = "%s %s %s" % (
            tglEstRujuk.split("-")[0],
            convBulan(tglEstRujuk.split("-")[1]),
            tglEstRujuk.split("-")[2],
        )
        catatan = ""
        if data["catatan"] is None:
            catatan = ""
        else:
            catatan = data["catatan"]

        pisa = "{} ".format(" ")
        pisa += "{} ".format(" Penanggung/Utama")
        sex = "{} ".format(dqKunjunganKlinikBrd[0]["JK"])
        catatanRujuk = ""
        # if data['response']['catatanRujuk'] is None:
        # 	catatanRujuk=""
        # else:
        # catatanRujuk=data['response']['catatanRujuk']
        catatanRujuk = "-"

        salamsjw = "Salam sejawat,{}".format(tglEstRujuk)
        nmDokter = data["dokter"]["nmDokter"]

        # prints(dqKunjunganKlinikBrd)
        noKTP = dqKunjunganKlinikBrd[0]["NO_PENGENAL"]
        noHP = dqKunjunganKlinikBrd[0]["TELEPON"]
        noKdPasien = dqKunjunganKlinikBrd[0]["KD_PASIEN"]
        alamat = dqKunjunganKlinikBrd[0]["ALAMAT"]

        jenisPelayanan = data["tkp"]["nmTkp"]
        subReport = (
            os.path.abspath(os.path.dirname(__name__)) + "\jrxml\ListNonKapitasi.jasper"
        )
        inputan = {
            "noRujukan": noRujukan,
            "nmPst": dqKunjunganKlinikBrd[0]["NAMAPASIEN"],
            "nokaPst": noKartu,
            "nmPPK": nmPPK,
            "umur": umur,
            "tglLahir": tglLahir,
            "sex": sex,
            "tglEstRujuk": tglEstRujuk,
            "no_trans": no_trans,
            "noKTP": noKTP,
            "noHP": noHP,
            "noKdPasien": noKdPasien,
            "alamat": alamat,
            "jenisPelayanan": jenisPelayanan,
            "logo": logo_url,
            "subReport": subReport,
        }

        pdf_file = Globals().generateReportDB(
            "EMR/SuratSPPPCAREBPJS.jrxml", "SuratSPPPCAREBPJS" + no_trans, user, inputan
        )
        pdf_file = {"success": True, "message": pdf_file["pdf"]}
        json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")
    else:
        if code == 4123:
            msgError = "Silahkan Simpan data kunjungan terlebih dahulu!"
        elif code == 412:
            msgError = "{} ".format(data["response"][0]["message"])
        else:
            msgError = "Server BPJS sedang maintenance {}".format(
                data["metaData"]["message"]
            )
        pdf_file = {"success": False, "message": msgError}
        json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")


def prints(msg):
    debug = getattr(env, "DEBUG_PCARE", False)
    # if debug:
    # print(msg)


def bridgeBPJS(request, url, method, payload={}):
    cursor = connection.cursor()
    kdApp = "095"

    cursor = connection.cursor()
    q = "select * from CABANG WHERE CABANG_ID='{}'".format(request.session["kdCabang"])
    cursor.execute(q)
    cabang = Globals().dictfetchall(cursor)

    # consid = getattr(env, 'BPJS_CONSID', 'DB')
    # secret = getattr(env, 'BPJS_SECRET', 'DB')
    # userpcare = getattr(env, 'BPJS_USERPCARE', 'DB')
    # passpcare = getattr(env, 'BPJS_PASSPCARE', 'DB')
    # BPJS_URL_PCARE = getattr(env, 'BPJS_URL_PCARE', 'DB')
    # BPJS_USERKEY = getattr(env, 'BPJS_USERKEY', 'DB')

    consid = cabang[0]["consid"]
    secret = cabang[0]["secret"]
    userpcare = cabang[0]["userncc"]
    passpcare = cabang[0]["passwordncc"]
    BPJS_URL_PCARE = getattr(env, "BPJS_URL_PCARE", "DB")
    BPJS_USERKEY = cabang[0]["bpjs_userkey"]

    tStamp = int(datetime.today().timestamp())
    tStamp = str(tStamp)
    message = consid + "&" + tStamp
    signature = hmac.new(
        bytes(secret, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha256
    ).digest()
    encodeSignature = base64.b64encode(signature)
    authorization = base64.b64encode(
        bytes(userpcare + ":" + passpcare + ":" + kdApp, "UTF-8")
    )

    headers = {
        "X-cons-id": consid,
        "X-timestamp": tStamp,
        "X-signature": encodeSignature.decode("UTF-8"),
        "Content-Type": "Application/JSON",
        "X-authorization": "Basic " + authorization.decode("UTF-8"),
        "Accept": "*/*",
        "user_key": "" + BPJS_USERKEY,
    }
    # #print(headers)
    # #print(url)
    if not payload:
        payload = 0
    else:
        payload = json.dumps(payload, cls=DjangoJSONEncoder)

    if method == "post":
        if payload == 0:
            res = requests.post(url, headers=headers).json()
        else:
            url_pcare = getattr(
                env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id"
            )
            urlKunj = url_pcare + "/kunjungan"
            if url != urlKunj:
                headers = {
                    "X-cons-id": consid,
                    "X-timestamp": tStamp,
                    "X-signature": encodeSignature.decode("UTF-8"),
                    "X-Authorization": "Basic " + authorization.decode("UTF-8"),
                    "Accept": "*/*",
                    "user_key": "" + BPJS_USERKEY,
                }
                # print('non url kunjungan post')
            else:
                headers = {
                    "X-cons-id": consid,
                    "X-timestamp": tStamp,
                    "X-signature": encodeSignature.decode("UTF-8"),
                    "Content-Type": "text/plain",
                    "X-Authorization": "Basic " + authorization.decode("UTF-8"),
                    "Accept": "*/*",
                    "user_key": "" + BPJS_USERKEY,
                }
                # print('url kunjungan post')
            res = requests.post(url, data=payload, headers=headers).json()
            # #print(res)
    elif method == "put":
        if payload == 0:
            res = requests.put(url, headers=headers).json()
        else:
            headers = {
                "X-cons-id": consid,
                "X-timestamp": tStamp,
                "X-signature": encodeSignature.decode("UTF-8"),
                "X-Authorization": "Basic " + authorization.decode("UTF-8"),
                "Accept": "*/*",
                "user_key": "" + BPJS_USERKEY,
            }
            # #print(url)
            # #print(headers)
            # #print(payload)
            # #print(requests.post(url   , data=payload, headers=headers).text)
            res = requests.put(url, data=payload, headers=headers).json()
            # #print(res)
    else:
        if payload == 0:
            res = requests.get(url, headers=headers).json()
        else:
            res = requests.get(url, data=payload, headers=headers).json()

    # print(url)
    # print(payload)
    # print(headers)
    # print('res')
    # print(res)
    # #print(json.loads(decrypt('{}{}{}'.format(consid,secret,'1660878392'),"h5d29n\/5Bd2mYLwK4kA4J\/vO+pGcGfzv569X\/JSGDfgrPXI9YI1GJFaLasMS8S5TgXwd\/nuXvRECvfHUNkCAier1XxZBO06lDdwYm1PJ546hB8\/ilsgzd+k4uZyvAnFeYOtb0+Q8PXvr5Fg0+oXGg9nq3kFnQG4+1RbQSGOKgw8Wf\/dpgRcZBQ9CWQ2IoXuO3skhtQg+Zo5IkbKjxRXlp1uEQP4cLdCdFfY7hJoAcxocBp\/xpbdUH5lqeAgg4QR6UuakRO2lgrzUd5ns7YTFn4aqlTwg4akQGagt3c7sB5\/13QTqAxW3dF8sEgPJaIzKFOBKzwAbNNfLN7amk2eVFvySWI1jvFPLsbKu3bfT1gk=")))
    try:
        resnew = {
            "response": json.loads(
                decrypt("{}{}{}".format(consid, secret, tStamp), res["response"])
            ),
            "metaData": res["metaData"],
        }
    except:
        # print('error')
        resnew = res
    # print(resnew)
    return resnew


def decrypt(key, txt_enc):
    x = lzstring.LZString()

    key_hash = hashlib.sha256(key.encode("utf-8")).digest()

    mode = AES.MODE_CBC

    # decrypt
    decryptor = AES.new(key_hash[0:32], mode, IV=key_hash[0:16])
    plain = decryptor.decrypt(base64.b64decode(txt_enc))
    decompress = x.decompressFromEncodedURIComponent(plain.decode("utf-8"))

    return decompress
