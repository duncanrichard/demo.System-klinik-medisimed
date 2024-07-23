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


def emr_perawat(request):
    if Globals().isLogin(request):
        user_priv = request.session["user_id"]
        user_privelege = request.session["user_priv"]
        user_name = request.session["user_name"]
        navbars = Globals().getNavbars(user_priv, "IMMODERMA", "emr_perawat")
        menubars = Globals().getMenubars(user_priv, "IMMODERMA", "emr_perawat", "0")
        menubarsChild = Globals().getMenubars(
            user_priv, "IMMODERMA", "emr_perawat", "1"
        )
        menubarCount = len(menubars)
        response = render(
            request,
            "emr_new/emr_perawat/base.html",
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
                "Status_DCG": request.session["Status_DCG"],
                "bridge_pcare": request.session["bridge_pcare"],
                "jns_cabang": request.session["jns_cabang"],
            },
        )
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def getPasienRJ(request):
    if "q" in request.GET:
        q = request.GET["q"]

        if q == "pasienRJ":
            if getattr(env, "MODE_URUT_BYNOTRANS", 0) == 1:
                q1 = "select IIF(EMR.CPTPCREATED_AT IS NULL,'0','1') AS STATUS_EMR,RIGHT(a.KPNO_TRANSAKSI,3) AS Row_Number,a.KPNO_TRANSAKSI,convert(varchar, KPTGL_PERIKSA, 105) as KPTGL_PERIKSA,KPKD_POLY,KPKD_DOKTER,c.FMDDOKTERN,a.KPKD_PASIEN as NORM,KD_CUSTOMER,d.NAME as PENANGGUNG,"
            else:
                q1 = "select ROW_NUMBER() OVER(ORDER BY a.KPNO_TRANSAKSI) AS Row_Number,a.KPNO_TRANSAKSI,convert(varchar, KPTGL_PERIKSA, 105) as KPTGL_PERIKSA,KPKD_POLY,KPKD_DOKTER,c.FMDDOKTERN,a.KPKD_PASIEN as NORM,KD_CUSTOMER,d.NAME as PENANGGUNG,"
            q2 = " b.NAMAPASIEN,convert(varchar, tgl_lahir, 105) as TGLLAHIR,convert(varchar, tgl_lahir, 101) as  tgl_lahir2,ALAMAT, JENIS_KELAMIN,e.KODEASSESMENT,e.FMPKLINIKN,ISNULL((SELECT TOP 1 FHRSTATUS FROM ERESEPDOKTER WHERE FHRBUKTI_ID=a.KPNO_TRANSAKSI),0) as Status from KUNJUNGANPASIEN a "
            q2 += " ,pasien b,Dokter c,CUSTOMER d,Poliklinik e where"
            q3 = " a.KPKD_PASIEN=b.KD_PASIEN  and c.FMDDOKTER_ID=a.KPKD_DOKTER and a.KD_CUSTOMER=d.CUSID and a.KPKD_POLY=E.FMPKLINIK_ID and"
            # RSUD REMBANG KECUALI OK
            q3 += " E.FMPPENUNJANG2<>'1' AND "
            # ---------------------------------
            if getattr(env, "MODE_URUT_BYNOTRANS", 0) == 1:
                q4 = " convert(datetime, KPTGL_PERIKSA, 105)>=convert(datetime, '{}', 105)  and convert(datetime, KPTGL_PERIKSA, 105)<=convert(datetime, '{}', 105) order by RIGHT(a.KPNO_TRANSAKSI,3) DESC".format(
                    request.GET["tglAwal"], request.GET["tglAkhir"]
                )
            else:
                q4 = " convert(datetime, KPTGL_PERIKSA, 105)>= '{}'  and convert(datetime, KPTGL_PERIKSA, 105)<= '{}' order by KPKD_POLY,KPTGL_PERIKSA,b.NAMAPASIEN DESC".format(
                    request.GET["tglAwal"], request.GET["tglAkhir"]
                )
            query = "{}{}{}{}".format(q1, q2, q3, q4)
            result = Globals().getDataQuery(query)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            # select a.UPDATERS, CONVERT(varchar,UPDATERS,8) as seli from KUNJUNGANPASIEN a where a.KD_CABANG='007' and   left(CONVERT(varchar,UPDATERS,8),2)<12
        elif q == "listPasienTgl":
            sortShiftBy = request.GET["sortShiftBy"]
            query = " SELECT IIF(EMR.MRPNO_TRANSAKSI IS NULL,'0','1') AS STATUS_EMRDR, IIF(EMRDR.CPTDCREATED_AT IS NULL,'0','1') AS STATUS_EMR,"
            query += " RTRIM(LTRIM(PSN.NO_ASURANSI)) as NO_ASURANSI,PSN.NAMAPASIEN, TGL_LAHIR as TGL_LAHIR,A.KPKD_PASIEN as NORM,PSN.ALAMAT,PSN.NO_PENGENAL,PSN.PKD_PASIEN_FHIR "
            query += " ,PL.FMPKLINIK_ID,FMPKLINIKN,PL.KODEASSESMENT,DR.FMDDOKTERN,DR.SSFHIR_KD_DOKTER,CST.NAME as CUSTOMER"
            query += " ,A.*,CONVERT(varchar,A.KPTGL_PERIKSA,105) as TGL_INDO,PSN.TELEPON,PSN.KD_PEKERJAAN as PEKERJAAN,convert(varchar, PSN.tgl_lahir, 101) as  tgl_lahir2,IIF(PSN.JENIS_KELAMIN=1,'L','P') as JENIS_KELAMIN"
            query += " ,ALER.ALPALERGI FROM KUNJUNGANPASIEN A"
            query += " LEFT JOIN PASIEN PSN ON A.KPKD_PASIEN=PSN.KD_PASIEN"
            # query += " LEFT JOIN PEKERJAAN PKJ ON PSN.KD_PEKERJAAN=PKJ.KD_PEKERJAAN "
            query += " LEFT JOIN POLIKLINIK PL ON A.KPKD_POLY=PL.FMPKLINIK_ID"
            query += " LEFT JOIN CUSTOMER CST ON A.KD_CUSTOMER=CST.CUSID"
            query += " INNER JOIN DOKTER DR ON A.KPKD_DOKTER=DR.FMDDOKTER_ID"
            query += " LEFT JOIN MR_PENYAKIT EMR ON A.KPNO_TRANSAKSI=EMR.MRPNO_TRANSAKSI AND EMR.MRPSTAT_DIAG IN(SELECT A.MSDIAGNOSAID FROM STATUSDIAGNOSA A WHERE A.MSDIAGUTAMA=1) "
            query += " LEFT JOIN EMRRJ_CPPT_DOKTER EMRDR ON A.KPNO_TRANSAKSI=EMRDR.CPTDNO_TRANSAKSI_RJ"
            query += " LEFT JOIN ALERGI_PASIEN ALER ON A.KPKD_PASIEN=ALER.ALPKD_PASIEN"
            query += " WHERE A.KPTGL_PERIKSA>='{}' AND A.KPTGL_PERIKSA<='{}' AND  LEFT(A.KD_CABANG,3)='{}'".format(
                request.GET["tglAwal"],
                request.GET["tglAkhir"],
                request.session["kdCabang"],
            )
            if sortShiftBy == "P":
                query += " and left(CONVERT(varchar,A.UPDATERS,8),2)<=12"
            elif sortShiftBy == "S":
                query += " and left(CONVERT(varchar,A.UPDATERS,8),2)>12"
            query += (
                " ORDER BY STATUS_EMR ASC, LEN(A.KD_ANTRIAN) DESC,A.KD_ANTRIAN DESC"
            )
            # print(query)
            result = Globals().getDataQuery(query)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "dataPickerKasus":
            query = "select MSKASUSID,MSKASUSNAMA from STATUSKASUS"
            result = Globals().getDataQuery(query)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "dataPickerDiagnosa":
            query = "select MSDIAGNOSAID,MSDIAGNOSANAMA FROM STATUSDIAGNOSA"
            result = Globals().getDataQuery(query)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "chartPasienRujukan":
            q = "select * from CABANG"
            result = Globals().getDataQuery(q)
            cabang = Globals().dictfetchall(cursor)
            kdCabang = cabang[0]["CABANG_ID"]
            q1 = " SELECT count(*) as jumPasien FROM  PASIEN_RUJUKAN,KUNJUNGANPASIEN "
            q1 += " WHERE  PASIEN_RUJUKAN.FRPNOTRANSAKSIKJ=KUNJUNGANPASIEN.KPNO_TRANSAKSI and FRPTGL>=convert(datetime, '{}', 105)  and FRPTGL<=convert(datetime, '{}', 105)".format(
                request.GET["tglAwal"], request.GET["tglAkhir"]
            )
            if kdCabang != "19":
                q1 += "  AND FRPNOANTRIDOKTER IS NOT NULL "

            if request.GET["pencarian"] == "1":
                if len(request.GET["kdDokter"].strip()) > 2:
                    q1 += " AND FRPDOKTER_ID='{}' ".format(request.GET["kdDokter"])
                else:
                    q1 += " AND FRPUNIT='{}'".format(request.GET["kdPoli"])

            else:
                if len(request.GET["kdPoli"].strip()) > 2:
                    q1 += " AND FRPUNIT='{}'".format(request.GET["kdPoli"])
                else:
                    q1 += " AND FRPDOKTER_ID='{}' ".format(request.GET["kdDokter"])

            query = "{}".format(q1)
            # prints("jumpasien")
            # ##print(query)

            result = Globals().getDataQuery(query)
            result = []
            result = Globals().dictfetchall(cursor)
            jumlahPasien = result[0]["jumPasien"]

            q1 = " SELECT count(*) as jumPasienPeriksa FROM  PASIEN_RUJUKAN,KUNJUNGANPASIEN "
            q1 += " WHERE PASIEN_RUJUKAN.FRPNOTRANSAKSIKJ=KUNJUNGANPASIEN.KPNO_TRANSAKSI and FRPSTATUS=2 and  FRPTGL>=convert(datetime, '{}', 105)  and FRPTGL<=convert(datetime, '{}', 105) ".format(
                request.GET["tglAwal"], request.GET["tglAkhir"]
            )
            if kdCabang != "19":
                q1 += "  AND FRPNOANTRIDOKTER IS NOT NULL "
            if request.GET["pencarian"] == "1":
                q1 += " AND FRPDOKTER_ID='{}' ".format(request.GET["kdDokter"])
            else:
                q1 += " AND FRPUNIT='{}'".format(request.GET["kdPoli"])
            query = "{}".format(q1)
            # prints("jumPasienPeriksa")

            # ##print(query)

            result = Globals().getDataQuery(query)
            result = []
            result = Globals().dictfetchall(cursor)

            q1 = " SELECT count(*) as jumPasienPeriksa FROM  PASIEN_RUJUKAN,KUNJUNGANPASIEN "
            q1 += " WHERE PASIEN_RUJUKAN.FRPNOTRANSAKSIKJ=KUNJUNGANPASIEN.KPNO_TRANSAKSI and FRPSTATUS=3 and  FRPTGL>=convert(datetime, '{}', 105)  and FRPTGL<=convert(datetime, '{}', 105) ".format(
                request.GET["tglAwal"], request.GET["tglAkhir"]
            )
            if kdCabang != "19":
                q1 += "  AND FRPNOANTRIDOKTER IS NOT NULL "
            if request.GET["pencarian"] == "1":
                q1 += " AND FRPDOKTER_ID='{}' ".format(request.GET["kdDokter"])
            else:
                q1 += " AND FRPUNIT='{}'".format(request.GET["kdPoli"])
            query = "{}".format(q1)

            # prints("jumPasienPeriksa")

            # ##print(query)

            result = Globals().getDataQuery(query)
            resultprw = []
            resultprw = Globals().dictfetchall(cursor)

            jumPasienPeriksa = result[0]["jumPasienPeriksa"]
            jumlahPasienDokter = int(result[0]["jumPasienPeriksa"])
            jumlahPasienPerawat = int(resultprw[0]["jumPasienPeriksa"])
            jumPasienPeriksaB = jumlahPasien - (
                jumlahPasienDokter + jumlahPasienPerawat
            )
            result = [
                {
                    "jumlahPasien": jumlahPasien,
                    "jumlahPasienDokter": jumlahPasienDokter,
                    "jumlahPasienPerawat": jumlahPasienPerawat,
                    "jumPasienPeriksaB": jumPasienPeriksaB,
                }
            ]

            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "chartPasienRujukanDokter":
            q = "select * from CABANG"
            result = Globals().getDataQuery(q)
            cabang = Globals().dictfetchall(cursor)
            kdCabang = cabang[0]["CABANG_ID"]
            # jumpasien all
            query = " SELECT count(*) as jumPasien FROM  PASIEN_RUJUKAN A "
            query += (
                " LEFT JOIN KUNJUNGANPASIEN B ON A.FRPNOTRANSAKSIKJ=B.KPNO_TRANSAKSI "
            )
            query += " INNER JOIN POLIKLINIK P ON A.FRPUNIT=P.FMPKLINIK_ID "
            query += " WHERE FRPTGL>=convert(datetime, '{}', 105)  ".format(
                request.GET["tglAwal"]
            )
            query += " and FRPTGL<=convert(datetime, '{}', 105)".format(
                request.GET["tglAkhir"]
            )
            query += " AND FRPDOKTER_ID='{}' AND P.FMPPENUNJANG2<>'1' AND A.FRPSTATUS2='3'".format(
                request.GET["kdDokter"]
            )
            # if kdCabang!="19":
            # 	q1+="  AND FRPNOANTRIDOKTER IS NOT NULL "

            result = Globals().getDataQuery(query)
            result = []
            result = Globals().dictfetchall(cursor)
            # ##print(query)
            jumlahPasien = result[0]["jumPasien"]

            # jumpasien dokter sudah di isi assesment
            query = " SELECT count(*) as jumPasienDokter FROM  PASIEN_RUJUKAN A "
            query += (
                " LEFT JOIN KUNJUNGANPASIEN B ON A.FRPNOTRANSAKSIKJ=B.KPNO_TRANSAKSI "
            )
            query += " INNER JOIN POLIKLINIK P ON A.FRPUNIT=P.FMPKLINIK_ID "
            query += " WHERE FRPTGL>=convert(datetime, '{}', 105)  ".format(
                request.GET["tglAwal"]
            )
            query += " and FRPTGL<=convert(datetime, '{}', 105)".format(
                request.GET["tglAkhir"]
            )
            query += " AND FRPDOKTER_ID='{}' AND P.FMPPENUNJANG2<>'1' AND A.FRPSTATUS='2' AND A.FRPSTATUS2='3'".format(
                request.GET["kdDokter"]
            )
            # prints("jumPasienPeriksa")

            # ##print(query)

            result = Globals().getDataQuery(query)
            result = []
            result = Globals().dictfetchall(cursor)
            jumPasienDokter = result[0]["jumPasienDokter"]

            result = Globals().getDataQuery(query)
            resultprw = []
            resultprw = Globals().dictfetchall(cursor)

            # jumPasienPeriksa=result[0]['jumPasienPeriksa']
            # jumlahPasienDokter=int(result[0]['jumPasienPeriksa'])
            # jumlahPasienPerawat=int(resultprw[0]['jumPasienPeriksa'])
            jumPasienDokterBelumDiPeriksa = jumlahPasien - jumPasienDokter
            result = [
                {
                    "jumlahPasien": jumlahPasien,
                    "jumlahPasienDokter": jumPasienDokter,
                    "jumPasienDokterBelumDiPeriksa": jumPasienDokterBelumDiPeriksa,
                }
            ]

            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data

        elif q == "chartPasienRujukanPerawat":
            kdCabang = request.session["kdCabang"]
            # jumpasien all
            query = " SELECT count(*) as jumPasien FROM  KUNJUNGANPASIEN B  "
            query += " INNER JOIN POLIKLINIK P ON B.KPKD_POLY=P.FMPKLINIK_ID "
            query += " WHERE convert(datetime, KPTGL_PERIKSA, 105)>= '{}'  and convert(datetime, KPTGL_PERIKSA, 105)<= '{}' AND P.FMPPENUNJANG2<>'1' AND b.KD_CABANG='{}'  ".format(
                request.GET["tglAwal"],
                request.GET["tglAkhir"],
                kdCabang,
            )

            result = Globals().getDataQuery(query)
            jumlahPasien = result[0]["jumPasien"]
            # jumpasien perawat sudah di isi assesment
            query = " SELECT count(*) as jumPasienPerawat FROM  KUNJUNGANPASIEN B  "
            query += " INNER JOIN POLIKLINIK P ON B.KPKD_POLY=P.FMPKLINIK_ID "
            query += " INNER JOIN EMRRJ_CPPT_DOKTER EMRDR ON B.KPNO_TRANSAKSI=EMRDR.CPTDNO_TRANSAKSI_RJ "
            query += " WHERE convert(datetime, KPTGL_PERIKSA, 105)>= '{}'  and convert(datetime, KPTGL_PERIKSA, 105)<= '{}' AND P.FMPPENUNJANG2<>'1' AND b.KD_CABANG='{}' ".format(
                request.GET["tglAwal"],
                request.GET["tglAkhir"],
                kdCabang,
            )
            result = Globals().getDataQuery(query)
            jumPasienPerawat = result[0]["jumPasienPerawat"]
            jumPasienPerawatBelumDiPeriksa = jumlahPasien - jumPasienPerawat

            # jumpasien dokter sudah di isi kode icd 10
            query = " SELECT count(*) as jumPasienDokter FROM  KUNJUNGANPASIEN B  "
            query += " INNER JOIN POLIKLINIK P ON B.KPKD_POLY=P.FMPKLINIK_ID "
            query += " INNER JOIN MR_PENYAKIT EMR ON B.KPNO_TRANSAKSI=EMR.MRPNO_TRANSAKSI AND EMR.MRPSTAT_DIAG IN(SELECT A.MSDIAGNOSAID FROM STATUSDIAGNOSA A WHERE A.MSDIAGUTAMA=1) "
            query += " INNER JOIN EMRRJ_CPPT_DOKTER EMRDR ON B.KPNO_TRANSAKSI=EMRDR.CPTDNO_TRANSAKSI_RJ "
            query += " WHERE convert(datetime, KPTGL_PERIKSA, 105)>= '{}'  and convert(datetime, KPTGL_PERIKSA, 105)<= '{}' AND P.FMPPENUNJANG2<>'1' AND b.KD_CABANG='{}' ".format(
                request.GET["tglAwal"],
                request.GET["tglAkhir"],
                kdCabang,
            )
            result = Globals().getDataQuery(query)
            jumPasienDokter = result[0]["jumPasienDokter"]
            jumPasienDokterBelumDiPeriksa = jumlahPasien - jumPasienDokter

            result = [
                {
                    "jumlahPasien": jumlahPasien,
                    "jumPasienPerawat": jumPasienPerawat,
                    "jumPasienPerawatBelumDiPeriksa": jumPasienPerawatBelumDiPeriksa,
                    "jumPasienDokter": jumPasienDokter,
                    "jumPasienDokterBelumDiPeriksa": jumPasienDokterBelumDiPeriksa,
                }
            ]

            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "detailDaftarResep":
            query = "Select a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, "
            query += "FDRSIGNA, FDRBUKTI_ID, b.PFKODE, PFKETERANGAN,c.HJUAL,(a.FDRQTY*c.Hjual) As Total  "
            query += "from ERESEPPAKETD a,ERESEPPAKET b,Barang c  "
            query += "where a.FDRBUKTI_ID=b.PFKODE and A.FDRBRG_ID=c.barangc   "
            query += "and b.PFKODE='{}' ORDER BY FDRRESEP ".format(
                request.GET["PFKODE"]
            )
            result = Globals().getDataQuery(query)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
    else:
        edit = "not permited"
    return HttpResponse(edit, content_type="application/json")

def getDataKunjunganPasien(request):

    query = " SELECT IIF(EMR.MRPNO_TRANSAKSI IS NULL,'0','1') AS STATUS_EMRDR, IIF(EMRDR.CPTDCREATED_AT IS NULL,'0','1') AS STATUS_EMR,"
    query += " RTRIM(LTRIM(PSN.NO_ASURANSI)) as NO_ASURANSI,PSN.NAMAPASIEN, TGL_LAHIR as TGL_LAHIR,A.KPKD_PASIEN as NORM,PSN.ALAMAT,PSN.NO_PENGENAL,PSN.PKD_PASIEN_FHIR "
    query += " ,PL.FMPKLINIK_ID,FMPKLINIKN,PL.KODEASSESMENT,DR.FMDDOKTERN,DR.SSFHIR_KD_DOKTER,CST.NAME as CUSTOMER"
    query += " ,A.*,CONVERT(varchar,A.KPTGL_PERIKSA,105) as TGL_INDO,PSN.TELEPON,PSN.KD_PEKERJAAN as PEKERJAAN,convert(varchar, PSN.tgl_lahir, 101) as  tgl_lahir2,IIF(PSN.JENIS_KELAMIN=1,'L','P') as JENIS_KELAMIN"
    query += " ,ALER.ALPALERGI FROM KUNJUNGANPASIEN A"
    query += " LEFT JOIN PASIEN PSN ON A.KPKD_PASIEN=PSN.KD_PASIEN"
    query += " LEFT JOIN POLIKLINIK PL ON A.KPKD_POLY=PL.FMPKLINIK_ID"
    query += " LEFT JOIN CUSTOMER CST ON A.KD_CUSTOMER=CST.CUSID"
    query += " INNER JOIN DOKTER DR ON A.KPKD_DOKTER=DR.FMDDOKTER_ID"
    query += " LEFT JOIN MR_PENYAKIT EMR ON A.KPNO_TRANSAKSI=EMR.MRPNO_TRANSAKSI AND EMR.MRPSTAT_DIAG IN(SELECT A.MSDIAGNOSAID FROM STATUSDIAGNOSA A WHERE A.MSDIAGUTAMA=1) "
    query += " LEFT JOIN EMRRJ_CPPT_DOKTER EMRDR ON A.KPNO_TRANSAKSI=EMRDR.CPTDNO_TRANSAKSI_RJ"
    query += " LEFT JOIN ALERGI_PASIEN ALER ON A.KPKD_PASIEN=ALER.ALPKD_PASIEN"
    query += " WHERE A.KPKD_PASIEN='{}'".format(
        request.GET["PasienId"],
    )
    query += (
        " ORDER BY STATUS_EMR ASC, LEN(A.KD_ANTRIAN) DESC,A.KD_ANTRIAN DESC"
    )
    # print(query)
    result = Globals().getDataQuery(query)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def panggilAntrianPendaftaran(request):
    no_antri = request.POST["no_antri"]
    channel = request.POST["channel"]
    userrs = request.session["user_id"]
    cabang = request.session["kdCabang"]
    tanggaljam = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tanggal = datetime.now().strftime("%Y-%m-%d")
    kdCabang = request.session["kdCabang"]
    result2 = []
    # Cari kode Bpjsnya dulu
    q = "select NO_BPJS,KdPoli,no_kartu from poliklinik_antri where no=%s and Tanggal=CONVERT(DATE, GETDATE()) and CABANG=%s "
    result = Globals().getDataQuery(q, [no_antri, kdCabang], "antrian")
    if len(result) != 0:
        q = "select FMPKLINIK_ID,a.FMPKLINIKN,a.FMPKODEBPJS from POLIKLINIK a where a.FMPKLINIK_ID=%s "
        result2 = Globals().getDataQuery(q, [result[0]["KdPoli"]])

    result3 = {
        "data1": result,
        "data2": result2,
    }

    q = "UPDATE pendaftaran SET Status_Pen = 'True', Sound = 'False',display='False' ,Channel = %s where NO= %s AND Tanggal = CONVERT(DATE, GETDATE()) AND CABANG=%s"
    # print(q,[channel, NO,kdCabang])
    Globals().executeQuery(q, [channel, no_antri, kdCabang], "antrian")

    # qdata = "SELECT * FROM pendaftaran where NO = %s AND Tanggal = CONVERT(DATE, GETDATE()) AND CABANG=%s"
    # cursor2.execute(qdata, [NO,kdCabang])
    # result = Globals().dictfetchall(cursor2)

    # json_data = json.dumps(result[0], cls=DjangoJSONEncoder)

    data = {
        "NO": request.POST["no_antri"],
        "id_poli": request.POST["id_poli"],
        "KdPoli": request.POST["id_poli"],
        "nama_poli": request.POST["nama_poli"],
        "id_dokter": request.POST["id_dokter"],
        "kode_dokter": request.POST["kode_dokter"],
        "nama_dokter": request.POST["nama_dokter"],
        "Pendaftaran": request.POST["Pendaftaran"],
        "tanggal": tanggal,
        "jam": tanggaljam,
        "cabang": request.session["kdCabang"],
        "no_antri": request.POST["no_antri"],
        "Channel": request.POST["channel"],
        "antrianJenis": request.POST["antrianJenis"],
    }

    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    url = getattr(env, "URL_SOCKET", "http://localhost:3000") + "/playCS"
    resp = requests.post(
        url, data=json_data, headers={"Content-type": "application/json"}
    )

    json_data = json.dumps(result3, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getPanggilAntrian(request):
    no_antri = request.POST["no_antri"]
    channel = request.POST["channel"]
    userrs = request.session["user_id"]
    cabang = request.session["kdCabang"]
    tanggaljam = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tanggal = datetime.now().strftime("%Y-%m-%d")

    q = "UPDATE poliklinik_antri SET Updateantrian= ISNULL(convert (int, Updateantrian), 0 )+1 ,Status_Pen = 'True', Sound = 'False',display='False' ,Channel =  %s where NO= %s AND Tanggal = CONVERT(DATE, GETDATE()) AND CABANG = %s "
    Globals().executeQuery(q, [channel, no_antri, cabang], "antrian")
    data = {
        "NO": request.POST["no_antri"],
        "id_poli": request.POST["id_poli"],
        "KdPoli": request.POST["id_poli"],
        "nama_poli": request.POST["nama_poli"],
        "id_dokter": request.POST["id_dokter"],
        "kode_dokter": request.POST["kode_dokter"],
        "nama_dokter": request.POST["nama_dokter"],
        "Pendaftaran": request.POST["Pendaftaran"],
        "tanggal": tanggal,
        "jam": tanggaljam,
        "cabang": request.session["kdCabang"],
        "no_antri": request.POST["no_antri"],
        "Channel": request.POST["channel"],
        "antrianJenis": request.POST["antrianJenis"],
    }

    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    if getattr(env, "mode", "DATABASE") == "SOCKET":
        url = getattr(env, "URL_SOCKET", "http://localhost:3000") + "/playPOLI"
        resp = requests.post(
            url, data=json_data, headers={"Content-type": "application/json"}
        )

    return HttpResponse(json_data, content_type="application/json")


def cekNoka(request):
    # -------
    nomor = request.GET["nomor"]
    kdCabang = request.session["kdCabang"]
    BPJS_USERPCARE = request.session["BPJS_USERPCARE"]
    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/peserta/noka/" + nomor
    method = "get"
    data = Globals().bridgeBPJS(url, method, kdCabang)
    # print (data)
    if data["metaData"]["code"] == 401:
        data = {"status": "gagal", "pesan": data["response"]["message"], "next": 0}
    if data["metaData"]["code"] == 412:
        data = {"status": "gagal", "pesan": data["response"]["message"], "next": 0}
    elif data["metaData"]["code"] != 200:
        data = {
            "status": "gagal",
            "pesan": "Nomor Tidak Valid \n Cek Kembali",
            "next": 0,
        }
    elif data["response"]["aktif"] == False:
        data = {
            "status": "gagal",
            "pesan": 'Nomor Tidak Aktif Karena "' + data["response"]["ketAktif"] + '"',
            "next": 0,
        }
    elif (
        (data["response"]["kdProviderPst"]["kdProvider"] != BPJS_USERPCARE)
        and (getattr(env, "NO_FASKES") == "0")
        and (
            data["response"]["kdProviderPst"]["kdProvider"]
            not in getattr(env, "WHITELIST_FASKES", [])
        )
    ):
        data = {
            "status": "gagal",
            "pesan": "Nomor BPJS Tidak Terdaftar Di Faskes Tingkat I Ini \n Silahkan Daftar Pasien Umum",
            "next": 1,
        }

    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def SP_ALERGI(request):
    kd_pasien = request.POST["kd_pasien"]
    alergi = request.POST["alergi"]
    user_rs = request.POST["user_rs"]
    update_rs = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # CEK KODE
    q = "select A.ALPKD_PASIEN,A.ALPALERGI from ALERGI_PASIEN A WHERE  ALPKD_PASIEN = %s"
    result = Globals().getDataSP(q, [kd_pasien])
    if len(result) == 0:
        q = "INSERT INTO   ALERGI_PASIEN (ALPKD_PASIEN,ALPALERGI,ALPCREATED_AT,ALPUPDATED_AT) VALUES (%s, %s, %s, %s)"
        Globals().executeQuery(q, [kd_pasien, alergi, update_rs, update_rs])
        json_data = json.dumps(
            {"pesan": "Berhasil Di Tambahkan"}, cls=DjangoJSONEncoder
        )

    else:
        q = "UPDATE   ALERGI_PASIEN  SET   ALPALERGI = %s,ALPCREATED_AT= %s,ALPUPDATED_AT= %s WHERE  ALPKD_PASIEN = %s"
        Globals().executeQuery(q, [alergi, update_rs, update_rs, kd_pasien])
        json_data = json.dumps({"pesan": "Berhasil Di Perbarui"}, cls=DjangoJSONEncoder)

    return HttpResponse(json_data, content_type="application/json")


def OpenDiagnosaGigiVisual(request):
    # -------
    NO_TRANSAKSI = request.GET["NO_TRANSAKSI"]
    kdCabang = request.session["kdCabang"]
    q = "SELECT MDG_NO_TRANSAKSI,MDG_VISUAL_1,MDG_VISUAL_2,MDG_VISUAL_3,MDG_VISUAL_4,MDG_VISUAL_5 FROM MR_DIAGNOSA_GIGI_VISUAL WHERE MDG_NO_TRANSAKSI= %s "
    result = Globals().getDataQuery(q, [NO_TRANSAKSI])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def generateResepTXT(request):
    # -------
    noTrans = request.GET["noTrans"]
    edit = {}
    edit["success"] = True
    edit["message"] = getEresepTxT(request.GET["noTrans"])
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    edit = json_data
    return HttpResponse(edit, content_type="application/json")


def getEresepTxT(noTrans):
    pengobatan = ""
    result = []
    query = " SELECT a.FDRRESEP, a.FDRBRG_ID, a.FDRBRG_ID2, a.FDRBRGN, a.FDRSATUAN, CAST(a.FDRQTY AS int) AS FDRQTY, CONVERT(varchar(MAX), a.FDRQTYOUT) AS FDRQTYOUT, CONVERT(varchar(MAX), a.FDRDOSIS) AS FDRDOSIS"
    query += " , a.FDRSIGNAF, CONVERT(varchar(MAX), a.FDRDOSIS2) AS FDRDOSIS2, a.FDRSIGNAS, a.FDRSIGNAW, a.FDRSIGNA, a.FDRBUKTI_ID, ISNULL(CASE WHEN a.FDRSTATUS = 0 THEN ' da ' +(SELECT NAME_BRG FROM BARANG WHERE BARANGC = a.FDRBRG_ID2 and BRANCH=LEFT(b.FHRBUKTI_ID,3)) + ' ' ELSE '' END, '') AS FDRBRGDA"
    query += " , b.FHRNO_TRANSAKSI, b.FHRBUKTI_ID, CONVERT(varchar, b.FHRDATE, 20) AS FHRDATE, b.FHRUSER, CONVERT(varchar, b.FHRUPDATE, 20)  AS FHRUPDATE, b.FHRSTATUS, CONVERT(varchar(MAX), c.HJUAL) AS HJUAL, CONVERT(varchar(MAX), a.FDRQTY * c.HJUAL) AS Total"
    query += " FROM ERESEPDOKTERD AS a"
    query += " LEFT JOIN ERESEPDOKTER AS b ON a.FDRBUKTI_ID = b.FHRNO_TRANSAKSI "
    query += " LEFT JOIN BARANG AS c ON a.FDRBRG_ID = c.BARANGC AND c.BRANCH=LEFT(b.FHRBUKTI_ID,3)"
    query += " WHERE (b.FHRBUKTI_ID = '{}') AND (a.FDRSTATUS2 IS NOT NULL) AND (a.FDRRACIK_ID = 'NULL')".format(
        noTrans
    )
    query += " ORDER BY a.FDRRESEP"
    dataResepNonRacik = Globals().getDataQuery(query, [])
    for isidataResepNonRacik in dataResepNonRacik:
        # pengobatan += "\n %s %s %s No. %s;" % (
        pengobatan += "%s %s %s No. %s;" % (
            isidataResepNonRacik["FDRBRGN"],
            isidataResepNonRacik["FDRSIGNA"],
            isidataResepNonRacik["FDRBRGDA"],
            isidataResepNonRacik["FDRQTY"],
        )
    no = 1

    queryAwal = " SELECT DISTINCT a.FDRRACIK_ID"
    queryAwal += " FROM ERESEPDOKTERD AS a"
    queryAwal += " INNER JOIN ERESEPDOKTER AS b ON a.FDRBUKTI_ID = b.FHRNO_TRANSAKSI"
    queryAwal += " INNER JOIN BARANG AS c ON a.FDRBRG_ID = c.BARANGC"
    queryAwal += " WHERE (b.FHRBUKTI_ID = %s) AND (a.FDRRACIK_ID <> 'NULL')"
    dataResepRacikH = Globals().getDataQuery(queryAwal, [noTrans])

    if int(len(dataResepRacikH)) > 0:
        pengobatan += "\n #Racikan: "
    for isidataResepRacikH in dataResepRacikH:
        q1 = "Select a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
        q2 = " ISNULL(CASE WHEN a.FDRSTATUS=0 THEN "
        q2 += "' da '"
        q2 += "+(SELECT NAME_BRG FROM BARANG WHERE BARANGC=a.FDRBRG_ID2 and BRANCH=LEFT(b.FHRBUKTI_ID,3))+' '"
        q2 += " ELSE '' END,'') as FDRBRGDA,"
        q2 += " (SELECT TOP 1 CONVERT(varchar(max),FERDKEBQTY2)+' '+FERRACIKDQTYJENIS FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}' AND FERRACIKDBRG_ID=FDRBRG_ID AND FERRACIKDQTY=FDRQTY) as FDRKEB,".format(
            isidataResepRacikH["FDRRACIK_ID"]
        )
        q2 += " b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,c.HJUAL,(a.FDRQTY*c.Hjual) As Total "
        q3 = " from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
        q4 = " where a.FDRSTATUS2 IS NOT NULL and a.FDRRACIK_ID<>'NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and c.BRANCH=LEFT(b.FHRBUKTI_ID,3) and b.FHRBUKTI_ID='{}' AND a.FDRRACIK_ID='{}' ORDER BY FDRRESEP".format(
            noTrans, isidataResepRacikH["FDRRACIK_ID"]
        )
        query = "{}{}{}{}".format(q1, q2, q3, q4)

        dataResepRacikD = Globals().getDataQuery(query, [])
        for isidataResepRacikD in dataResepRacikD:
            if no == 1:
                pengobatan += "\n %s (%s) %s " % (
                    isidataResepRacikD["FDRBRGN"],
                    isidataResepRacikD["FDRKEB"],
                    isidataResepRacikD["FDRBRGDA"],
                )
            else:
                pengobatan += "\n %s (%s) %s" % (
                    isidataResepRacikD["FDRBRGN"],
                    isidataResepRacikD["FDRKEB"],
                    isidataResepRacikD["FDRBRGDA"],
                )
            if no == int(len(dataResepRacikD)):
                pengobatan += "\n %s" % (isidataResepRacikD["FDRSIGNA"])
            no += 1

    query = "SELECT ISNULL(FHRRESEPTEXT,'') as FHRRESEPTEXT,FHRNO_TRANSAKSI  FROM ERESEPDOKTER where FHRBUKTI_ID='{}'".format(
        noTrans
    )
    # print(query)
    dataResepManual = Globals().getDataQuery(query, [])
    # print(dataResepManual)
    # pengobatan += "\n"
    if int(len(pengobatan)) > 5:
        dataResepManual = ""
    pengobatan += ""

    for isidataResepManual in dataResepManual:
        pengobatan += "%s " % (isidataResepManual["FHRRESEPTEXT"])

    return pengobatan


def getIdDataDiagnosa(request):
    kode = request.GET["kode"]
    q = " select KD_PENYAKIT,PENYAKIT,NOTES  "
    q += " from penyakit where KD_PENYAKIT = %s order by KD_PENYAKIT "
    result = Globals().getDataQuery(q, [kode])
    if len(result) == 0:
        data = {"status": "gagal", "pesen": "data tidak ditemukan", "data": None}
    else:
        data = {"status": "ok", "pesen": "data ditemukan", "data": result[0]}
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getDataDiagnosa(request):
    nama = "%" + request.GET["nama"] + "%"
    if nama == "nullnone0":
        result = []
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")
    else:
        q = " select TOP 100 KD_PENYAKIT,PENYAKIT,NOTES  "
        q += " from penyakit where KD_PENYAKIT = %s OR PENYAKIT LIKE %s OR NOTES LIKE %s order by KD_PENYAKIT "
        result = Globals().getDataQuery(q, [nama, nama, nama])

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def findStatusKasus(request):
    if "id" in request.GET:
        q = "SELECT * FROM STATUSKASUS WHERE MSKASUSID = %s ORDER BY MSKASUSID ASC "
        result = Globals().getDataQuery(q, [request.GET["id"]])
    else:
        q = "SELECT * FROM STATUSKASUS ORDER BY MSKASUSID ASC "
        result = Globals().getDataQuery(q)

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def findStatusDiagnosaKlaim(request):
    q = "SELECT * FROM STATUSDIAGNOSA WHERE MSDIAGUTAMA > 0 ORDER BY MSDIAGUTAMA ASC "
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def findStatusDiagnosaKlaimAwal(request):
    q = (
        "SELECT * FROM STATUSDIAGNOSA WHERE MSDIAGNOSAID ="
        + getattr(env, "REKAMMEDIS_MSDIAGNOSAID_DIAGNOSA_AWAL", "0")
        + " ORDER BY MSDIAGUTAMA ASC "
    )
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def Openpenyakit(request):
    # -------
    NO_TRANSAKSI = request.GET["NO_TRANSAKSI"]
    q = "Select a.MRPNO_TRANSAKSI,MRPURUT_MASUK, convert(varchar, MRPTGL_MASUK, 105) as MRPTGL_MASUK,MRPKD_PENYAKIT,b.PENYAKIT,a.MRPSTAT_DIAG,c.MSDIAGNOSANAMA,a.MRPKASUS,d.MSKASUSNAMA, ISNULL(a.MRPIMUNKE, 0 ) as MRPIMUNKE,ISNULL(b.STATUS_IMUN, 0 ) as STATUS_IMUN "
    q += " FROM  MR_PENYAKIT a,PENYAKIT b,STATUSDIAGNOSA c,STATUSKASUS d "
    q += " where a.MRPKD_PENYAKIT=b.kd_penyakit and a.MRPSTAT_DIAG=c.MSDIAGNOSAID and a.MRPKASUS=d.MSKASUSID "
    q += " and MRPNO_TRANSAKSI=%s order by MRPURUT_MASUK "
    result = Globals().getDataQuery(q, [NO_TRANSAKSI])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def cekDiagnosaTACC(diagnosa, request):
    kdCabang = request.session["kdCabang"]
    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/diagnosa/{}/0/100".format(diagnosa)
    method = "get"

    method = "get"
    datas = Globals().bridgeBPJS(url, method, kdCabang)
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


def cek_diagnosa_bpjs(request):
    # -------
    kd_penyakit = json.loads(request.POST["kd_penyakit"])
    # parameter1 ='1'
    # parameter2 = '100'
    kdCabang = request.session["kdCabang"]
    response = {
        "success": False,
    }

    ListPenyakit = json.loads(request.POST["kd_penyakit"])
    for value in ListPenyakit:
        diagnosa = value
        # print(diagnosa)
        cekStatusDiagnosaTACC = cekDiagnosaTACC(diagnosa, request)
        # return 0
        if cekStatusDiagnosaTACC == "1":
            response = {
                "success": True,
            }
    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def save_assesment(request):
    try:
        q = "SET NOCOUNT ON;"
        q += " EXEC EMRJ_AUD_CPPT_PERAWAT "
        q += " %s ,"  # @CPTDNO_TRANSAKSI_RJ varchar(60) NULL,
        q += " %s ,"  # @CPTDNO_TRANSAKSI varchar(60) NULL,
        q += " %s ,"  # @CPTDUSER_ID varchar(20) NULL,
        q += " %s ,"  # @CPTDUSER_TYPE varchar(20) NULL,
        q += " %s ,"  # @CPTDUSER_NAME varchar(20) NULL,
        q += " %s ,"  # @KD_PASIEN varchar(10) ,
        q += " %s ,"  # @KD_CABANG varchar(50),
        q += " %s ,"  # @CPTD_KELUHANUTAMA	text,
        q += " %s ,"  # @CPTD_RIWAYAT_SKG	text,
        q += " %s ,"  # @TTVTSISTOL int  NULL,
        q += " %s ,"  # @TTVDIASTOL int  NULL,
        q += " %s ,"  # @TTVNADI int  NULL,
        q += " %s ,"  # @TTVNAFAS int  NULL,
        q += " %s ,"  # @TTVSUHU float  NULL,
        q += " %s ,"  # @TTVBERAT_BADAN float  NULL,
        q += " %s ,"  # @TTVTINGGI_BADAN float  NULL,
        q += " %s ,"  # @TTVO2 int  NULL,
        q += " %s ,"  # @TTVKESADARAN varchar (150) NULL,
        q += " %s ,"  # @TTV_LINGKAR_KEPALA float  NULL,
        q += " %s ,"  # @CPTP_KESADARAN,
        q += " %s ,"  # @CPTP_NAFAS,
        q += " %s ,"  # @CPTP_RESIKO,
        q += " %s ,"  # @CPTP_NYERI_DADA,
        q += " %s ,"  # @CPTP_NILAI_NYERI,
        q += " %s ,"  # @CPTP_LOKASI_NYERI,
        q += " %s ,"  # @CPTP_BATUK,
        q += " %s ,"  # @CPTP_GIZI,
        q += " %s ,"  # @TTVGCS_E,
        q += " %s ,"  # @TTVGCS_M,
        q += " %s ,"  # @TTVGCS_V,
        q += " %s ;"  # @STATUS_AUD nvarchar(5) = 'A'

        proc_param = [
            Globals().input(
                request.POST, "noTrans"
            ),  # @CPTDNO_TRANSAKSI_RJ varchar(20) NULL,
            Globals().input(
                request.POST, "no_transaksi_cppt"
            ),  # @CPTDNO_TRANSAKSI varchar(20) NULL,
            request.session["user_id"],  # @CPTDUSER_ID varchar(20) NULL,
            request.session["user_priv"],
            request.session["user_name"],
            Globals().input(request.POST, "no_rm"),  # @KD_PASIEN varchar(10) ,
            request.session["kdCabang"],  # @KD_CABANG varchar(50) NULL,
            Globals().input(
                request.POST, "CPTD_KELUHANUTAMA"
            ),  # @CPTD_KELUHANUTAMA	text NULL,
            Globals().input(
                request.POST, "CPTD_RIWAYAT_SKG"
            ),  # @CPTD_RIWAYAT_SKG	text NULL,
            (
                None
                if Globals().input(request.POST, "TTVTSISTOL") == ""
                else Globals().input(request.POST, "TTVTSISTOL")
            ),  # @TTVTSISTOL int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVDIASTOL") == ""
                else Globals().input(request.POST, "TTVDIASTOL")
            ),  # @TTVDIASTOL int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVNADI") == ""
                else Globals().input(request.POST, "TTVNADI")
            ),  # @TTVNADI int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVNAFAS") == ""
                else Globals().input(request.POST, "TTVNAFAS")
            ),  # @TTVNAFAS int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVSUHU") == ""
                else Globals().input(request.POST, "TTVSUHU")
            ),  # @TTVSUHU float  NULL,
            (
                None
                if Globals().input(request.POST, "TTVBERAT_BADAN") == ""
                else Globals().input(request.POST, "TTVBERAT_BADAN")
            ),  # @TTVBERAT_BADAN float  NULL,
            (
                None
                if Globals().input(request.POST, "TTVTINGGI_BADAN") == ""
                else Globals().input(request.POST, "TTVTINGGI_BADAN")
            ),  # @TTVTINGGI_BADAN float  NULL,
            (
                None
                if Globals().input(request.POST, "TTVO2") == ""
                else Globals().input(request.POST, "TTVO2")
            ),  # @TTVO2 int  NULL,
            (
                None
                if Globals().input(request.POST, "TTV_LINGKAR_KEPALA") == ""
                else Globals().input(request.POST, "TTV_LINGKAR_KEPALA")
            ),  # @TTV_LINGKAR_KEPALA float  NULL,
            (
                None
                if Globals().input(request.POST, "TTV_LINGKAR_PERUT") == ""
                else Globals().input(request.POST, "TTV_LINGKAR_PERUT")
            ),  # @TTV_LINGKAR_PERUT float NULL,
            Globals().input(request.POST, "CPTP_KESADARAN"),
            Globals().input(request.POST, "CPTP_NAFAS"),
            Globals().input(request.POST, "CPTP_RESIKO"),
            Globals().input(request.POST, "CPTP_NYERI_DADA"),
            Globals().input(request.POST, "CPTP_NILAI_NYERI"),
            Globals().input(request.POST, "CPTP_LOKASI_NYERI"),
            Globals().input(request.POST, "CPTP_BATUK"),
            Globals().input(request.POST, "CPTP_GIZI"),
            (
                None
                if Globals().input(request.POST, "TTVGCS_E") == ""
                else Globals().input(request.POST, "TTVGCS_E")
            ),
            (
                None
                if Globals().input(request.POST, "TTVGCS_M") == ""
                else Globals().input(request.POST, "TTVGCS_M")
            ),
            (
                None
                if Globals().input(request.POST, "TTVGCS_V") == ""
                else Globals().input(request.POST, "TTVGCS_V")
            ),
            "A",
        ]
        # print(q % proc_param)
        # print(q % tuple(proc_param))
        result_set = Globals().getDataSP(q, proc_param)
        json_data = json.dumps(result_set, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print("coba")


def save_cuti(request):
    try:
        q = "SET NOCOUNT ON;"
        q += " EXEC EMRJ_AUD_CPPT_CUTI "
        q += " %s ,"  # @no_transaksi_cppt varchar(60) NULL,
        q += " %s ,"  # @TTV_LAMA_CUTI varchar(20) NULL,
        q += " %s ,"  # @TTV_TGL_CUTI varchar(20) NULL,
        q += " %s "  # @TTV_KET_CUTI varchar(20) NULL,

        proc_param = [
            Globals().input(request.POST, "no_transaksi_cppt"),
            Globals().input(request.POST, "TTV_LAMA_CUTI"),
            Globals().input(request.POST, "TTV_TGL_CUTI"),
            Globals().input(request.POST, "TTV_KET_CUTI"),
        ]
        result_set = Globals().getDataSP(q, proc_param)
        json_data = json.dumps(result_set, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print("coba")


def save_cppt(request):
    # DETAIL ListDiagnosa
    MRPURUT_MASUK = json.loads(request.POST["MRPURUT_MASUK"])
    MRPKD_PENYAKIT = json.loads(request.POST["MRPKD_PENYAKIT"])
    MRPSTAT_DIAG = json.loads(request.POST["MRPSTAT_DIAG"])
    MRPKASUS = json.loads(request.POST["MRPKASUS"])

    if request.method == "POST":
        edit = ""
        i = 1
        upload_paths = []

        q = "SET NOCOUNT ON;"
        q += " DECLARE @ListDiagnosa ListMR_PENYAKIT; "
        q += " DECLARE @ListTindakan ListMR_TINDAKAN2; "
        ListTindakan = json.loads(request.POST["tindakan"])
        i = 0
        for x in MRPKD_PENYAKIT:
            q += "INSERT INTO @ListDiagnosa (MRPURUT_MASUK, MRPKD_PENYAKIT,MRPSTAT_DIAG,MRPKASUS) VALUES ("
            q += "'" + MRPURUT_MASUK[i] + "',"
            q += "'" + MRPKD_PENYAKIT[i] + "',"
            q += "'" + MRPSTAT_DIAG[i] + "',"
            q += "'" + MRPKASUS[i] + "');"
            i += 1
        for value in ListTindakan:
            q += " INSERT INTO @ListTindakan (MRTURUT_MASUK, MRTKD_TINDAKAN,MRTKD_PASIEN) "
            q += (
                " VALUES ("
                + str(i)
                + " , '"
                + value["MRTKD_TINDAKAN"]
                + "', '"
                + Globals().input(request.POST, "no_rm")
                + "');"
            )
            i += 1
        q += " EXEC EMRJ_AUD_CPPT_DOKTER "
        q += " %s ,"  # @CPTDNO_TRANSAKSI_RJ varchar(60) NULL,
        q += " %s ,"  # @CPTDNO_TRANSAKSI varchar(60) NULL,
        q += " %s ,"  # @CPTDUSER_ID varchar(20) NULL,
        q += " %s ,"  # @CPTDUSER_TYPE varchar(20) NULL,
        q += " %s ,"  # @CPTDUSER_NAME varchar(20) NULL,
        q += " %s ,"  # @CPTD_S text NULL,
        q += " %s ,"  # @CPTD_O text NULL,
        q += " %s ,"  # @CPTD_A text NULL,
        q += " %s ,"  # @CPTD_P text NULL,
        q += " @ListDiagnosa ,"  # @List_Penyakit ListMR_PENYAKIT READONLY,
        q += " @ListTindakan ,"  # @List_TINDAKAN ListMR_TINDAKAN2 READONLY,
        q += " %s ,"  # @KD_PASIEN varchar(10) ,
        q += " %s ,"  # @KD_CABANG varchar(50),
        q += " %s ,"  # @CPTD_ANAMNESA	varchar(100),
        q += " %s ,"  # @CPTD_ANAMNESA_KET1	varchar(250),
        q += " %s ,"  # @CPTD_ANAMNESA_KET2	varchar(250),
        q += " %s ,"  # @CPTD_KELUHANUTAMA	text,
        q += " %s ,"  # @CPTD_RIWAYAT_SKG	text,
        q += " %s ,"  # @TTVTSISTOL int  NULL,
        q += " %s ,"  # @TTVDIASTOL int  NULL,
        q += " %s ,"  # @TTVNADI int  NULL,
        q += " %s ,"  # @TTVNAFAS int  NULL,
        q += " %s ,"  # @TTVSUHU float  NULL,
        q += " %s ,"  # @TTVBERAT_BADAN float  NULL,
        q += " %s ,"  # @TTVTINGGI_BADAN float  NULL,
        q += " %s ,"  # @TTVO2 int  NULL,
        q += " %s ,"  # @TTVKESADARAN varchar (150) NULL,
        q += " %s ,"  # @TTV_LINGKAR_KEPALA float  NULL,
        q += " %s ,"  # @TTV_HPHT datetime  NULL,
        q += " %s ,"  # @TTV_HPL datetime  NULL,
        q += " %s ,"  # @TTV_LINGKAR_PERUT float NULL,
        q += " %s ,"  # @TTV_UH varhcar(50) NULL,
        q += " %s ,"  # @Program_DCG int NULL,
        q += " %s ,"  # @Program_Rujukan int NULL,
        q += " %s ;"  # @STATUS_AUD nvarchar(5) = 'A'

        proc_param = [
            Globals().input(
                request.POST, "noTrans"
            ),  # @CPTDNO_TRANSAKSI_RJ varchar(20) NULL,
            Globals().input(
                request.POST, "no_transaksi_cppt"
            ),  # @CPTDNO_TRANSAKSI varchar(20) NULL,
            request.session["user_id"],  # @CPTDUSER_ID varchar(20) NULL,
            "DOKTER",  # @CPTDUSER_TYPE varchar(20) NULL,
            request.session["user_name"],  # @CPTDUSER_NAME varchar(20) NULL,
            Globals().input(request.POST, "S_dokter"),  # @CPTD_S text NULL,
            Globals().input(request.POST, "O_dokter"),  # @CPTD_O text NULL,
            Globals().input(request.POST, "A_dokter"),  # @CPTD_A text NULL,
            Globals().input(request.POST, "P_dokter"),  # @CPTD_P text NULL,
            # @List_Penyakit ListMR_PENYAKIT READONLY,
            # @List_TINDAKAN ListMR_TINDAKAN2 READONLY,
            Globals().input(request.POST, "no_rm"),  # @KD_PASIEN varchar(10) ,
            request.session["kdCabang"],  # @KD_CABANG varchar(50) NULL,
            Globals().input(
                request.POST, "CPTD_ANAMNESA"
            ),  # @CPTD_ANAMNESA	varchar(100) NULL,
            Globals().input(
                request.POST, "CPTD_ANAMNESA_KET1"
            ),  # @CPTD_ANAMNESA_KET1	varchar(250) NULL,
            Globals().input(
                request.POST, "CPTD_ANAMNESA_KET2"
            ),  # @CPTD_ANAMNESA_KET2	varchar(250) NULL,
            Globals().input(
                request.POST, "CPTD_KELUHANUTAMA"
            ),  # @CPTD_KELUHANUTAMA	text NULL,
            Globals().input(
                request.POST, "CPTD_RIWAYAT_SKG"
            ),  # @CPTD_RIWAYAT_SKG	text NULL,
            (
                None
                if Globals().input(request.POST, "TTVTSISTOL") == ""
                else Globals().input(request.POST, "TTVTSISTOL")
            ),  # @TTVTSISTOL int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVDIASTOL") == ""
                else Globals().input(request.POST, "TTVDIASTOL")
            ),  # @TTVDIASTOL int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVNADI") == ""
                else Globals().input(request.POST, "TTVNADI")
            ),  # @TTVNADI int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVNAFAS") == ""
                else Globals().input(request.POST, "TTVNAFAS")
            ),  # @TTVNAFAS int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVSUHU") == ""
                else Globals().input(request.POST, "TTVSUHU")
            ),  # @TTVSUHU float  NULL,
            (
                None
                if Globals().input(request.POST, "TTVBERAT_BADAN") == ""
                else Globals().input(request.POST, "TTVBERAT_BADAN")
            ),  # @TTVBERAT_BADAN float  NULL,
            (
                None
                if Globals().input(request.POST, "TTVTINGGI_BADAN") == ""
                else Globals().input(request.POST, "TTVTINGGI_BADAN")
            ),  # @TTVTINGGI_BADAN float  NULL,
            (
                None
                if Globals().input(request.POST, "TTVO2") == ""
                else Globals().input(request.POST, "TTVO2")
            ),  # @TTVO2 int  NULL,
            (
                None
                if Globals().input(request.POST, "TTVKESADARAN") == ""
                else Globals().input(request.POST, "TTVKESADARAN")
            ),  # @TTVKESADARAN varchar (150) NULL,
            (
                None
                if Globals().input(request.POST, "TTV_LINGKAR_KEPALA") == ""
                else Globals().input(request.POST, "TTV_LINGKAR_KEPALA")
            ),  # @TTV_LINGKAR_KEPALA float  NULL,
            (
                None
                if Globals().input(request.POST, "TTV_HPHT") == ""
                else Globals().input(request.POST, "TTV_HPHT")
            ),  # @TTV_HPHT datetime  NULL,
            (
                None
                if Globals().input(request.POST, "TTV_HPL") == ""
                else Globals().input(request.POST, "TTV_HPL")
            ),  # @TTV_HPL datetime  NULL,
            (
                None
                if Globals().input(request.POST, "TTV_LINGKAR_PERUT") == ""
                else Globals().input(request.POST, "TTV_LINGKAR_PERUT")
            ),  # @TTV_LINGKAR_PERUT float NULL,
            (
                None
                if Globals().input(request.POST, "TTV_UH") == ""
                else Globals().input(request.POST, "TTV_UH")
            ),  # @TTV_UH float NULL,
            Globals().input(request.POST, "Program_DCG"),
            Globals().input(request.POST, "Program_Rujukan"),
            "A",  # @STATUS_AUD nvarchar(5) = 'A'
        ]
        # print(q % proc_param)
        # print(q % tuple(proc_param))
        result_set = Globals().getDataSP(q, proc_param)
        # edit= json.loads(result_set)

        if result_set[0]["error_code"] == 0:
            edit = json.dumps(
                {
                    "success": True,
                    "message": "succes tanpa bridging",
                    "data": result_set[0],
                }
            )
            # CEK CABANGNYA BRIDGING GAK
            qBPJS = "SELECT * FROM CABANG WHERE CABANG_ID=%s"
            cekQCabang = Globals().getDataQuery(qBPJS, [request.session["kdCabang"]])
            if len(cekQCabang) > 0:
                # CEK CUSTOMER NYA BRIDGING GAK
                qBPJS = " SELECT * FROM KUNJUNGANPASIEN KP"
                qBPJS += " LEFT JOIN CUSTOMER CST ON KP.KD_CUSTOMER=CST.CUSID"
                qBPJS += (
                    " LEFT JOIN KELOMPOKCUSTOMER KCT ON CST.KELOMPOK_ID=KCT.FMKCUST_ID"
                )
                qBPJS += " WHERE KCT.STATUS_BPJS='1' AND KP.KPNO_TRANSAKSI=%s"
                cekQBridging = Globals().getDataQuery(
                    qBPJS, [Globals().input(request.POST, "noTrans")]
                )
                if len(request.POST["noBPJS"]) == 13:
                    cekQBridging = "1"
                if len(cekQBridging) > 0:
                    saveFormPcares = ""
                    saveFormPcares = str(saveFormPcare(request))
                    if saveFormPcares == "OK":
                        savePcareKunjungan = ""
                        # try:
                        # savePcareKunjungan=str(views_pcare.bridgingPostRujukanSpesialis(request))
                        savePcareKunjungan = {}
                        savePcareKunjungan = bridgingPostRujukanSpesialis(request)
                        # print(savePcareKunjungan)
                        if savePcareKunjungan["success"] == True:
                            edit = json.dumps(
                                {
                                    "success": True,
                                    "message": "Sukses Simpan dan Bridging pcare",
                                    "data": result_set[0],
                                }
                            )
                        else:
                            edit = json.dumps(
                                {
                                    "success": False,
                                    "message": "Sukses Simpan EMR  {}".format(
                                        savePcareKunjungan["messages"]
                                    ),
                                }
                            )
                    else:
                        edit = json.dumps({"success": False, "message": saveFormPcare})
        else:
            edit = json.dumps(
                {
                    "success": False,
                    "message": result_set[0]["error_message"]
                    + ", pada line "
                    + str(result_set[0]["line_error"]),
                }
            )
        # pprint(edit)

        return HttpResponse(edit, content_type="application/json")
    else:
        return HttpResponse(_("Invalid request!"))


def saveFormPcare(request):
    noKunjungan = None

    if len(request.POST["noBPJS"]) < 13:
        return "No BPJS tidak boleh kurang dari 13 digits"

    if len(request.POST["noBPJS"]) > 13:
        return "No BPJS tidak valid"
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
    qKunjunganKlinikBrd = (
        "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' ".format(
            request.POST["noTrans"]
        )
    )
    dataKunjunganKlinikBrd = Globals().getDataQuery(qKunjunganKlinikBrd, [])

    if int(len(dataKunjunganKlinikBrd)) > 0:
        qKunjunganKlinikBrd = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING "
        qKunjunganKlinikBrd += " SET  opsiRujuk_rbs='%s', jenisRujukan_rbs='%s', rujukanSarana='%s', ppkRujukan='%s', ppkRujukanN='%s', spesialisRujukan='%s', spesialisRujukanN='%s', catatanRujukan='%s', tglRujukan='%s', kondisiKhususKategori='%s',noKunjungan='%s',kdTacc='%s',alasanTacc='%s',StatusPulang='%s',KD_CABANG='%s',jamRujuk='%s' "
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
            request.POST["jamRujuk"],
        )
        qKunjunganKlinikBrd = qKunjunganKlinikBrd % inputan
        qKunjunganKlinikBrd += " where MRDNO_TRANSAKSI='{}' ".format(
            request.POST["noTrans"]
        )
        Globals().executeQuery(qKunjunganKlinikBrd, [])
    else:
        qKunjunganKlinikBrd = "INSERT INTO MR_KUNJUNGAN_KLINIK_BRIDGING(MRDNO_TRANSAKSI,opsiRujuk_rbs, jenisRujukan_rbs, rujukanSarana, ppkRujukan, ppkRujukanN, spesialisRujukan, spesialisRujukanN, catatanRujukan, tglRujukan, kondisiKhususKategori,noKunjungan,kdTacc,alasanTacc,StatusPulang,KD_CABANG) "
        qKunjunganKlinikBrd += "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') "
        inputan = (
            request.POST["noTrans"],
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
        # print(qKunjunganKlinikBrd)
        # print(inputan)
        qKunjunganKlinikBrd = qKunjunganKlinikBrd % inputan
        Globals().executeQuery(qKunjunganKlinikBrd, [])

    return "OK"


def prints(msg):
    debug = getattr(env, "DEBUG_PCARE", False)
    # if debug:
    # print(msg)


def bridgingPostRujukanSpesialis(request):
    kdCabang = request.session["kdCabang"]
    if len(request.POST["noBPJS"]) < 13:
        return "No BPJS tidak boleh kurang dari 13 digits"

    if len(request.POST["noBPJS"]) > 13:
        return "No BPJS tidak valid"

    qPoli = "SELECT * FROM POLIKLINIK where FMPKLINIK_ID='{}'".format(
        request.POST["MRDKD_UNIT"]
    )
    dataPoli = Globals().getDataQuery(qPoli)
    FMPKODEBPJS = dataPoli[0]["FMPKODEBPJS"]

    alasanTacc = None
    nmTacc="Tanpa TACC"
    kdTacc = request.POST["kdTacc"]
    if request.POST["kdTacc"] == "":
        kdTacc = "0"
    if request.POST["alasanTacc"] == "":
        alasanTacc = None
    
    if kdTacc == "1":
        alasanTacc=["< 3 Hari", ">= 3 - 7 Hari", ">= 7 Hari"][int(request.POST['alasanTacc'])]
        # alasanTacc = ["< 3 Hari", ">= 3 - 7 Hari", ">= 7 Hari"]
        nmTacc="Time"
    if kdTacc == "2":
        nmTacc="Age"
        alasanTacc=["< 1 Bulan", ">= 1 Bulan s/d < 12 Bulan", ">= 1 Tahun s/d < 5 Tahun",">= 5 Tahun s/d < 12 Tahun", ">= 12 Tahun s/d < 55 Tahun", ">= 55 Tahun"][int(request.POST['alasanTacc'])]
        # alasanTacc = [
        #     "< 1 Bulan",
        #     ">= 1 Bulan s/d < 12 Bulan",
        #     ">= 1 Tahun s/d < 5 Tahun",
        #     ">= 5 Tahun s/d < 12 Tahun",
        #     ">= 12 Tahun s/d < 55 Tahun",
        #     ">= 55 Tahun",
        # ]
    if kdTacc == "3":
        nmTacc="Complication"
        alasanTacc = request.POST["alasanTacc"]
    if kdTacc == "4":
        nmTacc="Comorbidity"
        alasanTacc=request.POST['alasanTacc']
        alasanTacc = ["< 3 Hari", ">= 3 - 7 Hari", ">= 7 Hari"]

    qDdataPenyakit = "SELECT * FROM MR_PENYAKIT where MRPNO_TRANSAKSI='{}'  AND MR_PENYAKIT.MRPSTAT_DIAG='5' ".format(
        request.POST["noTrans"]
    )
    dataPenyakit = Globals().getDataQuery(qDdataPenyakit, [])
    qDdataPenyakit2 = "SELECT * FROM MR_PENYAKIT where MRPNO_TRANSAKSI='{}' AND MR_PENYAKIT.MRPSTAT_DIAG<>'5' ".format(
        request.POST["noTrans"]
    )
    dataPenyakit2 = Globals().getDataQuery(qDdataPenyakit2, [])
    if int(len(dataPenyakit2)) > 0:
        dataPenyakit2s = dataPenyakit2[0]["MRPKD_PENYAKIT"]
        if int(len(dataPenyakit2)) > 1:
            dataPenyakit3s = dataPenyakit2[1]["MRPKD_PENYAKIT"]
        else:
            dataPenyakit3s = None
    else:
        dataPenyakit2s = None
        dataPenyakit3s = None

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
        if kdTacc == "0":
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
        else:
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
                "nmTacc": nmTacc,
                "alasanTacc": alasanTacc,
            }
    except:
        restHasil = {
            "success": False,
            "messages": "\n TETAPI TIDAK TERSAVE PCARE KARENA: \n KELUHAN,TTV BELUM LENGKAP",
        }
        return restHasil
    # print("payload kunjungan")
    # print(payload)
    # url = "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0/kunjungan"
    url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
    url = url_pcare + "/kunjungan"
    qCariNoRujukan = "SELECT ISNULL(a.noKunjungan,'-') as noKunjungan FROM MR_KUNJUNGAN_KLINIK_BRIDGING a where a.MRDNO_TRANSAKSI='{}' and ISNULL(a.noKunjungan,'-')<>'-'  and ISNULL(a.noKunjungan,'-')<>'None' ".format(
        request.POST["noTrans"]
    )
    dataCariNoRujukan = Globals().getDataQuery(qCariNoRujukan, [])
    if len(dataCariNoRujukan) > 0:
        noKunjungan = dataCariNoRujukan[0]["noKunjungan"]
    else:
        noKunjungan = kunjunganRujukanBridging(
            request, request.POST["noBPJS"], request.POST["MRDTGL_DIAGNOSA"]
        )
    # return "No BPJS tidak valid"
    # print("noKunjungan")
    # print(noKunjungan)
    # return noKunjungan
    # return 0
    restHasil = {"success": True, "messages": "OK"}
    if noKunjungan != "-":
        # # prints(headers)
        # print("update Kunjungan")
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
        if request.POST["StatusPulang"] != "4":
            # update data kunjungan untuk pasien tidak rujuk
            try:
                # print('put')
                # print(url)
                # res1 = Globals().bridgeBPJS(request, url, "put", payload)
                # print("delete1 Kunjungan")
                # print("---------------------------")
                # print(url)
                # print(payload)
                # prints("---------------------------")
                res1 = Globals().bridgeBPJS(url, "put", kdCabang, payload)
                # print("delete Kunjungan")
                # print(res1)
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
                    q = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET noKunjungan='{}',jamRujuk='{}' where MRDNO_TRANSAKSI='{}'".format(
                        noKunjungan, request.POST["jamRujuk"], request.POST["noTrans"]
                    )
                    # prints(q)
                    Globals().executeQuery(q, [])
                    # Globals().executeQuery(q)

                # prints("here")
            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        else:
            # delete data kunjungan untuk pasien  rujuk lalu buat pendaftaran baru
            try:
                tanggal = datetime.now().strftime("%d-%m-%Y")
                nomor = request.POST["noBPJS"]
                poli = FMPKODEBPJS
                noUrut = request.POST["antrianbpjs"]

                # hapus kunjungan dulu
                urlhapus = url + "/" + noKunjungan
                res = Globals().bridgeBPJS(urlhapus, "DELETE", kdCabang)
                # print("delete Kunjungan")
                # print(urlhapus)
                # print(res)
                # hapus pendaftaran dulu
                urlhapus = (
                    url_pcare
                    + "/pendaftaran/peserta/"
                    + nomor
                    + "/tglDaftar/"
                    + tanggal
                    + "/noUrut/"
                    + noUrut
                    + "/kdPoli/"
                    + poli
                )
                method = "DELETE"
                res = Globals().bridgeBPJS(urlhapus, method, kdCabang)
                # print("delete daftar")
                # print(res)
                # print(urlhapus)

                # cek noka
                urlnoka = url_pcare + "/peserta/noka/" + request.POST["noBPJS"]
                method = "get"
                data = Globals().bridgeBPJS(urlnoka, method, kdCabang)
                urldaftar = url_pcare + "/pendaftaran"
                method = "post"

                payloaddaftar = {
                    "kdProviderPeserta": data["response"]["kdProviderPst"][
                        "kdProvider"
                    ],
                    "tglDaftar": request.POST["MRDTGL_DIAGNOSA"],
                    "noKartu": request.POST["noBPJS"],
                    "kdPoli": FMPKODEBPJS,
                    "keluhan": "",
                    "kunjSakit": True,
                    "sistole": int(request.POST["TTVTSISTOL"]),
                    "diastole": int(request.POST["TTVDIASTOL"]),
                    "beratBadan": int(request.POST["TTVBERAT_BADAN"]),
                    "tinggiBadan": int(request.POST["TTVTINGGI_BADAN"]),
                    "respRate": int(request.POST["TTVNAFAS"]),
                    "lingkarPerut": int(request.POST["TTV_LINGKAR_PERUT"]),
                    "heartRate": int(request.POST["TTVNADI"]),
                    "rujukBalik": 0,
                    "kdTkp": "10",
                }
                data = Globals().bridgeBPJS(urldaftar, method, kdCabang, payloaddaftar)
                if data["metaData"]["code"] == 201:
                    no_antrian = data["response"]["message"]
                    query = "UPDATE KUNJUNGANPASIEN SET KD_ANTRIAN_BPJS=%s WHERE KPNO_TRANSAKSI =%s "
                    Globals().executeQuery(query, [no_antrian, request.POST["noTrans"]])
                # print("insert Kunjungan")
                # print(noKunjungan)
                noKunjungan = ""
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
                res = Globals().bridgeBPJS(url, "post", kdCabang, payload)
                prints(res)
                prints(res)
                prints("---------------------------")
                prints(url)
                prints(payload)
                prints("---------------------------")
                if res:
                    datas = res
                    # print("datas")
                    # print(url)
                    # print(payload)
                    # print(datas)
                    # prints(datas)
                    if datas["metaData"]["code"] == 201:
                        # q = "INSERT INTO BPJS_SEP(FMNOTRANSAKSI,FMNOSEP,FMNO_KARTU,FMNAMA_PESERTA)VALUES('{}','{}','{}','{}')".format(request.POST['MRDNO_TRANSAKSI'],datas['response']['message'],request.POST['noBPJS'],request.POST['noBPJS'])
                        # # prints(q)
                        # Globals().executeQuery(q)
                        noKunjungan = datas["response"][0]["message"]
                        q = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET noKunjungan='{}',jamRujuk='{}' where MRDNO_TRANSAKSI='{}'".format(
                            noKunjungan,
                            request.POST["jamRujuk"],
                            request.POST["noTrans"],
                        )
                        # Globals().executeQuery(q)
                        Globals().executeQuery(q, [])
                    else:
                        respon = []
                        # print("sini")
                        # print(datas)
                        # print(len(datas["response"]))
                        if len(datas["response"]) == 0:
                            # print('sini')
                            msgE = "\n TETAPI TIDAK TERSAVE PCARE KARENA \n {}".format(
                                datas["metaData"]["message"]
                            )
                            restHasil = {"success": False, "messages": msgE}
                            return restHasil

                        if datas["metaData"]["code"] == 0:
                            msgE = "\n TETAPI TIDAK TERSAVE PCARE KARENA ICD10 BELUM DI ISI "
                            restHasil = {"success": False, "messages": msgE}
                        else:
                            msgE = "\n TETAPI TIDAK TERSAVE PCARE KARENA: "

                            if len(datas["response"]) > 0:
                                for x in datas["response"]:
                                    msgE += "\n- {} {} ".format(
                                        x["field"], x["message"]
                                    )
                            restHasil = {"success": False, "messages": msgE}
                else:
                    prints("gagal post")
                    prints(res)
            except requests.exceptions.RequestException as e:
                prints(e)
                raise

    else:
        try:
            # cek dulu apakah sudah di daftarkan
            if request.POST["antrianbpjs"] == "":
                # cek noka
                urlnoka = url_pcare + "/peserta/noka/" + request.POST["noBPJS"]
                method = "get"
                data = Globals().bridgeBPJS(urlnoka, method, kdCabang)
                urldaftar = url_pcare + "/pendaftaran"
                method = "post"
                payloaddaftar = {
                    "kdProviderPeserta": data["response"]["kdProviderPst"][
                        "kdProvider"
                    ],
                    "tglDaftar": request.POST["MRDTGL_DIAGNOSA"],
                    "noKartu": request.POST["noBPJS"],
                    "kdPoli": FMPKODEBPJS,
                    "keluhan": "",
                    "kunjSakit": True,
                    "sistole": int(request.POST["TTVTSISTOL"]),
                    "diastole": int(request.POST["TTVDIASTOL"]),
                    "beratBadan": int(request.POST["TTVBERAT_BADAN"]),
                    "tinggiBadan": int(request.POST["TTVTINGGI_BADAN"]),
                    "respRate": int(request.POST["TTVNAFAS"]),
                    "lingkarPerut": int(request.POST["TTV_LINGKAR_PERUT"]),
                    "heartRate": int(request.POST["TTVNADI"]),
                    "rujukBalik": 0,
                    "kdTkp": "10",
                }
                data = Globals().bridgeBPJS(urldaftar, method, kdCabang, payloaddaftar)
                if data["metaData"]["code"] == 201:
                    no_antrian = data["response"]["message"]
                    query = "UPDATE KUNJUNGANPASIEN SET KD_ANTRIAN_BPJS=%s WHERE KPNO_TRANSAKSI =%s "
                    Globals().executeQuery(query, [no_antrian, request.POST["noTrans"]])
            # batas-----------------------------

            # print("insert Kunjungan")
            # print(noKunjungan)
            res = Globals().bridgeBPJS(url, "post", kdCabang, payload)
            prints(res)
            prints(res)
            prints("---------------------------")
            prints(url)
            # print(payload)
            prints("---------------------------")
            if res:
                datas = res
                print("datas")
                print(url)
                print(payload)
                print(datas)
                # prints(datas)
                if datas["metaData"]["code"] == 201:
                    # q = "INSERT INTO BPJS_SEP(FMNOTRANSAKSI,FMNOSEP,FMNO_KARTU,FMNAMA_PESERTA)VALUES('{}','{}','{}','{}')".format(request.POST['MRDNO_TRANSAKSI'],datas['response']['message'],request.POST['noBPJS'],request.POST['noBPJS'])
                    # # prints(q)
                    # Globals().executeQuery(q)
                    noKunjungan = datas["response"][0]["message"]
                    q = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET noKunjungan='{}',jamRujuk='{}' where MRDNO_TRANSAKSI='{}'".format(
                        noKunjungan, request.POST["jamRujuk"], request.POST["noTrans"]
                    )
                    # Globals().executeQuery(q)
                    Globals().executeQuery(q, [])
                else:
                    respon = []
                    # print("sini")
                    # print(datas)
                    # print(len(datas["response"]))
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
            request.POST["noTrans"]
        )
    )
    dataKunjunganKlinikBrd = Globals().getDataQuery(qKunjunganKlinikBrd, [])
    if int(len(dataKunjunganKlinikBrd)) > 0:
        qKunjunganKlinikBrd = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING "
        qKunjunganKlinikBrd += " SET  opsiRujuk_rbs='%s', jenisRujukan_rbs='%s', rujukanSarana='%s', ppkRujukan='%s', ppkRujukanN='%s', spesialisRujukan='%s', spesialisRujukanN='%s', catatanRujukan='%s', tglRujukan='%s', kondisiKhususKategori='%s',noKunjungan='%s',kdTacc='%s',alasanTacc='%s',StatusPulang='%s',KD_CABANG='%s',jamRujuk='%s' "
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
            request.POST["jamRujuk"],
        )
        qKunjunganKlinikBrd = qKunjunganKlinikBrd % inputan
        qKunjunganKlinikBrd += " where MRDNO_TRANSAKSI='{}' ".format(
            request.POST["noTrans"]
        )
        Globals().executeQuery(qKunjunganKlinikBrd, [])
    else:
        qKunjunganKlinikBrd = "INSERT INTO MR_KUNJUNGAN_KLINIK_BRIDGING(MRDNO_TRANSAKSI,opsiRujuk_rbs, jenisRujukan_rbs, rujukanSarana, ppkRujukan, ppkRujukanN, spesialisRujukan, spesialisRujukanN, catatanRujukan, tglRujukan, kondisiKhususKategori,noKunjungan,kdTacc,alasanTacc,StatusPulang,KD_CABANG,jamRujuk) "
        qKunjunganKlinikBrd += "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') "
        inputan = (
            request.POST["noTrans"],
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
            request.POST["jamRujuk"],
        )
        qKunjunganKlinikBrd = qKunjunganKlinikBrd % inputan
        # cursorKunjunganKlinikBrd.execute(qKunjunganKlinikBrd)
        Globals().executeQuery(qKunjunganKlinikBrd, [])
        # else:
        # 	# pprints("gagal")
        # 	# prints(datas)

    # return datas
    return restHasil


def kunjunganRujukanBridging(request, noKartu, tanggal):
    kdCabang = request.session["kdCabang"]
    kdApp = "095"
    qBPJS = "SELECT * FROM CABANG WHERE CABANG_ID=%s"
    cabang = Globals().getDataQuery(qBPJS, [request.session["kdCabang"]])
    PCARE_STATUS = getattr(env, "PCARE_STATUS", "PROD")
    BPJS_USERPCARE1 = getattr(env, "BPJS_USERPCARE1", cabang[0]["userncc"])
    url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
    url = url_pcare + "/kunjungan/peserta/{}".format(noKartu)
    # res = requests.get(url,headers=headers)
    datas = Globals().bridgeBPJS(url, "get", kdCabang)
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
            # print(dataRujukan)
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


def printSuratKeteranganSehat(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    pdf_file = Globals().generateReportDB(
        "EMR/Klinik_SuratKeteranganSehat.jrxml",
        "SuratKeteranganSehat_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "logo": logo_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratRTW(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    pdf_file = Globals().generateReportDB(
        "EMR/Klinik_SuratRTW.jrxml",
        "SuratRTW_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "logo": logo_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratResumeMedis(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    # if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
    #     logo_url = os.path.abspath(
    #         os.path.dirname(__name__)
    #     ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    # else:
    #     logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    pdf_file = Globals().generateReportDB(
        "EMR/SuratResumeMedis.jrxml",
        "SuratRTW_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            # "logo": logo_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratFTW(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    pdf_file = Globals().generateReportDB(
        "EMR/Klinik_SuratRTW.jrxml",
        "SuratRTW_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "logo": logo_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratKeteranganDokter(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    tglAwalcuti = Globals().input(request.GET, "tglAwalcuti")
    # tglAwalcuti = tglAwalcuti.strftime("%b %d, %Y")
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
        TTD_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["TTD"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
        TTD_url = "static/img/logo/{}".format(cabang[0]["TTD"])
    pdf_file = Globals().generateReportDB(
        "EMR/Klinik_SuratKeteranganDokter.jrxml",
        "SuratKeteranganDokter_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "logo": logo_url,
            "tglAwalcuti": tglAwalcuti,
            # "ttd_dokter": TTD_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratRujukanDPP(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])

    user = Globals().input(request.GET, "user_id")
    no_trans = Globals().input(request.GET, "no_transaksi")

    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    kdCabang = cabang[0]["CABANG_ID"]
    q = "SELECT MD.MRD_DIASTOLE,MD.MRD_SISTOLE,MD.MRDNO_TRANSAKSI,MD.MRDKD_DOKTER ,MD.MRDSOAPIKET,ISNULL(SRJ.FMSKETALERGI,'-') as FMSKETALERGI "
    q += " FROM MR_DIAGNOSA as MD LEFT JOIN SOAPI_RJ as SRJ ON MD.MRDNO_TRANSAKSI=SRJ.FMSBUKTI_ID"
    q += " WHERE MD.MRDNO_TRANSAKSI='{}'".format(no_trans)
    Globals().executeQuery(q)
    cekAsesment = Globals().dictfetchall(cursor)
    # prints(cekAsesment)
    pdf_file = {}
    if int(len(cekAsesment)) > 0:
        inputan = {"NO_TRANSAKSI": no_trans, "logo": logo_url}
        pdf = Globals().generateReportDB(
            "EMR/Klinik_Surat_FORMULIR_PINDAH_FASILITAS_KESEHATAN.jrxml",
            "Klinik_Surat_FORMULIR_PINDAH_FASILITAS_KESEHATAN_" + no_trans,
            user,
            inputan,
        )
        pdf_file = {"success": True, "message": pdf["pdf"]}
    else:
        pdf_file = {"success": False, "message": "Terjadi Kesalahan!"}

    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratPenolakanTindakanKedokteran(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    pdf_file = Globals().generateReportDB(
        "EMR/Klinik_Surat_FORMULIR_PENOLAKAN_TINDAKAN_KEDOKTERAN_INDUK.jrxml",
        "Surat_FORMULIR_PENOLAKAN_TINDAKAN_KEDOKTERAN_INDUK_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "logo": logo_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratPersetujuanTindakanKedokteran(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    pdf_file = Globals().generateReportDB(
        "EMR/Klinik_Surat_FORMULIR_PERSETUJUAN_TINDAKAN_KEDOKTERAN_INDUK.jrxml",
        "Surat_FORMULIR_PERSETUJUAN_TINDAKAN_KEDOKTERAN_INDUK_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "logo": logo_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printSuratKematianKlinik(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])

    pdf_file = Globals().generateReportDB(
        "EMR/Klinik_Surat_FORMULIR_SURAT_KEMATIAN.jrxml",
        "Surat_FORMULIR_SURAT_KEMATIAN_" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "logo": logo_url,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def calculateAge(birthDate):
    today = date.today()
    age = (
        today.year
        - birthDate.year
        - ((today.month, today.day) < (birthDate.month, birthDate.day))
    )
    return age


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


def printSuratRujukanPCAREBPJS(request):
    kdApp = "095"
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    code = None
    qKunjunganKlinikBrd = "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' AND RESPONSE IS NOT NULL".format(
        request.GET["no_transaksi"]
    )
    dqKunjunganKlinikBrd = Globals().getDataQuery(qKunjunganKlinikBrd)
    if int(len(dqKunjunganKlinikBrd)) == 0:
        url_pcare = getattr(
            env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
        )
        url = url_pcare + "/kunjungan/rujukan/{}".format(request.GET["noRujukan"])
        data = Globals().bridgeBPJS(url, "get", kdCabang)
        code = data["metaData"]["code"]
    else:
        code = int(dqKunjunganKlinikBrd[0]["CODE"])
        data = json.loads(dqKunjunganKlinikBrd[0]["RESPONSE"])
    # code = 400
    # print("code")
    # print(code)
    qKunjunganKlinikBrd = (
        "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' ".format(
            request.GET["no_transaksi"]
        )
    )
    dqKunjunganKlinikBrd = Globals().getDataQuery(qKunjunganKlinikBrd)

    if code == 200:
        qKunjunganKlinikBrd = "UPDATE MR_KUNJUNGAN_KLINIK_BRIDGING SET RESPONSE='{}',CODE='{}' where MRDNO_TRANSAKSI='{}' ".format(
            (json.dumps(data)).replace("'", ""), code, request.GET["no_transaksi"]
        )
        Globals().executeQuery(qKunjunganKlinikBrd)
        # print(qKunjunganKlinikBrd)

        user = request.session["user_id"]
        no_trans = Globals().input(request.GET, "no_transaksi")
        noRujukan = Globals().input(request.GET, "noRujukan")
        logo_url = (
            os.path.abspath(os.path.dirname(__name__)) + "\static\img\logobpjs.png"
        )

        if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
            logo_url = (
                os.path.abspath(os.path.dirname(__name__)) + "\static\img\logobpjs.png"
            )
        else:
            logo_url = (
                os.path.abspath(os.path.dirname(__name__)) + "/static/img/logobpjs.png"
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
            qKunjunganKlinikBrd = "SELECT  UPPER(ISNULL(spesialisRujukanN,'')) as spesialisRujukanNs,* FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' AND RESPONSE IS NOT NULL".format(
                request.GET["no_transaksi"]
            )
            dqKunjunganKlinikBrd = Globals().getDataQuery(qKunjunganKlinikBrd)
            if int(len(dqKunjunganKlinikBrd)) != 0:
                nmPoli = dqKunjunganKlinikBrd[0]["spesialisRujukanNs"]
                catatanRujuk = dqKunjunganKlinikBrd[0]["catatanRujukan"]

        jadwalPcare = data["response"]["jadwal"]
        if jadwalPcare is None:
            jadwalPcare = ""
            qKunjunganKlinikBrd = "SELECT * FROM MR_KUNJUNGAN_KLINIK_BRIDGING where MRDNO_TRANSAKSI='{}' AND RESPONSE IS NOT NULL".format(
                request.GET["no_transaksi"]
            )
            dqKunjunganKlinikBrd = Globals().getDataQuery(qKunjunganKlinikBrd)
            if int(len(dqKunjunganKlinikBrd)) != 0:
                jadwalPcare = dqKunjunganKlinikBrd[0]["jamRujuk"]
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
        pdf_file = Globals().generateReportDB(
            "EMR/SuratRujukanPCAREBPJS.jrxml",
            "SuratRujukanPCAREBPJS" + no_trans,
            user,
            inputan,
            # list_format=[pilihcetak]
        )
        # pdf_file = {"success": True, "message": pdf_file["pdf"]}
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


def printCPPT(request):
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    user = request.session["user_id"]
    no_trans = Globals().input(request.GET, "no_transaksi")
    Terapi=getEresepTxT(no_trans)
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        logo_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
        TTD_url = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["TTD"])
    else:
        logo_url = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
        TTD_url = "static/img/logo/{}".format(cabang[0]["TTD"])
    pdf_file = Globals().generateReportDB(
        "EMR/_CetakCPPT_RJ.jrxml",
        "_CetakCPPT_RJ" + no_trans,
        user,
        {
            "NO_TRANSAKSI": no_trans,
            "cabang":kdCabang,
            "logo": logo_url,
            "Terapi":Terapi,
        },
        # list_format=[pilihcetak]
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

## ERESEP ##
def detailResep(request):
    kdCabang = request.session["kdCabang"]
    NO_TRANSAKSI = request.GET["NO_TRANSAKSI"]
    query = " SELECT ISNULL(b.FHRRESEPTEXT, '-') AS FHRRESEPTEXT, a.FDRRESEP, ISNULL(a.FDRRACIK_ID,(SELECT TOP 1 FERRACIK_ID FROM ERESEPRACIK AAA WHERE AAA.FHRNO_TRANSAKSI=%s )) AS FDRRACIK_ID, a.FDRBRG_ID, a.FDRBRGN, a.FDRSATUAN, a.FDRQTY, a.FDRQTYOUT, a.FDRDOSIS, a.FDRSIGNAF, "
    query += "  a.FDRDOSIS2, a.FDRSIGNAS, a.FDRSIGNAW, a.FDRSIGNA, a.FDRBUKTI_ID, b.FHRNO_TRANSAKSI, b.FHRBUKTI_ID, CONVERT(varchar, b.FHRDATE, 20) AS FHRDATE, b.FHRUSER, CONVERT(varchar, b.FHRUPDATE, 20) "
    query += " AS FHRUPDATE, b.FHRSTATUS, c.HJUAL, a.FDRQTY * c.HJUAL AS Total"
    query += " FROM  ERESEPDOKTER AS b "
    query += " LEFT JOIN ERESEPDOKTERD AS a ON b.FHRNO_TRANSAKSI = a.FDRBUKTI_ID "
    query += (
        " LEFT JOIN BARANG AS c ON a.FDRBRG_ID = c.BARANGC and c.BRANCH= LEFT(%s,3)"
    )
    query += " WHERE (b.FHRBUKTI_ID = %s)"
    query += " ORDER BY a.FDRRESEP"
    result = Globals().getDataQuery(query, [NO_TRANSAKSI, kdCabang, NO_TRANSAKSI])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def DaftardetailResep(request):
    kdCabang = request.session["kdCabang"]
    NO_TRANSAKSI = request.GET["NO_TRANSAKSI"]
    DOKTER_ID = request.GET["DOKTER_ID"]
    query = "Select a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, "
    query += "FDRSIGNA, FDRBUKTI_ID, b.PFKODE, PFKETERANGAN,c.HJUAL,(a.FDRQTY*c.Hjual) As Total  "
    query += "from ERESEPPAKETD a inner join ERESEPPAKET b on a.FDRBUKTI_ID=b.PFKODE  "
    query += "inner join Barang c on A.FDRBRG_ID=c.barangc and c.BRANCH=%s "
    query += "where b.PFKODE=%s and b.PFKDDOKTER=%s ORDER BY FDRRESEP "

    result = Globals().getDataQuery(query, [kdCabang, NO_TRANSAKSI, DOKTER_ID])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def crudDaftarResep(request):
    json_data_list = []
    edit = {}
    if request.method == "POST":
        q = request.POST["q"]
        now = datetime.now()
        if q == "entryDaftarResep":
            try:
                ks = None
                isi = '"{}"'.format(request.POST["PFKODE"])
                isi += ' ,"{}"'.format(request.POST["PFKETERANGAN"])
                isi += ' ,"{}"'.format(request.POST["FDRRESEPU"])
                isi += ' ,"{}"'.format(request.POST["FDRBRG_ID"])
                isi += ' ,"{}"'.format(request.POST["FDRBRGN"])
                isi += ' ,"{}"'.format(request.POST["FDRSATUAN"])
                isi += ' ,"{}"'.format(request.POST["FDRQTY"])
                isi += ' ,"{}"'.format(request.POST["FDRDOSIS"])
                isi += ' ,"{}","{}","{}" '.format(
                    request.POST["FDRSIGNAF"],
                    request.POST["FDRDOSIS2"],
                    request.POST["FDRSIGNAS"],
                )  # SIGNAF,DOSIS2,SIGNAS
                isi += ' ,"{}"'.format(request.POST["FDRSIGNAW"])
                isi += ' ,"{}"'.format(request.POST["FDRSIGNA"])
                isi += ' ,"{}"'.format(request.POST["PFKODE"])
                isi += ' ,"{}"'.format(request.POST["StatusAUD"])
                isi += ' ,"{}"'.format(request.POST["DOKTER_ID"])
                query = "EXEC AUD_ERESEPPAKETD {}".format(isi)
                # print(query)
                Globals().executeQuery(query)

                edit["success"] = True
                edit["message"] = "Method Valid"
            except requests.exceptions.RequestException as e:
                prints(e)
                raise

        elif q == "gantiNamaResep":
            query = "UPDATE ERESEPPAKET SET PFKODE='{}' WHERE PFKODE='{}' ".format(
                request.POST["PFKODE"], request.POST["FDRBUKTI_ID_EDIT"]
            )
            Globals().executeQuery(query)
            # prints(query)
            query = "UPDATE ERESEPPAKETD SET FDRBUKTI_ID='{}' WHERE FDRBUKTI_ID='{}' ".format(
                request.POST["PFKODE"], request.POST["FDRBUKTI_ID_EDIT"]
            )
            Globals().executeQuery(query)
            # result_set = cursor.fetchall()
            edit["success"] = True
            edit["message"] = "Sukses Ganti Nama"
        else:
            edit["success"] = False
            edit["message"] = "Method Not Valid"
    else:
        edit["success"] = False
        edit["message"] = "Method Not Valid"
    json_data_list.append(edit)
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def pickerDaftarResep(request):
    query = "select PFKODE,PFKETERANGAN from ERESEPPAKET where PFKDDOKTER='{}' GROUP BY  PFKODE,PFKETERANGAN order by PFKETERANGAN".format(
        request.GET["DOKTER_ID"]
    )
    result = Globals().getDataQuery(query)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def deleteItemPaketResep(request):
    query = "DELETE FROM ERESEPPAKETD WHERE FDRRESEP='{}' AND FDRBUKTI_ID='{}' AND PFKDDOKTER='{}'".format(
        request.POST["FDRRESEP"],
        request.POST["FDRBUKTI_ID"],
        request.POST["PFKDDOKTER"],
    )
    deleteItem = Globals().executeQuery(query)
    query = "DELETE FROM ERESEPPAKET WHERE PFKODE='{}' AND PFKDDOKTER='{}'".format(
        request.POST["FDRBUKTI_ID"],
        request.POST["PFKDDOKTER"],
    )
    deleteItem = Globals().executeQuery(query)
    result = {"success": True, "message": "Sukses Hapus"}
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printResepDokter(request):
    nomor = request.GET["no_trans"]
    report = "resepDokterRJ2.jrxml"
    report2 = "resepDokterRJ2"
    tanggal_waktu_cetak = datetime.now().strftime("%Y-%m-%d")
    jam = str(datetime.now().strftime("%H:%M:%S"))
    user = request.session["user_priv"]
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    if getattr(env, "JDBC_MODE", "WINDOWS") == "WINDOWS":
        file_logo = os.path.abspath(
            os.path.dirname(__name__)
        ) + "\static\img\logo\{}".format(cabang[0]["logoKlinik"])
    else:
        file_logo = "static/img/logo/{}".format(cabang[0]["logoKlinik"])
    pdf_file = Globals().generateReportDB(
        report,
        report2,
        user,
        {
            "no_trans": nomor,
            "logo": file_logo,
        },
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def printResepDoktermanual(request):
    nomor = request.GET["no_trans"]
    report = "SuratEResepNonFormularium.jrxml"
    report2 = "SuratEResepNonFormularium"
    tanggal_waktu_cetak = datetime.now().strftime("%Y-%m-%d")
    jam = str(datetime.now().strftime("%H:%M:%S"))
    user = request.session["user_priv"]
    # file_logo = '/static/img/logo/logo.png'
    pdf_file = Globals().generateReportDB(
        report,
        report2,
        user,
        {
            "NO_TRANSAKSI": nomor,
        },
    )
    json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getIdDataBarang(request):
    kode = request.GET["kode"]
    cabang_id = request.session["kdCabang"]
    tarifobat = 0
    if len(kode) == 0:
        q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,iif(case when %s=1 then DBP "
        q += " when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end =0,HJUAL,case when %s=1 then DBP  "
        q += " when %s=2 then HJUALASKIN  when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end) AS HJUAL, "
        q += " iif(case when %s=1 then DBP "
        q += " when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end =0,0,case when %s=1 then 1  "
        q += " when %s=2 then 1  when %s=3 then 1 "
        q += " when %s=4 then 0 else 0 end) AS STATUS, "
        q += " TTYPEC,B.STATUSPRODUK,A.SATKEKUATAN,A.KEKUATAN  "
        q += " FROM BARANG A INNER JOIN PRODUKOBAT B ON  A.TTYPEC=B.PRD_ID where AKTIF<>1 and  BARANGC=%s and A.BRANCH=%s order by BARANGC "
        result = Globals().getDataQuery(
            q,
            [
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                kode,
                cabang_id,
            ],
        )
    else:
        q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,iif(case when %s=1 then DBP "
        q += " when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end =0,HJUAL,case when %s=1 then DBP  "
        q += " when %s=2 then HJUALASKIN  when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end) AS HJUAL, "
        q += " iif(case when %s=1 then DBP "
        q += " when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end =0,0,case when %s=1 then 1  "
        q += " when %s=2 then 1  when %s=3 then 1 "
        q += " when %s=4 then 0 else 0 end) AS STATUS, "
        q += " TTYPEC,B.STATUSPRODUK,A.SATKEKUATAN,KEKUATAN  "
        q += " FROM BARANG A INNER JOIN PRODUKOBAT B ON  A.TTYPEC=B.PRD_ID where AKTIF<>1 and  BARANGC=%s or BARCODE=%s and A.BRANCH=%s order by BARANGC "
        result = Globals().getDataQuery(
            q,
            [
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                kode,
                kode,
                cabang_id,
            ],
        )

    if len(result) == 0:
        data = {"status": "gagal", "pesen": "data tidak ditemukan", "data": None}
    else:
        data = {"status": "ok", "pesen": "data ditemukan", "data": result[0]}
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getDataBarang(request):
    # nama = '%'+request.GET['nama']+'%'
    nama = request.GET["nama"] + "%"
    tarifobat = 0
    cabang_id = request.session["kdCabang"]

    if nama == "nullnone0":
        result = []
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    else:
        q = " SELECT A.BARANGC,NAME_BRG,SATSTAND,iif(case when %s=1 then DBP "
        q += " when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end =0,HJUAL,case when %s=1 then DBP  "
        q += " when %s=2 then HJUALASKIN  when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end) AS HJUAL, "
        q += " iif(case when %s=1 then DBP "
        q += " when %s=2 then HJUALASKIN when %s=3 then HJUALSUKARELA "
        q += " when %s=4 then HPOKOK else hjual end =0,0,case when %s=1 then 1  "
        q += " when %s=2 then 1  when %s=3 then 1 "
        q += " when %s=4 then 0 else 0 end) AS STATUS, "
        q += " TTYPEC,B.STATUSPRODUK,A.SATKEKUATAN,KEKUATAN  "
        q += " FROM BARANG A INNER JOIN PRODUKOBAT B ON  A.TTYPEC=B.PRD_ID "
        q += " where AKTIF<>1 and name_brg like %s and A.BRANCH=%s order by BARANGC "

        result = Globals().getDataQuery(
            q,
            [
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                tarifobat,
                nama,
                cabang_id,
            ],
        )

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getHistoryBarang(request):
    cabang_id = request.session["kdCabang"]
    kode_barang = request.GET["kode_barang"]
    q = "select c.NAME_WH,a.BARANGC, a.NAME_BRG, a.SATSTAND, "
    q += "CAST(((isnull(b.FSBSALDO_AWAL,0)+isnull(b.FSBRPENJUALAN,0)+isnull(b.FSBPEMBELIAN,0)+isnull(b.FSBLAIN_MASUK,0)+isnull(b.FSBRKANVAS,0)) - "
    q += "(isnull(b.FSBPENJUALAN,0)+isnull(b.FSBRPEMBELIAN,0)+isnull(b.FSBLAIN_KELUAR,0)+isnull(b.FSBKANVAS,0))) AS INT) AS STOK "
    q += "from BARANG a left join SALDOBARANG b on "
    q += "a.BARANGC = b.FSBBRG_ID  left join WAREHOUSE c on "
    q += "b.FSBWH_ID=c.WH_ID where a.BARANGC =  %s AND a.BRANCH =  %s "
    result = Globals().getDataQuery(q, [kode_barang, cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def crudResepRJ(request):
    json_data_list = []
    edit = {}
    if request.method == "POST":
        q = request.POST["q"]
        now = datetime.now()
        if q == "entryResepRJ":
            try:
                NODATE = "{}".format(now.strftime("%Y-%m-%d"))
                if "FDRRACIK_ID" in request.POST:
                    FDRRACIK_ID = request.POST["FDRRACIK_ID"]  # RACIKID
                else:
                    FDRRACIK_ID = "NULL"  # RACIKID
                NORESEPRJ = request.POST["NOTRANSAKSI"]
                isi = (
                    request.POST["DOKTER_ID"],
                    request.POST["TANGGAL"],
                    NORESEPRJ,
                    request.POST["BUKTI_ID"],
                    "NULL",
                    request.POST["BRG_ID"],
                    request.POST["BRGN"],
                    request.POST["SATUAN"],
                    request.POST["QTY"],
                    request.POST["QTYOUT"],
                    request.POST["DOSIS"],
                    request.POST["SIGNAF"],
                    request.POST["DOSIS2"],
                    request.POST["SIGNAS"],
                    request.POST["SIGNAW"],
                    request.POST["SIGNA"],
                    request.session["user_id"],
                    FDRRACIK_ID,
                    NODATE,
                    "NULL",
                    "NULL",
                    request.POST["StatusAUD"],
                )
                query = (
                    "EXEC add_EresepDokter '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'"
                    % isi
                )
                # print(query)
                try:
                    result_set = Globals().getDataSP(query, [], setIndex=2)

                    if "FDRRACIK_ID" in request.POST:
                        queryFDRRACIK_ID = "UPDATE ERESEPDOKTERD SET FDRRESEP=(SELECT MIN(FDRRESEP) FROM ERESEPDOKTERD WHERE FDRRACIK_ID='{}') WHERE FDRRACIK_ID='{}'".format(
                            request.POST["FDRRACIK_ID"], request.POST["FDRRACIK_ID"]
                        )
                        Globals().executeQuery(queryFDRRACIK_ID)
                    if request.POST["StatusAUD"] == "A":
                        if int(len(result_set)) > 0:
                            try:
                                edit["success"] = True
                                edit["message"] = "" + result_set[0]["FDRBUKTI_ID"]
                                if "SIGNAMODE" in request.POST:
                                    queryFDRRACIK_ID = "UPDATE ERESEPDOKTERD SET FDRSIGNAMODE='{}' WHERE FDRBUKTI_ID='{}' AND FDRBRG_ID='{}'".format(
                                        request.POST["SIGNAMODE"],
                                        result_set[0]["FDRBUKTI_ID"],
                                        request.POST["BRG_ID"],
                                    )
                                    Globals().executeQuery(queryFDRRACIK_ID)
                            except Exception as e:
                                edit["success"] = False
                                edit["message"] = result_set[0]["error_message"]

                        else:
                            edit["success"] = False
                            edit["message"] = "Gagal Insert"
                    else:
                        edit["success"] = True
                        edit["message"] = "Sukses {}".format(request.POST["StatusAUD"])
                except Exception as e:
                    edit["success"] = False
                    edit["message"] = str(e)
            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        elif q == "editResepRJ":
            try:
                ks = None
                isi = '"{}"'.format(request.POST["DOKTER_ID"])
                isi = '{},"{}"'.format(isi, request.POST["TANGGAL"])  # tanggal
                isi = '{},"{}"'.format(isi, request.POST["NOTRANSAKSI"])  # NOTRANSAKSI
                isi = '{},"{}"'.format(isi, request.POST["BUKTI_ID"])  # BUKTI_ID
                isi = '{},"{}"'.format(isi, request.POST["batchno"])  # batchno
                isi = '{},"{}"'.format(isi, request.POST["BRG_ID"])  # BRG_ID
                isi = '{},"{}"'.format(isi, request.POST["BRGN"])  # BRGN
                isi = '{},"{}"'.format(isi, request.POST["SATUAN"])  # SATUAN
                isi = '{},"{}"'.format(isi, request.POST["QTY"])  # QTY
                isi = '{},"{}"'.format(isi, request.POST["QTYOUT"])  # QTYOUT
                isi = '{},"{}"'.format(isi, request.POST["DOSIS"])  # DOSIS
                isi = '{},"{}"'.format(isi, request.POST["SIGNAF"])  # SIGNAF
                isi = '{},"{}"'.format(isi, request.POST["DOSIS2"])  # DOSIS2
                isi = '{},"{}"'.format(isi, request.POST["SIGNAS"])  # SIGNAS
                isi = '{},"{}"'.format(isi, request.POST["SIGNAW"])  # SIGNAW
                isi = '{},"{}"'.format(isi, request.POST["SIGNA"])  # SIGNA
                isi = '{},"{}"'.format(isi, request.session["user_id"])  # USERRS
                if "FDRRACIK_ID" in request.POST:
                    isi = '{},"{}"'.format(isi, request.POST["FDRRACIK_ID"])  # RACIKID
                else:
                    isi = '{},"NULL"'.format(isi)  # RACIKID
                isi = '{},"{}"'.format(isi, now.strftime("%Y-%m-%d"))  # tanggal
                isi = '{},"NULL"'.format(isi)  # Formatheader
                isi = '{},"NULL"'.format(isi)  # OutputNoBukti
                isi = '{},"{}"'.format(isi, request.POST["StatusAUD"])  # StatusAUD
                query = "EXEC add_EresepDokter {}".format(isi)
                Globals().executeQuery(query)
                edit["success"] = True
                edit["message"] = "Sukses"
            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        elif q == "saveEResepManual":
            query = " "
            query += " DECLARE @KD_DOKTER varchar(20);   "
            query += " DECLARE @FDRRACIK_ID varchar(20);  "
            query += " DECLARE @NO_TRANSAKSI varchar(20); "
            query += " DECLARE @TANGGAL datetime;  "
            query += " SET @KD_DOKTER='{}' ".format(request.POST["DOKTER_ID"])
            query += " SET @NO_TRANSAKSI='{}' ".format(request.POST["NO_TRANSAKSI"])
            query += " SET @TANGGAL='{}' ".format(request.POST["TANGGAL"])
            query += " EXEC AUD_ERESEP_MANUAL @NO_TRANSAKSI,%s,@KD_DOKTER,%s,@TANGGAL,@KD_DOKTER"
            NORESEP = Globals().input(request.POST, "FDRBUKTI_ID", None)
            if NORESEP == "NULL":
                NORESEP = None
            # print(query, [NORESEP,nl2br(Globals().input(request.POST,'FHRRESEPTEXT',None))])
            Globals().executeQuery(
                query,
                [NORESEP, nl2br(Globals().input(request.POST, "FHRRESEPTEXT", None))],
            )
            edit["success"] = True
            edit["message"] = "Sukses Simpan"
        elif q == "kirimEntryResepRJ":
            try:
                # query = "update  ERESEPDOKTER set FHRSTATUS=1,FHRRESEPTEXT='{}' where  FHRNO_TRANSAKSI='{}'".format(
                #     getEresepTxT(request.POST["KPNO_TRANSAKSI"]),
                #     request.POST["FHRNO_TRANSAKSI"],
                # )
                query = "update  ERESEPDOKTER set FHRSTATUS=1 where  FHRNO_TRANSAKSI='{}'".format(
                    request.POST["FHRNO_TRANSAKSI"],
                )
                edit["success"] = True
                edit["message"] = "Success Kirim"
                Globals().executeQuery(query)
                # prints(rows)
                # return HttpResponse(json_data, content_type="application/json")
                # cursor = connection.cursor()
                # q = "select * from CABANG"
                # cursor.execute(q)
                # cabang = Globals().dictfetchall(cursor)
                # if 'jns_cabang' in cabang[0]:
                # 	jns_cabang = cabang[0]['jns_cabang']
                # 	if jns_cabang=="KLINIK":

                # 		#cek status bridging
                # 		cursorqKPendaftaran = connection.cursor()
                # 		qKPendaftaran=" SELECT * FROM KUNJUNGANPASIEN"
                # 		qKPendaftaran+=" LEFT JOIN CUSTOMER ON KUNJUNGANPASIEN.KD_CUSTOMER=CUSTOMER.CUSID "
                # 		qKPendaftaran+=" LEFT JOIN KELOMPOKCUSTOMER ON CUSTOMER.KELOMPOK_ID=KELOMPOKCUSTOMER.FMKCUST_ID "
                # 		qKPendaftaran+=" WHERE KELOMPOKCUSTOMER.STATUSBRIDGE='1' "
                # 		qKPendaftaran+=" AND  KUNJUNGANPASIEN.KPNO_TRANSAKSI='{}'".format(request.POST['KPNO_TRANSAKSI'])
                # 		cursorqKPendaftaran.execute(qKPendaftaran)
                # 		dataCustomer = Globals().dictfetchall(cursorqKPendaftaran)
                # 		# prints(qKPendaftaran)
                # 		jum=int(len(dataCustomer))
                # 		# prints(jum)
                # 		if jum>0:
                # 			bridgingObat=crudBridgingBPJSObat(request.POST['KPNO_TRANSAKSI'],request.POST['noKunjungan'])
                # 			if bridgingObat['success']==True:
                # 				edit['success']=True
                # 				edit['message']="Success Kirim"
                # 			else:
                # 				edit['success']=False
                # 				edit['message']=bridgingObat['message']
                # 		else:
                # 			edit['success']=True
                # 			edit['message']="Success Kirim"
                # 	else:
                # 		query="select  * FROM ERESEPDOKTER  where  FHRSTATUS=1 AND FHRNO_TRANSAKSI='{}'".format(request.POST['FHRNO_TRANSAKSI'])
                # 		cursor.execute(query)
                # 		rows = cursor.fetchall()
                # 		jum=int(len(rows))
                # 		if jum<1:
                # 			edit['success']=False
                # 			edit['message']="Gagal Kirim"
                # 		else:
                # 			edit['success']=True
                # 			edit['message']="Success Kirim"
                # else:
                # 	query="select  * FROM ERESEPDOKTER  where  FHRSTATUS=1 AND FHRNO_TRANSAKSI='{}'".format(request.POST['FHRNO_TRANSAKSI'])
                # 	cursor.execute(query)
                # 	rows = cursor.fetchall()
                # 	jum=int(len(rows))
                # 	if jum<1:
                # 		edit['success']=False
                # 		edit['message']="Gagal Kirim"
                # 	else:
                # 		edit['success']=True
                # 		edit['message']="Success Kirim"

            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        elif q == "copyResepRJ":
            try:
                query = "EXEC DUPLICATE_RESEP '{}','{}',NULL,NULL".format(
                    request.POST["NO_RESEP"], request.POST["NO_TRANS"]
                )
                edit["success"] = True
                edit["message"] = "Method Valid"
                copyResep = Globals().executeQuery(query)
                query = (
                    "select  * FROM ERESEPDOKTER  where  FHRNO_TRANSAKSI='{}'".format(
                        copyResep[0]["nomor"]
                    )
                )
                rows = Globals().executeQuery(query)
                jum = int(len(rows))
                if jum < 1:
                    edit["success"] = False
                    edit["message"] = "Gagal Buat Resep"
                else:
                    edit["success"] = True
                    edit["message"] = "Success Buat Resep"
            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        elif q == "deleteObatResep":
            try:
                query = "delete from ERESEPDOKTERD where FDRBUKTI_ID ='{}' and FDRRESEP='{}'".format(
                    request.POST["FDRBUKTI_ID"], request.POST["FDRRESEP"]
                )
                edit["success"] = True
                edit["message"] = "Method Valid"
                Globals().executeQuery(query)
                query = "Select * from ERESEPDOKTERD where FDRBUKTI_ID ='{}' and FDRRESEP='{}'".format(
                    request.POST["FDRBUKTI_ID"], request.POST["FDRRESEP"]
                )
                rows = Globals().executeQuery(query)
                jum = int(len(rows))
                if jum > 0:
                    edit["success"] = False
                    edit["message"] = "Gagal Hapus"
                else:
                    edit["success"] = True
                    edit["message"] = "Success Hapus"

            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        elif q == "batalkanResepRJ":
            try:
                query = "UPDATE ERESEPDOKTER SET FHRSTATUS='0' where FHRBUKTI_ID='{}'".format(
                    request.POST["FHRBUKTI_ID"]
                )
                edit["success"] = True
                edit["message"] = "Method Valid"
                Globals().executeQuery(query)
                query = "Select * from ERESEPDOKTER where FHRBUKTI_ID ='{}' and FHRSTATUS='0'".format(
                    request.POST["FHRBUKTI_ID"]
                )
                rows = Globals().getDataQuery(query)
                jum = int(len(rows))
                if jum > 0:
                    edit["success"] = True
                    edit["message"] = "Success Batal Resep"
                else:
                    edit["success"] = False
                    edit["message"] = "Gagal Batal Resep"

            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        elif q == "updatePengobatanResepRJ":
            try:
                queryFDRRACIK_ID = (
                    " UPDATE MR_DIAGNOSA SET MRDTERAPI='%s' WHERE MRDNO_TRANSAKSI='%s'"
                )
                # cursor.execute(queryFDRRACIK_ID,[request.POST['MRDTERAPI'],request.POST['MRDNO_TRANSAKSI']])
                Globals().executeQuery(
                    queryFDRRACIK_ID
                    % (request.POST["MRDTERAPI"], request.POST["MRDNO_TRANSAKSI"])
                )

                edit["success"] = True
                edit["message"] = "Success Update"

            except requests.exceptions.RequestException as e:
                prints(e)
                raise
        else:
            edit["success"] = False
            edit["message"] = "Method Not Valid"
    else:
        edit["success"] = False
        edit["message"] = "Method Not Valid"
    json_data_list.append(edit)
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def deleteEresep(request):
    query = "  DELETE ERESEPDOKTERD "
    query += "  WHERE  "
    query += " FDRBUKTI_ID in (SELECT FHRNO_TRANSAKSI FROM ERESEPDOKTER WHERE FHRBUKTI_ID=%s AND KD_CABANG=%s)"
    deleteItem = Globals().executeQuery(
        query,
        [
            Globals().input(request.POST, "NO_TRANSAKSI", None),
            request.session["kdCabang"],
        ],
    )

    query = "  DELETE ERESEPDOKTER "
    query += "  WHERE  "
    query += " FHRBUKTI_ID=%s AND KD_CABANG=%s"
    deleteHeader = Globals().executeQuery(
        query,
        [
            Globals().input(request.POST, "NO_TRANSAKSI", None),
            request.session["kdCabang"],
        ],
    )

    result = {"success": True, "message": "Sukses Hapus"}
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def nl2br(string, is_xhtml=True):
    if is_xhtml:
        return string.replace("\n", "<br />\n")
    else:
        return string.replace("\n", "<br>\n")


## ERESEP ##


def getRiwayatPemeriksaanByNORMDetail(request):
    if request.GET["jenis"] == "CPPT_DR":
        q = "SELECT TOP 12 dbo.EMR_GET_USER(A.CPTDUSER_ID) as USER_EMR,CONVERT(varchar,A.CPTDCREATED_AT,113) as TTVUPDATED_ATS, "
        q += " A. CPTDNO_TRANSAKSI_RJ, CPTDNO_TRANSAKSI, CPTDCREATED_AT, CPTDUPDATED_AT, CPTDUSER_ID, CPTDUSER_TYPE, CPTDUSER_NAME, CPTD_S, "
        q += " LTRIM(CONVERT (VARCHAR(MAX),CPTD_A)+' '+ISNULL((stuff( (select '; ' + cast(B.MRPKD_PENYAKIT as varchar(max))+' '+cast(E.PENYAKIT as varchar(max))+' '+cast(C.MSDIAGNOSANAMA as varchar(max))  "
        q += " from MR_PENYAKIT B INNER JOIN PENYAKIT E ON B.MRPKD_PENYAKIT = E.KD_PENYAKIT   "
        q += " INNER JOIN STATUSDIAGNOSA C ON C.MSDIAGNOSAID=B.MRPSTAT_DIAG "
        q += " WHERE B.MRPNO_TRANSAKSI =A.CPTDNO_TRANSAKSI_RJ for xml path ('')), 1, 1, '')),'')) AS CPTD_A, "
        q += " LTRIM(ISNULL(CONVERT (VARCHAR(MAX),CPTD_P),'')+' '+ISNULL((stuff((select ';' + cast(BB.MRTKD_TINDAKAN as varchar(max))+' '+cast(EE.FMI9KETERANGAN as varchar(max))  "
        q += " from MR_TINDAKAN BB INNER JOIN MR_ICD9 EE ON BB.MRTKD_TINDAKAN = EE.FMI9KODE "
        q += " WHERE BB.MRTNOTRANSAKSI =A.CPTDNO_TRANSAKSI_RJ for xml path ('')), 1, 1, '')),'')) AS CPTD_P, "
        q += " LTRIM(ISNULL(CONVERT (VARCHAR(MAX),CPTD_O),'')+' '+ISNULL((stuff((select ';' +'Sistole: '+ cast(BBB.TTVTSISTOL as varchar(max))+'; Diastole: '+cast(BBB.TTVDIASTOL as varchar(max)) "
        q += " +'; Nadi: '+cast(BBB.TTVNADI as varchar(max))+'; Suhu: '+cast(BBB.TTVSUHU as varchar(max))+'; Respirasi: '+cast(BBB.TTVNAFAS as varchar(max))+'; SPO2: '+cast(BBB.TTVO2 as varchar(max)) "
        q += " +'; Berat Badan: '+cast(BBB.TTVBERAT_BADAN as varchar(max))+'; Tinggi Badan: '+cast(BBB.TTVTINGGI_BADAN as varchar(max))+'; L.Perut: '+cast(BBB.TTV_LINGKAR_PERUT as varchar(max)) "
        q += " +'; L.Kepala: '+cast(isnull(BBB.TTV_LINGKAR_KEPALA,'') as varchar(max)) "
        q += " from  EMRRJ_TTV BBB  "
        q += " WHERE BBB.TTVNO_TRANSAKSI_RJ =A.CPTDNO_TRANSAKSI_RJ for xml path ('')), 1, 1, '')),'')) AS CPTD_O, "
        q += " CPTD_GABUNGAN,CPTDRESEP_DOKTER, CPTDRESEP_ID, KD_CABANG, CPTD_ANAMNESA, CPTD_ANAMNESA_KET1, CPTD_ANAMNESA_KET2, CPTD_KELUHANUTAMA, CPTD_RIWAYAT_SKG, CPTD_KD_PASIEN "
        q += " FROM  EMRRJ_CPPT_DOKTER A  "
        q += " WHERE A.CPTDNO_TRANSAKSI_RJ='{}'".format(request.GET["no_transaksi"])
    elif request.GET["jenis"] == "CPPT_PRW":
        q = " SELECT dbo.EMR_GET_USER(A.CPTPUSER_ID) as USER_EMR,CONVERT(varchar,A.CPTPCREATED_AT,113) as TTVUPDATED_ATS,A.*,TTV.*,CONVERT(date,TTV.TTV_HPHT) as TTV_HPHTS,CONVERT(date,TTV.TTV_HPL) as TTV_HPLS "
        q += " FROM  EMRRJ_CPPT_PERAWAT A "
        q += " LEFT JOIN EMRRJ_TTV TTV ON A.CPTPNO_TRANSAKSI_RJ=TTV.TTVNO_TRANSAKSI_RJ"
        q += " WHERE A.CPTPNO_TRANSAKSI_RJ='{}'".format(request.GET["no_transaksi"])
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getHistoricalBPJSpasien(request):
    nomor = request.GET["nomor"]
    # -------
    kdCabang = request.session["kdCabang"]
    # BPJS_USERPCARE=request.session['BPJS_USERPCARE']
    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/kunjungan/peserta/" + nomor
    method = "get"
    data = Globals().bridgeBPJS(url, method, kdCabang)
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getriwayat(request):
    pasien = request.GET["pasien"]
    kdCabang = request.session["kdCabang"]
    q = " select convert (varchar(10),TTV_TGL_CUTI,120) as TTV_TGL_CUTI,a.TTV_LAMA_CUTI,a.TTV_KET_CUTI,b.KPKD_PASIEN,b.KPKD_DOKTER,c.MRPKD_PENYAKIT,d.NAMAPASIEN,e.FMDDOKTERN "
    q += " from EMRRJ_TTV a inner join KUNJUNGANPASIEN b on a.TTVNO_TRANSAKSI_RJ=b.KPNO_TRANSAKSI and b.KD_CABANG=%s "
    q += " inner join PASIEN  d on b.KPKD_PASIEN=d.KD_PASIEN "
    q += " inner join DOKTER  e on b.KPKD_DOKTER=e.FMDDOKTER_ID "
    q += " inner join MR_PENYAKIT c on b. KPNO_TRANSAKSI=c.MRPNO_TRANSAKSI and c.KD_CABANG=b.KD_CABANG "
    q += " where TTV_LAMA_CUTI is not null and b.KPKD_PASIEN=%s "
    result = Globals().getDataQuery(q, [kdCabang, pasien])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getjkn(request):
    tglAwal = request.GET["tglAwal"]
    tglAkhir = request.GET["tglAkhir"]
    kdCabang = request.session["kdCabang"]
    q = " SELECT CONVERT(varchar,FAPTGL_APPOITMENT,105) as TGL_APP, "
    q += " DOKTER.FMDDOKTERN, "
    q += " POLIKLINIK.FMPKLINIKN, "
    q += " APPOINTMENT_PASIEN.* FROM APPOINTMENT_PASIEN "
    q += " LEFT JOIN DOKTER ON APPOINTMENT_PASIEN.FAPDOKTER_ID=DOKTER.FMDDOKTER_ID "
    q += " LEFT JOIN POLIKLINIK ON APPOINTMENT_PASIEN.FAPPOLI=POLIKLINIK.FMPKLINIK_ID "
    q += "where (FAPTGL_APPOITMENT >= %s and FAPTGL_APPOITMENT<=%s  ) and (CABANG = %s)  "
    result = Globals().getDataQuery(q, [tglAwal, tglAkhir, kdCabang])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def cekIcare(request):
    # -------
    nomor = request.GET["nomor"]
    kdCabang = request.session["kdCabang"]
    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = "https://apijkn.bpjs-kesehatan.go.id/wsihs/api/pcare/validate"
    # url = "https://apijkn-dev.bpjs-kesehatan.go.id/ihs_dev/api/pcare/validate"
    method = "post2"
    payload = {
        "param": nomor,
    }
    data = Globals().bridgeBPJSICARE(url, method, kdCabang, payload)
    # print(data)
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def crudBridgingBPJSLab(request):
    kdApp = "095"
    response = {}
    kdCabang = request.session["kdCabang"]
    q = "select * from CABANG WHERE CABANG_ID=%s "
    cabang = Globals().getDataQuery(q, [kdCabang])
    tanggal = datetime.now().strftime("%d-%m-%Y")
    # request.POST["tglPelayanan"].strftime("%d-%m-%Y")
    url_pcare = getattr(env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id")
    url = url_pcare + "/MCU"
    if request.POST["kdMCU"] == "0":
        method = "post"
        payload = {
            "kdMCU": 0,
            "noKunjungan": request.POST["noKunjungan"],
            "kdProvider": cabang[0]["userncc"],
            "tglPelayanan": tanggal,
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
        res = Globals().bridgeBPJS(url, method, kdCabang, payload)
        # print(payload)
        # print(res)
        datas = res
        # prints(datas)
        if datas["metaData"]["code"] == 201:
            response = {"success": True, "message": "Berhasil Insert"}
        else:
            response = {"success": False, "message": datas["metaData"]["message"]}
    else:
        method = "put"
        payload = {
            "kdMCU": request.POST["kdMCU"],
            "noKunjungan": request.POST["noKunjungan"],
            "kdProvider": cabang[0]["userncc"],
            "tglPelayanan": tanggal,
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

        res = Globals().bridgeBPJS(url, method, kdCabang, payload)
        datas1 = res
        if datas1["metaData"]["code"] == 200:
            response = {"success": True, "message": "Berhasil Insert"}
        else:
            response = {"success": False, "message": datas1["metaData"]["message"]}

    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getBPJSMCU(request):
    noKunjungan = request.GET["noKunjungan"]
    # -------
    kdCabang = request.session["kdCabang"]
    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/MCU/kunjungan/" + noKunjungan
    method = "get"
    data = Globals().bridgeBPJS(url, method, kdCabang)
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def deleteBPJSMCU(request):
    noKunjungan = request.GET["noKunjungan"]
    kdMCU = request.GET["kdMCU"]
    # -------
    kdCabang = request.session["kdCabang"]
    url_pcare = getattr(
        env, "URL_PCARE", "https://new-api.bpjs-kesehatan.go.id/pcare-rest-v3.0"
    )
    url = url_pcare + "/MCU/" + kdMCU + "/kunjungan/" + noKunjungan
    method = "DELETE"
    data = Globals().bridgeBPJS(url, method, kdCabang)
    if data["metaData"]["code"] == 412:
        response = {"success": True, "message": "Berhasil hapus"}
    else:
        response = {"success": False, "message": data["metaData"]["message"]}

    json_data = json.dumps(response, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def getHistoricalsurvei(request):
    nomor = request.GET["nomor"]  # "0000590481066"
    payload = {
        "no_bpjs": nomor,
    }
    url = "https://kuisioner.medisimed.com/api/get_resume"
    res = requests.get(url, payload).json()
    json_data = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


# FTW
def save_ftw(request):
    try:
        q = "SET NOCOUNT ON;"
        q += " EXEC EMRJ_AUD_FTW "
        q += " %s ,"  # 1@FTW_NOTRANS_RJ varchar (60),
        q += " %s ,"  # 2@FTW_NOTRANS varchar (60) NULL,
        q += " %s ,"  # 3@FTW_PERUSAHAAN nvarchar (50) NULL,
        q += " %s ,"  # 4@FTW_TGL_NILAI datetime  NULL,
        q += " %s ,"  # 5@FTW_KELUHAN_UTAMA varchar (max) NULL,
        q += " %s ,"  # 6@FTW_RWYT_SKT_SKRG varchar (max) NULL,
        q += " %s ,"  # 7@FTW_RWYT_SKT_DL varchar (max) NULL,
        q += " %s ,"  # 8@FTW_BIASA varchar (max) NULL,
        q += " %s ,"  # 9@FTW_KELUHAN_RASA varchar (max) NULL,
        q += " %s ,"  # 10@FTW_PMR_FISIK varchar (max) NULL,
        q += " %s ,"  # 11@FTW_PMR_PENUNJANG varchar (max) NULL,
        q += " %s ,"  # 12@FTW_KRITERIA_SEMBUH varchar (max) NULL,
        q += " %s ,"  # 13@FTW_BAHAYA varchar (max) NULL,
        q += " %s ,"  # 14@FTW_BAHAYA_NOTE varchar (max) NULL,
        q += " %s ,"  # 15@FTW_KESIMPULAN varchar (max) NULL,
        q += " %s ,"  # 16@FTW_REKOMENDASI varchar (max) NULL,
        q += " %s ,"  # 17@FTW_KD_PASIEN varchar (50) NULL,
        q += " %s ,"  # 18@FTW_CABANG varchar (50) NULL,
        q += " %s ,"  # 19@FTW_HARIAN varchar (50) NULL,
        q += " %s ,"  # 20@FTW_KEMAMPUAN varchar (50) NULL,
        q += " %s ;"  # 21@STATUS_AUD nvarchar(5) = 'A'

        proc_param = [
            Globals().input(request.POST, "noTrans"),  # 1@FTW_NOTRANS_RJ varchar (60),
            Globals().input(
                request.POST, "FTW_NOTRANS"
            ),  # 2@FTW_NOTRANS varchar (60) NULL,
            Globals().input(
                request.POST, "FTW_PERUSAHAAN"
            ),  # 3@FTW_PERUSAHAAN nvarchar (50) NULL,
            Globals().input(
                request.POST, "FTW_TGL_NILAI"
            ),  # 4@FTW_TGL_NILAI datetime  NULL,
            Globals().input(
                request.POST, "FTW_KELUHAN_UTAMA"
            ),  # 5@FTW_KELUHAN_UTAMA varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_RWYT_SKT_SKRG"
            ),  # 6@FTW_RWYT_SKT_SKRG varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_RWYT_SKT_DL"
            ),  # 7@FTW_RWYT_SKT_DL varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_BIASA"
            ),  # 8@FTW_BIASA varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_KELUHAN_RASA"
            ),  # 9@FTW_KELUHAN_RASA varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_PMR_FISIK"
            ),  # 10@FTW_PMR_FISIK varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_PMR_PENUNJANG"
            ),  # 11@FTW_PMR_PENUNJANG varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_KRITERIA_SEMBUH"
            ),  # 12@FTW_KRITERIA_SEMBUH varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_BAHAYA"
            ),  # 13@FTW_BAHAYA varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_BAHAYA_NOTE"
            ),  # 14@FTW_BAHAYA_NOTE varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_KESIMPULAN"
            ),  # 15@FTW_KESIMPULAN varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_REKOMENDASI"
            ),  # 16@FTW_REKOMENDASI varchar (max) NULL,
            Globals().input(
                request.POST, "FTW_KD_PASIEN"
            ),  # 17@FTW_KD_PASIEN varchar (50) NULL,
            request.session["kdCabang"],  # 18@FTW_CABANG varchar (50) NULL,
            Globals().input(
                request.POST, "FTW_HARIAN"
            ),  # 19@FTW_HARIAN nvarchar (max) NULL,
            Globals().input(
                request.POST, "FTW_KEMAMPUAN"
            ),  # 20@FTW_KEMAMPUAN nvarchar (max) NULL,
            "A",  # 21@STATUS_AUD nvarchar(5) = 'A'
        ]
        # print(q % proc_param)
        # print(q % tuple(proc_param))
        result_set = Globals().getDataSP(q, proc_param)
        json_data = json.dumps(result_set, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print("coba")


def get_ftw(request):
    noTrans = request.GET["noTrans"]
    kdCabang = request.session["kdCabang"]
    q = " SELECT * FROM EMRRJ_FTW A where A.FTW_NOTRANS_RJ=%s   "
    result = Globals().getDataQuery(q, [noTrans])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


# FTW
