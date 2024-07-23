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
from . import views_pcare
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def isLogin(request):
    if "userauth" in request.session:
        is_login = request.session["userauth"]
    else:
        is_login = False
    return is_login


def getMRICD9(request):
    cursor = connection.cursor()
    if "key" in request.GET:
        key = "%" + request.GET["key"] + "%"
        q = " select TOP 100 FMI9KODE,FMI9KETERANGAN,FMI9KETERANGAN2  "
        q += " from MR_ICD9 WHERE FMI9KODE like %s or FMI9KETERANGAN like %s "
        q += " or FMI9KETERANGAN2 like %s order by FMI9KODE"
        cursor.execute(q, [key, key, key])
        result = Globals().dictfetchall(cursor)
    else:
        q = "select FMI9KODE,FMI9KETERANGAN,FMI9KETERANGAN2 from MR_ICD9 order by FMI9KODE"
        result = Globals().getData(q)
    edit = json.dumps(result, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(edit, content_type="application/json")


def getDignosaKerjaCPPT(request):
    cursor = connection.cursor()
    q = " SELECT A.*,B.MSKASUSNAMA,C.MSDIAGNOSANAMA,D.PENYAKIT FROM MR_PENYAKIT A"
    q += " JOIN STATUSKASUS B ON B.MSKASUSID = A.MRPKASUS "
    q += " JOIN STATUSDIAGNOSA C ON C.MSDIAGNOSAID = A.MRPSTAT_DIAG "
    q += " JOIN PENYAKIT D ON D.KD_PENYAKIT  = A.MRPKD_PENYAKIT"
    q += " WHERE MRPNO_TRANSAKSI = %s"
    proc_param = [Globals().input(request.GET, "no_transaksi_ri")]
    cursor.execute(q, proc_param)
    result_set = Globals().dictfetchall(cursor)
    json_data = json.dumps(result_set, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


def setSession(request):
    json_data_list = []
    edit = {}
    if "q" in request.GET:
        q = request.GET["q"]
        if q == "entryResepRJ":
            q1 = "select a.KPNO_TRANSAKSI,KPTGL_PERIKSA,KPJAM_MASUK,KPKD_POLY,KPKD_DOKTER,c.FMDDOKTERN,a.KPKD_PASIEN, KD_CUSTOMER,d.NAME,b.NAMAPASIEN,tgl_lahir,ALAMAT, JENIS_KELAMIN"
            q2 = " from KUNJUNGANPASIEN a,pasien b,Dokter c,CUSTOMER d "
            q3 = " where a.KPKD_PASIEN=b.KD_PASIEN  and c.FMDDOKTER_ID=a.KPKD_DOKTER and a.KD_CUSTOMER=d.CUSID and "
            q4 = " A.KPNO_TRANSAKSI='{}'".format(request.GET["noTrans"])
            query = "{}{}{}{}".format(q1, q2, q3, q4)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            # prints(rows[0][4])
            # prints(rows[0][5])
            # return HttpResponse(json_data, content_type="application/json")
            jum = int(len(rows))
            if jum > 0:
                request.session["noTrans"] = request.GET["noTrans"]
                request.session["FMDDOKTER_ID"] = rows[0][4]
                request.session["FMDDOKTERN"] = rows[0][5]
                request.session.modified = True
                edit["success"] = True
                edit["message"] = "Success NoTrans Valid"

                query1 = "SELECT KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID='{}'".format(
                    rows[0][3]
                )
                cursor = connection.cursor()
                cursor.execute(query1)
                rows1 = cursor.fetchall()
                jum1 = int(len(rows1))
                if jum > 0:
                    edit["kdAssesment"] = rows1[0][0]
                else:
                    edit["kdAssesment"] = "-"
                # prints('kdAssesment')
                # prints(edit['kdAssesment'])
            else:
                edit["success"] = False
                edit["message"] = "NoTrans Tidak Valid"
        elif q == "selectPasienEMR":
            request.session["noTrans"] = request.GET["noTrans"]
            request.session["dokterId"] = request.GET["dokterId"]
            request.session["dokterN"] = request.GET["dokterN"]
            request.session["noRM"] = request.GET["noRM"]
            request.session["namaPasien"] = request.GET["namaPasien"]
            request.session["assesmentType"] = request.GET["assesmentType"]
            request.session["assesmentId"] = request.GET["assesmentId"]
            request.session.modified = True
            edit["success"] = True
            edit["message"] = "Success"
        elif q == "printResepRJ":
            query = "select  * FROM ERESEPDOKTER  where  FHRSTATUS=1 AND FHRNO_TRANSAKSI='{}'".format(
                request.GET["FHRNO_TRANSAKSI"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            # prints(rows)
            # return HttpResponse(json_data, content_type="application/json")
            jum = int(len(rows))
            if jum > 0:
                request.session["FHRNO_TRANSAKSI"] = request.GET["FHRNO_TRANSAKSI"]
                request.session.modified = True
                edit["success"] = True
                edit["message"] = "Success NoTrans Valid"
            else:
                edit["success"] = False
                edit["message"] = "NoTrans Tidak Valid"
        elif q == "sessionEditRacik":
            request.session["FDRBUKTI_ID"] = request.GET["FDRBUKTI_ID"]
            request.session["FDRRACIK_ID"] = request.GET["FDRRACIK_ID"]
            request.session.modified = True
            edit["success"] = True
            edit["message"] = "Success NoTrans Valid"
        elif q == "delsessionEditRacik":
            del request.session["FDRBUKTI_ID"]
            del request.session["FDRRACIK_ID"]
            request.session.modified = True
            edit["success"] = True
            edit["message"] = "Success NoTrans Valid"
        else:
            edit["success"] = False
            edit["message"] = "Request Tidak Valid"
    else:
        edit["success"] = False
        edit["message"] = "Request Tidak Valid"
    json_data_list.append(edit)
    json_data = json.dumps(json_data_list)
    return HttpResponse(json_data, content_type="application/json")


def getDetailPasienRJ(request):
    if "q" in request.GET:
        q = request.GET["q"]
        if q == "detailKunjungan":
            query = " SELECT a.KPNO_TRANSAKSI, CONVERT(varchar, a.KPTGL_PERIKSA, 105) AS KPTGL_PERIKSA, a.KPKD_POLY, a.KPKD_DOKTER, c.FMDDOKTERN, a.KPKD_PASIEN,"
            query += " a.KD_CUSTOMER, d.NAME, b.NAMAPASIEN, CONVERT(varchar, b.TGL_LAHIR, 105) AS tgl_lahir, CONVERT(varchar, b.TGL_LAHIR, 101) AS tgl_lahir2, b.ALAMAT,IIF (b.JENIS_KELAMIN=1,'L','P') as JENIS_KELAMIN"
            query += " FROM KUNJUNGANPASIEN AS a "
            query += " LEFT JOIN PASIEN AS b ON a.KPKD_PASIEN = b.KD_PASIEN "
            query += " LEFT JOIN DOKTER AS c ON a.KPKD_DOKTER = c.FMDDOKTER_ID"
            query += " LEFT JOIN CUSTOMER AS d ON a.KD_CUSTOMER = d.CUSID"
            query += " WHERE a.KPNO_TRANSAKSI = %s"
            result = Globals().getDataQuery(query, [request.GET["noTrans"]])
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data

        elif q == "detailResep":
            query = " SELECT ISNULL(b.FHRRESEPTEXT, '-') AS FHRRESEPTEXT, a.FDRRESEP, ISNULL(a.FDRRACIK_ID, 'SATUAN') AS FDRRACIK_ID, a.FDRBRG_ID, a.FDRBRGN, a.FDRSATUAN, a.FDRQTY, a.FDRQTYOUT, a.FDRDOSIS, a.FDRSIGNAF, "
            query += "  a.FDRDOSIS2, a.FDRSIGNAS, a.FDRSIGNAW, a.FDRSIGNA, a.FDRBUKTI_ID, b.FHRNO_TRANSAKSI, b.FHRBUKTI_ID, CONVERT(varchar, b.FHRDATE, 20) AS FHRDATE, b.FHRUSER, CONVERT(varchar, b.FHRUPDATE, 20) "
            query += " AS FHRUPDATE, b.FHRSTATUS, c.HJUAL, a.FDRQTY * c.HJUAL AS Total"
            query += " FROM  ERESEPDOKTER AS b "
            query += (
                " LEFT JOIN ERESEPDOKTERD AS a ON b.FHRNO_TRANSAKSI = a.FDRBUKTI_ID "
            )
            query += " LEFT JOIN BARANG AS c ON a.FDRBRG_ID = c.BARANGC and c.BRANCH= LEFT(%s,3)"
            query += " WHERE (b.FHRBUKTI_ID = %s)"
            query += " ORDER BY a.FDRRESEP"
            result = Globals().getDataQuery(
                query, [request.GET["noTrans"], request.GET["noTrans"]]
            )
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "detailKunjunganCPPT":
            query = " SELECT b.NO_ASURANSI, c.KODEDOKTER, ISNULL(NULL, 0) AS tarif_rs, e.FMPKLINIKN, a.KPKD_POLY, k.FMKCUST_ID, k.FMKCUSTN, a.KPNO_TRANSAKSI, "
            query += " CONVERT(varchar, a.KPTGL_PERIKSA, 105) AS KPTGL_PERIKSA, a.KPKD_POLY AS Expr1, a.KPKD_DOKTER, c.FMDDOKTERN, a.KPKD_PASIEN, a.KD_CUSTOMER, "
            query += " d.NAME, b.NAMAPASIEN, CONVERT(varchar, b.TGL_LAHIR, 105) AS tgl_lahir, CONVERT(varchar, b.TGL_LAHIR, 101) AS tgl_lahir2, b.ALAMAT, b.JENIS_KELAMIN, ISNULL(e.KODEASSESMENT, N'') AS KODEASSESMENT "
            query += " FROM KUNJUNGANPASIEN AS a  "
            query += " LEFT JOIN PASIEN AS b ON a.KPKD_PASIEN = b.KD_PASIEN  "
            query += " LEFT JOIN POLIKLINIK AS e ON a.KPKD_POLY = e.FMPKLINIK_ID   "
            query += " LEFT JOIN DOKTER AS c ON a.KPKD_DOKTER = c.FMDDOKTER_ID   "
            query += " LEFT JOIN CUSTOMER AS d  ON a.KD_CUSTOMER = d.CUSID   "
            query += (
                " LEFT JOIN KELOMPOKCUSTOMER AS k  ON d.KELOMPOK_ID= k.FMKCUST_ID    "
            )
            query += " WHERE a.KPNO_TRANSAKSI =%s "
            result = Globals().getDataQuery(query, [request.GET["noTrans"]])
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data

        elif q == "totalDetailResep":
            q1 = "Select SUM((a.FDRQTY*c.Hjual)) As Total "
            q3 = " from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            q4 = " where a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ".format(
                request.GET["noTrans"]
            )
            query = "{}{}{}".format(q1, q3, q4)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "pickerERINDIKASI":
            q1 = "SELECT NO_INDIKASI,NMINDIKASI  FROM ERINDIKASI"
            query = "{}".format(q1)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "pickerObat":
            BARANGC = "%{}%".format(request.GET["barangId"])
            ZATADITIF = "%{}%".format(request.GET["zataditif"])
            NAME_BRG = "%{}%".format(request.GET["barangNama"])
            query = " select  TOP 100 MERK_ID,barangc as BrgId,name_brg as NamaBrg,satstand as Satuan,hjual as Harga,HPOKOK,DBP,HJUALASKIN,HJUALSUKARELA,ZATADITIF"
            query += " from BARANG"
            query += " WHERE BARANGC LIKE %s AND ZATADITIF LIKE %s AND NAME_BRG LIKE %s AND BRANCH=%s"
            query += " order by BARANGC"
            result = Globals().getDataQuery(
                query, [BARANGC, ZATADITIF, NAME_BRG, request.session["kdCabang"]]
            )
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "pickerObatRacik":
            q1 = "select  MERK_ID,barangc as BrgId,name_brg as NamaBrg,satstand as Satuan,hjual as Harga,"
            # q1+="STUFF((select  ' | ' +  a.FSBWH_ID,' ' +  b.name_wh+'= ',  ((isnull(a.FSBSALDO_AWAL,0)+isnull(a.FSBRPENJUALAN,0)+isnull(a.FSBPEMBELIAN,0)+isnull(a.FSBLAIN_MASUK,0)+isnull(a.FSBRKANVAS,0)) -  (isnull(a.FSBPENJUALAN,0)+isnull(a.FSBRPEMBELIAN,0)+isnull(a.FSBLAIN_KELUAR,0)+isnull(a.FSBKANVAS,0))) from  SALDOBARANG a,WAREHOUSE b where  a.FSBWH_ID=b.wh_id and  "
            # q1+="a.FSBBRG_ID=barangc  ORDER BY 3 DESC FOR XML PATH('')),1,1,'') as Persedian,"
            # and a.FSBWH_ID='GO002'
            q2 = " HPOKOK,DBP,HJUALASKIN,HJUALSUKARELA,ZATADITIF,ISNULL(KEKUATAN,0) as KEKUATAN,ISNULL(SATKEKUATAN,'-') as SATKEKUATAN from BARANG "
            q3 = " WHERE KEKUATAN IS NOT NULL AND  SATKEKUATAN IS NOT NULL AND BARANGC LIKE '%{}%' AND ZATADITIF LIKE '%{}%' AND NAME_BRG LIKE '%{}%' AND BRANCH='{}' ".format(
                request.GET["barangId"],
                request.GET["zataditif"],
                request.GET["barangNama"],
                request.session["kdCabang"],
            )
            # q3=" WHERE BARANGC LIKE '%{}%' AND ZATADITIF LIKE '%{}%' AND NAME_BRG LIKE '%{}%' ".format(request.GET['barangId'],request.GET['zataditif'],request.GET['barangNama'])
            q4 = " order by BARANGC  "
            query = "{}{}{}{}".format(q1, q2, q3, q4)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "pickerCaraPakai":
            query = "select FMSWMYT as Materi,FMSWSBL as Signa,FMSWKODE as Kode from ERSIGNAW"
            if "cariSigna" in request.GET:
                query += " where FMSWSBL LIKE '{}{}{}'".format(
                    "%", request.GET["cariSigna"], "%"
                )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "pickerCaraPakaiF":
            query = "SELECT  FMSFMYT as Materi,FMSFSBL as Signa,FMSFKODE as Kode FROM ERSIGNAF"
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "pickerCaraPakaiS":
            query = "SELECT  FMSSMYT as Materi,FMSSSBL as Signa,FMSSKODE as Kode FROM ERSIGNAS"
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()

        elif q == "generateResepTXT":
            # pengobatan='ERESEP FORMULARIUM:'
            # # q1="Select a.FDRRESEP, FDRBRG_ID,FDRBRG_ID2, FDRBRGN, FDRSATUAN,  CAST(FDRQTY AS int) as FDRQTY, CONVERT(varchar(MAX),FDRQTYOUT) as FDRQTYOUT,CONVERT(varchar(MAX),FDRDOSIS) as  FDRDOSIS, FDRSIGNAF,CONVERT(varchar(MAX),FDRDOSIS2) as FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
            # # q2=" ISNULL(CASE WHEN a.FDRSTATUS=0 THEN "
            # # q2+="' da '"
            # # q2+="+(SELECT NAME_BRG FROM BARANG WHERE BARANGC=a.FDRBRG_ID2)+' '"
            # # q2+=" ELSE '' END,'') as FDRBRGDA,"
            # # q2+=" b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,CONVERT(varchar(MAX),c.HJUAL) as HJUAL,CONVERT(varchar(MAX),(a.FDRQTY*c.Hjual))  As Total "
            # # q3=" from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            # # q4=" where a.FDRSTATUS2 IS NOT NULL and a.FDRRACIK_ID='NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ORDER BY FDRRESEP".format(request.GET['noTrans'])
            # # query="{}{}{}{}".format(q1,q2,q3,q4)
            # result = []
            # query=" SELECT a.FDRRESEP, a.FDRBRG_ID, a.FDRBRG_ID2, a.FDRBRGN, a.FDRSATUAN, CAST(a.FDRQTY AS int) AS FDRQTY, CONVERT(varchar(MAX), a.FDRQTYOUT) AS FDRQTYOUT, CONVERT(varchar(MAX), a.FDRDOSIS) AS FDRDOSIS"
            # query+=" , a.FDRSIGNAF, CONVERT(varchar(MAX), a.FDRDOSIS2) AS FDRDOSIS2, a.FDRSIGNAS, a.FDRSIGNAW, a.FDRSIGNA, a.FDRBUKTI_ID, ISNULL(CASE WHEN a.FDRSTATUS = 0 THEN ' da ' +(SELECT NAME_BRG FROM BARANG WHERE BARANGC = a.FDRBRG_ID2 and BRANCH=LEFT(b.FHRBUKTI_ID,3)) + ' ' ELSE '' END, '') AS FDRBRGDA"
            # query+=" , b.FHRNO_TRANSAKSI, b.FHRBUKTI_ID, CONVERT(varchar, b.FHRDATE, 20) AS FHRDATE, b.FHRUSER, CONVERT(varchar, b.FHRUPDATE, 20)  AS FHRUPDATE, b.FHRSTATUS, CONVERT(varchar(MAX), c.HJUAL) AS HJUAL, CONVERT(varchar(MAX), a.FDRQTY * c.HJUAL) AS Total"
            # query+=" FROM ERESEPDOKTERD AS a"
            # query+=" LEFT JOIN ERESEPDOKTER AS b ON a.FDRBUKTI_ID = b.FHRNO_TRANSAKSI "
            # query+=" LEFT JOIN BARANG AS c ON a.FDRBRG_ID = c.BARANGC AND c.BRANCH=LEFT(b.FHRBUKTI_ID,3)"
            # query+=" WHERE (b.FHRBUKTI_ID = '{}') AND (a.FDRSTATUS2 IS NOT NULL) AND (a.FDRRACIK_ID = 'NULL')".format(request.GET['noTrans'])
            # query+=" ORDER BY a.FDRRESEP"
            # # print(query)
            # dataResepNonRacik=Globals().getDataQuery(query,[])
            # #  pengobatan+=obj.FDRBRGN+' '+obj.FDRSIGNA+ ' '+obj.FDRBRGDA+' No.'+obj.FDRQTY+' ; ';

            # for isidataResepNonRacik in dataResepNonRacik:
            # 	pengobatan+='\n %s %s %s No. %s;' % (isidataResepNonRacik['FDRBRGN'],isidataResepNonRacik['FDRSIGNA'],isidataResepNonRacik['FDRBRGDA'],isidataResepNonRacik['FDRQTY'])
            # # print(dataResepNonRacik)

            # no=1
            # # queryAwal="Select DISTINCT a.FDRRACIK_ID from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c  where a.FDRRACIK_ID<>'NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ".format(request.GET['noTrans'])
            # queryAwal=" SELECT DISTINCT a.FDRRACIK_ID"
            # queryAwal+=" FROM ERESEPDOKTERD AS a"
            # queryAwal+=" INNER JOIN ERESEPDOKTER AS b ON a.FDRBUKTI_ID = b.FHRNO_TRANSAKSI"
            # queryAwal+=" INNER JOIN BARANG AS c ON a.FDRBRG_ID = c.BARANGC"
            # queryAwal+=" WHERE (b.FHRBUKTI_ID = %s) AND (a.FDRRACIK_ID <> 'NULL')"
            # dataResepRacikH=Globals().getDataQuery(queryAwal,[request.GET['noTrans']])
            # # print(queryAwal)
            # if int(len(dataResepRacikH))>0:
            # 	pengobatan+='\n #Racikan: '
            # for isidataResepRacikH in dataResepRacikH:
            # 	q1="Select a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
            # 	q2=" ISNULL(CASE WHEN a.FDRSTATUS=0 THEN "
            # 	q2+="' da '"
            # 	q2+="+(SELECT NAME_BRG FROM BARANG WHERE BARANGC=a.FDRBRG_ID2 and BRANCH=LEFT(b.FHRBUKTI_ID,3))+' '"
            # 	q2+=" ELSE '' END,'') as FDRBRGDA,"
            # 	if kdCabang=="13":
            # 		q2+=" (SELECT TOP 1 CONVERT(varchar(max),FERDKEBQTY2)+' '+FERRACIKDQTYJENIS FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}' AND FERRACIKDBRG_ID=FDRBRG_ID AND CEILING(FERRACIKDQTY)=FDRQTY) as FDRKEB,".format(isidataResepRacikH['FDRRACIK_ID'])
            # 	else:
            # 		q2+=" (SELECT TOP 1 CONVERT(varchar(max),FERDKEBQTY2)+' '+FERRACIKDQTYJENIS FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}' AND FERRACIKDBRG_ID=FDRBRG_ID AND FERRACIKDQTY=FDRQTY) as FDRKEB,".format(isidataResepRacikH['FDRRACIK_ID'])
            # 	q2+=" b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,c.HJUAL,(a.FDRQTY*c.Hjual) As Total "
            # 	q3=" from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            # 	q4=" where a.FDRSTATUS2 IS NOT NULL and a.FDRRACIK_ID<>'NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and c.BRANCH=LEFT(b.FHRBUKTI_ID,3) and b.FHRBUKTI_ID='{}' AND a.FDRRACIK_ID='{}' ORDER BY FDRRESEP".format(request.GET['noTrans'],isidataResepRacikH['FDRRACIK_ID'])
            # 	query="{}{}{}{}".format(q1,q2,q3,q4)

            # 	dataResepRacikD=Globals().getDataQuery(query,[])
            # 	for isidataResepRacikD in dataResepRacikD:
            # 		if no==1:
            # 			pengobatan+='\n %s (%s) %s ' %(isidataResepRacikD['FDRBRGN'],isidataResepRacikD['FDRKEB'],isidataResepRacikD['FDRBRGDA'])
            # 		else:
            # 			pengobatan+='\n %s (%s) %s' %(isidataResepRacikD['FDRBRGN'],isidataResepRacikD['FDRKEB'],isidataResepRacikD['FDRBRGDA'])

            # 		# print(pengobatan)
            # 		# print(int(len(dataResepRacikD)))
            # 		if no==int(len(dataResepRacikD)):
            # 			pengobatan+='\n %s' %(isidataResepRacikD['FDRSIGNA'])
            # 		no+=1

            # query="SELECT ISNULL(FHRRESEPTEXT,'') as FHRRESEPTEXT,FHRNO_TRANSAKSI  FROM ERESEPDOKTER where FHRBUKTI_ID='{}'".format(request.GET['noTrans'])
            # dataResepManual=Globals().getDataQuery(query,[])

            # pengobatan+='\n ERESEP NON FORMULARIUM : '

            # for isidataResepManual in dataResepManual:
            # 	pengobatan+='\n %s ' %(isidataResepManual['FHRRESEPTEXT'])
            edit = {}
            edit["success"] = True
            edit["message"] = getEresepTxT(request.GET["noTrans"])
            json_data = json.dumps(edit, cls=DjangoJSONEncoder)
            edit = json_data
        elif q == "pickerDaftarResep":
            query = "select PFKODE,PFKETERANGAN from ERESEPPAKET where PFKDDOKTER='{}' GROUP BY  PFKODE,PFKETERANGAN order by PFKETERANGAN".format(
                request.session["user_id"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "detailDaftarResep":
            query = "Select a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, "
            query += "FDRSIGNA, FDRBUKTI_ID, b.PFKODE, PFKETERANGAN,c.HJUAL,(a.FDRQTY*c.Hjual) As Total  "
            query += "from ERESEPPAKETD a,ERESEPPAKET b,Barang c  "
            query += "where a.FDRBUKTI_ID=b.PFKODE and A.FDRBRG_ID=c.barangc   "
            query += "and b.PFKODE='{}' ORDER BY FDRRESEP ".format(
                request.GET["PFKODE"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "setCaraPakai":
            query = "select FMSWMYT as Materi,FMSWSBL as Signa,FMSWKODE as Kode from ERSIGNAW where FMSWKODE='{}'".format(
                request.GET["FMSWKODE"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "setCaraPakaiS":
            query = "SELECT  FMSSMYT as Materi,FMSSSBL as Signa,FMSSKODE as Kode FROM ERSIGNAS WHERE FMSSKODE='{}'".format(
                request.GET["FMSWKODE"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "setCaraPakaiF":
            query = "SELECT  FMSFMYT as Materi,FMSFSBL as Signa,FMSFKODE as Kode FROM ERSIGNAF WHERE FMSFKODE='{}'".format(
                request.GET["FMSWKODE"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "setPickerSigna":
            queryF = "SELECT  FMSFMYT as Materi,FMSFSBL as Signa,FMSFKODE as Kode FROM ERSIGNAF WHERE FMSFKODE='{}'".format(
                request.GET["FERCKNSIGNAF"]
            )
            queryW = "select FMSWMYT as Materi,FMSWSBL as Signa,FMSWKODE as Kode from ERSIGNAW where FMSWKODE='{}'".format(
                request.GET["FERCKNSIGNAW"]
            )
            queryS = "SELECT  FMSSMYT as Materi,FMSSSBL as Signa,FMSSKODE as Kode FROM ERSIGNAS WHERE FMSSKODE='{}'".format(
                request.GET["FERCKNSIGNAS"]
            )

            json_data_list = []
            edits = {}

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(queryF)
            ERSIGNAF = []
            ERSIGNAF = Globals().dictfetchall(cursor)

            cursor.execute(queryW)
            ERSIGNAW = []
            ERSIGNAW = Globals().dictfetchall(cursor)

            cursor.execute(queryS)
            ERSIGNAS = []
            ERSIGNAS = Globals().dictfetchall(cursor)

            if int(len(ERSIGNAF)) > 0:
                edits["ERSIGNAF"] = ERSIGNAF[0]
            if int(len(ERSIGNAW)) > 0:
                edits["ERSIGNAW"] = ERSIGNAW[0]
            if int(len(ERSIGNAS)) > 0:
                edits["ERSIGNAS"] = ERSIGNAS[0]

            edit = json.dumps(edits, cls=DjangoJSONEncoder)
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "detailRS":
            query = "SELECT * FROM CABANG WHERE CABANG_ID={}".format(
                request.session["kdCabang"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "detailApotik":
            query = "SELECT * FROM CABANG_APOTEK,CABANG"
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "transaksiResep":
            query = " SELECT ISNULL(PNY.PENYAKIT,'') as MRPKD_PENYAKITN,ISNULL(MRP.MRPKD_PENYAKIT,'') as MRPKD_PENYAKIT,ED.FHRNO_TRANSAKSI,KP.KPNO_TRANSAKSI,KP.KPKD_DOKTER,CONVERT(varchar,KP.KPTGL_PERIKSA,105) as KPTGL_PERIKSA,DK.FMDDOKTERN  "
            query += " FROM KUNJUNGANPASIEN as KP  "
            query += " LEFT JOIN DOKTER DK ON KP.KPKD_DOKTER=DK.FMDDOKTER_ID  "
            query += " LEFT JOIN MR_PENYAKIT MRP ON KP.KPNO_TRANSAKSI=MRP.MRPNO_TRANSAKSI AND MRP.MRPSTAT_DIAG='5'   "
            query += " LEFT JOIN PENYAKIT PNY ON MRP.MRPKD_PENYAKIT=PNY.KD_PENYAKIT  "
            query += "  ,ERESEPDOKTER as ED   "
            query += "	where KP.KPKD_PASIEN='{}' and KP.KPNO_TRANSAKSI=ED.FHRBUKTI_ID ORDER BY KPTGL_PERIKSA".format(
                request.GET["FHFJCUST_ID"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "transaksiResepDetail":
            query = "	SELECT FDRRESEP,FDRBRGN,FDRSATUAN,FDRQTY,FDRDOSIS,FDRDOSIS2,FDRSIGNA FROM ERESEPDOKTERD where FDRBUKTI_ID='{}' ".format(
                request.GET["FDRBUKTI_ID"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "getBentukRacikan":
            query = "SELECT * FROM BENTUKRACIKAN"
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "detailResepRacik":
            json_data_list = []
            edits = {}
            query = "Select TOP 1 a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
            query += " b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,c.HJUAL,(a.FDRQTY*c.Hjual) As Total "
            query += " from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            query += " where a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ORDER BY FDRRESEP".format(
                request.GET["noTrans"]
            )

            q1 = "select a.KPNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) as KPTGL_PERIKSA,KPKD_POLY,KPKD_DOKTER,c.FMDDOKTERN,a.KPKD_PASIEN, KD_CUSTOMER,d.NAME,b.NAMAPASIEN,convert(varchar, tgl_lahir, 105) as  tgl_lahir,convert(varchar, tgl_lahir, 101) as  tgl_lahir2,ALAMAT, JENIS_KELAMIN"
            q2 = " from KUNJUNGANPASIEN a,pasien b,Dokter c,CUSTOMER d "
            q3 = " where a.KPKD_PASIEN=b.KD_PASIEN  and c.FMDDOKTER_ID=a.KPKD_DOKTER and a.KD_CUSTOMER=d.CUSID and "
            q4 = " A.KPNO_TRANSAKSI='{}'".format(request.GET["noTrans"])
            query2 = "{}{}{}{}".format(q1, q2, q3, q4)

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            resep = []
            resep = Globals().dictfetchall(cursor)

            cursor.execute(query2)
            detailKujungan = []
            detailKujungan = Globals().dictfetchall(cursor)

            if int(len(detailKujungan)) > 0:
                edits["detailKunjungan"] = detailKujungan[0]
            if int(len(resep)) > 0:
                edits["resep"] = resep[0]

            edit = json.dumps(edits, cls=DjangoJSONEncoder)
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "detailResepRacikRI":
            json_data_list = []
            edits = {}
            query = "Select TOP 1 a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
            query += " b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,c.HJUAL,(a.FDRQTY*c.Hjual) As Total "
            query += " from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            query += " where a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ORDER BY FDRRESEP".format(
                request.GET["noTrans"]
            )

            q1 = "SELECT TOP 1 D.JENIS_KELAMIN,D.KD_PERUSAHAAN,(SELECT NAME FROM CUSTOMER where CUSID=D.KD_PERUSAHAAN) as PERUSAHAAN ,B.PRWIKD_CUSTOMER,B.PRWIKD_SPECIAL as KD_SPESIALIS,ISNULL((SELECT FMSURLASSESMENT FROM SPESIALISASI where FMSPESIALISASI_ID=B.PRWIKD_SPECIAL ),'#') as SPESIALIS_URL,(SELECT FMSPESIALISASIN FROM SPESIALISASI where FMSPESIALISASI_ID=B.PRWIKD_SPECIAL ) as SPESIALIS,(SELECT FMDDOKTERN FROM DOKTER where FMDDOKTER_ID=B.PRWIKD_DOKTER) as DOKTERPJN,B.PRWIKD_DOKTER as DOKTERPJKD,B.PRWIKD_SPECIAL as KDPOLI,(SELECT FMSPESIALISASIN FROM SPESIALISASI where FMSPESIALISASI_ID=B.PRWIKD_SPECIAL) AS POLIN,B.PRWINO_TRANSAKSI,B.PRWIKD_PASIEN as NORM,(SELECT NAMAPASIEN FROM PASIEN WHERE KD_PASIEN=B.PRWIKD_PASIEN) as NAMAPASIEN,(SELECT ALAMAT FROM PASIEN WHERE KD_PASIEN=B.PRWIKD_PASIEN) as ALAMAT,"
            q2 = " DATEDIFF(YY,(SELECT TGL_LAHIR FROM PASIEN WHERE KD_PASIEN=B.PRWIKD_PASIEN),GETDATE()) as USIA,CONVERT(varchar,(SELECT TGL_LAHIR FROM PASIEN WHERE KD_PASIEN=B.PRWIKD_PASIEN),105) as TGL_LAHIR,CONVERT(varchar,PRWITGL_MASUK,105) as TGL_MASUK,(SELECT NAME FROM CUSTOMER where CUSID=PRWIKD_CUSTOMER) as PENANGGUNG,C.FMKNAMA_KAMAR"
            q3 = " FROM KAMAR_INDUK A , PASIENRAWATINAP B,KAMAR C,PASIEN D where B.PRWIKD_KAMAR=C.FMKKAMAR_ID AND A.FMKAMAR_ID=C.FMKKAMARINDUK AND B.PRWITGL_KELUAR IS NULL "
            q4 = " AND B.PRWINO_TRANSAKSI='{}' AND D.KD_PASIEN=B.PRWIKD_PASIEN ORDER BY PRWIKD_PASIEN".format(
                request.GET["noTrans"]
            )

            query2 = "{}{}{}{}".format(q1, q2, q3, q4)

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            resep = []
            resep = Globals().dictfetchall(cursor)

            cursor.execute(query2)
            detailKujungan = []
            detailKujungan = Globals().dictfetchall(cursor)

            if int(len(detailKujungan)) > 0:
                edits["detailKunjungan"] = detailKujungan[0]
            if int(len(resep)) > 0:
                edits["resep"] = resep[0]

            edit = json.dumps(edits, cls=DjangoJSONEncoder)
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "getAllRacikanById":
            json_data_list = []
            edits = {}
            query = " SELECT * FROM ERESEPRACIK WHERE FERRACIK_ID='{}'".format(
                request.GET["FERRACIK_ID"]
            )
            query2 = " SELECT * FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}'".format(
                request.GET["FERRACIK_ID"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            ERESEPRACIK = []
            ERESEPRACIK = Globals().dictfetchall(cursor)

            cursor.execute(query2)
            ERESEPRACIKD = []
            ERESEPRACIKD = Globals().dictfetchall(cursor)

            if int(len(ERESEPRACIK)) > 0:
                edits["ERESEPRACIK"] = ERESEPRACIK[0]
            else:
                edits["ERESEPRACIK"] = []
            if int(len(ERESEPRACIKD)) > 0:
                edits["ERESEPRACIKD"] = ERESEPRACIKD
            else:
                edits["ERESEPRACIKD"] = []

            edit = json.dumps(edits, cls=DjangoJSONEncoder)
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "getFindRacikanByResep":
            json_data_list = []
            edits = {}
            query = "SELECT FERCKNBENTUKS,FHRNO_TRANSAKSI,FERCKNBENTUK_ID,FERCKNBENTUKN,FERCKNQTYRMW,FERCKNQTY,FERCKNDOSIS,FERCKNDOSIS2,FERCKNSIGNAF,FERCKNSIGNAS,FERCKNSIGNAW,"
            query += " FERRACIK_ID,FERCKNSIGNA, convert(varchar, UPDATERS, 105) as UPDATERS FROM ERESEPRACIK WHERE FHRNO_TRANSAKSI='{}' AND KD_CABANG=LEFT(FHRNO_TRANSAKSI,3)".format(
                request.GET["FHRNO_TRANSAKSI"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            ERESEPRACIK = []
            ERESEPRACIK = Globals().dictfetchall(cursor)

            if int(len(ERESEPRACIK)) > 0:
                edits = ERESEPRACIK

            edit = json.dumps(edits, cls=DjangoJSONEncoder)
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "getHeaderRacikanByResep":
            json_data_list = []
            edits = {}
            query = " SELECT * FROM ERESEPRACIK WHERE FHRNO_TRANSAKSI='{}'".format(
                request.GET["FHRNO_TRANSAKSI"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            ERESEPRACIK = []
            ERESEPRACIK = Globals().dictfetchall(cursor)

            if int(len(ERESEPRACIK)) > 0:
                edits["ERESEPRACIK"] = ERESEPRACIK[0]

            edit = json.dumps(edits, cls=DjangoJSONEncoder)
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "getDetailRacikanByResep":
            # json_data_list = []
            # edits={}
            # query=" SELECT FERRACIKD_ID,FERRACIKDNO,FERRACIKDBRG_ID,FERRACIKDBRGN,FERRACIKDKK,FERRACIKDSATKK,FERRACIKDQTYJENIS,FERRACIKDQTY,FERDKEBQTY,FERDKEBQTY2,FERDKEBSATUAN,FERDDOSIS,convert(varchar, UPDATERS, 105) as UPDATERS"
            # query+=" FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}'".format(request.GET['FERRACIK_ID'].strip())
            json_data_list = []
            edits = {}
            query = " SELECT A.FERRACIKD_ID,A.FERRACIKDNO,A.FERRACIKDBRG_ID,A.FERRACIKDBRGN,A.FERRACIKDKK,A.FERRACIKDSATKK,A.FERRACIKDQTYJENIS"
            query += " ,A.FERRACIKDQTY,A.FERDKEBQTY,A.FERDKEBQTY2,A.FERDKEBSATUAN,A.FERDDOSIS,convert(varchar, A.UPDATERS, 105) as UPDATERS"
            query += " ,B.FERCKNBENTUK_ID,B.FERCKNBENTUKN,B.FERCKNBENTUKS,B.FERCKNDOSIS,B.FERCKNDOSIS2,B.FERCKNQTY,B.FERCKNQTYRMW,B.FERCKNSIGNA"
            query += " ,B.FERCKNSIGNAF,B.FERCKNSIGNAS,B.FERCKNSIGNAW"
            query += " FROM ERESEPRACIKD A LEFT JOIN ERESEPRACIK B ON A.FERRACIKD_ID=B.FERRACIK_ID"
            query += " WHERE A.FERRACIKD_ID='{}'".format(
                request.GET["FERRACIK_ID"].strip()
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            ERESEPRACIK = []
            ERESEPRACIK = Globals().dictfetchall(cursor)

            if int(len(ERESEPRACIK)) > 0:
                edits = ERESEPRACIK

            edit = json.dumps(edits, cls=DjangoJSONEncoder)
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "detailResepReport":
            q1 = "Select a.FDRRESEP, FDRBRG_ID,FDRBRG_ID2, FDRBRGN, FDRSATUAN,  CAST(FDRQTY AS int) as FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
            q2 = " ISNULL(CASE WHEN a.FDRSTATUS=0 THEN "
            q2 += "' da '"
            q2 += "+(SELECT NAME_BRG FROM BARANG WHERE BARANGC=a.FDRBRG_ID2 and BRANCH=LEFT(b.FHRBUKTI_ID,3) )+' '"
            q2 += " ELSE '' END,'') as FDRBRGDA,"
            q2 += " b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,c.HJUAL,(a.FDRQTY*c.Hjual) As Total "
            q3 = " from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            q4 = " where a.FDRSTATUS2 IS NOT NULL and a.FDRRACIK_ID='NULL' and c.BRANCH=LEFT(b.FHRBUKTI_ID,3) and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ORDER BY FDRRESEP".format(
                request.GET["noTrans"]
            )
            query = "{}{}{}{}".format(q1, q2, q3, q4)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "detailResepReportPengganti":
            q1 = "Select TOP 1 a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
            q2 = " b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,c.HJUAL,(a.FDRQTY*c.Hjual) As Total "
            q3 = " from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            q4 = " where a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and A.FDRBRG_ID2='{}' and c.BRANCH=LEFT(b.FHRBUKTI_ID,3) and b.FHRBUKTI_ID='{}' ORDER BY FDRRESEP".format(
                request.GET["FDRBRG_ID2"], request.GET["noTrans"]
            )
            query = "{}{}{}{}".format(q1, q2, q3, q4)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "detailResepRacikReport":
            json_data_list = []
            edits = {}

            queryAwal = "Select DISTINCT a.FDRRACIK_ID from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c  where a.FDRRACIK_ID<>'NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ".format(
                request.GET["noTrans"]
            )
            cursor = connection.cursor()
            cursor.execute(queryAwal)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "detailDataResepRacikReport":
            json_data_list = []
            edits = {}

            q1 = "Select a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
            q2 = " ISNULL(CASE WHEN a.FDRSTATUS=0 THEN "
            q2 += "' da '"
            q2 += "+(SELECT NAME_BRG FROM BARANG WHERE BARANGC=a.FDRBRG_ID2)+' '"
            q2 += " ELSE '' END,'') as FDRBRGDA,"
            q2 += " (SELECT TOP 1 CONVERT(varchar(max),FERDKEBQTY2)+' '+FERRACIKDQTYJENIS FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}' AND FERRACIKDBRG_ID=FDRBRG_ID AND FERRACIKDQTY=FDRQTY) as FDRKEB,".format(
                request.GET["FDRRACIK_ID"]
            )
            q2 += " b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,c.HJUAL,(a.FDRQTY*c.Hjual) As Total "
            q3 = " from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
            q4 = " where a.FDRSTATUS2 IS NOT NULL and a.FDRRACIK_ID<>'NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' AND a.FDRRACIK_ID='{}' ORDER BY FDRRESEP".format(
                request.GET["noTrans"], request.GET["FDRRACIK_ID"]
            )
            query = "{}{}{}{}".format(q1, q2, q3, q4)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        else:
            edit = "not permited"
    else:
        edit = "not permited"
    return HttpResponse(edit, content_type="application/json")


def getPasienRJ(request):
    if "q" in request.GET:
        q = request.GET["q"]
        if q == "pasienRJ":
            if getattr(env, "MODE_URUT_BYNOTRANS", 0) == 1:
                q1 = "select RIGHT(a.KPNO_TRANSAKSI,3) AS Row_Number,a.KPNO_TRANSAKSI,convert(varchar, KPTGL_PERIKSA, 105) as KPTGL_PERIKSA,convert(varchar, KPJAM_MASUK, 105) as KPJAM_MASUK,KPKD_POLY,KPKD_DOKTER,c.FMDDOKTERN,a.KPKD_PASIEN as NORM,KD_CUSTOMER,d.NAME as PENANGGUNG,"
            else:
                q1 = "select ROW_NUMBER() OVER(ORDER BY a.KPNO_TRANSAKSI) AS Row_Number,a.KPNO_TRANSAKSI,convert(varchar, KPTGL_PERIKSA, 105) as KPTGL_PERIKSA,convert(varchar, KPJAM_MASUK, 105) as KPJAM_MASUK,KPKD_POLY,KPKD_DOKTER,c.FMDDOKTERN,a.KPKD_PASIEN as NORM,KD_CUSTOMER,d.NAME as PENANGGUNG,"
            q1 += " ISNULL(PRJK.FRPSTATUS,0) as FRPSTATUS,"
            q1 += " ISNULL(PRJK.FRPSTATUS2,0) as FRPSTATUS2,"
            q2 = " b.NAMAPASIEN,convert(varchar, tgl_lahir, 105) as TGLLAHIR,convert(varchar, tgl_lahir, 101) as  tgl_lahir2,ALAMAT, JENIS_KELAMIN,e.KODEASSESMENT,e.FMPKLINIKN,ISNULL((SELECT TOP 1 FHRSTATUS FROM ERESEPDOKTER WHERE FHRBUKTI_ID=a.KPNO_TRANSAKSI),0) as Status from KUNJUNGANPASIEN a "
            q2 += " LEFT JOIN PASIEN_RUJUKAN PRJK ON a.KPNO_TRANSAKSI=PRJK.FRPNOTRANSAKSIKJ"
            q2 += " ,pasien b,Dokter c,CUSTOMER d,Poliklinik e where"
            q3 = " a.KPKD_PASIEN=b.KD_PASIEN  and c.FMDDOKTER_ID=a.KPKD_DOKTER and a.KD_CUSTOMER=d.CUSID and a.KPKD_POLY=E.FMPKLINIK_ID and"
            # RSUD REMBANG KECUALI OK
            q3 += " E.FMPPENUNJANG2<>'1' AND "
            # ---------------------------------
            if "kdDokter" in request.GET:
                q3 += " A.KPKD_DOKTER='{}'  and  ".format(request.GET["kdDokter"])
                if getattr(env, "MODE_WAJIB_ASS_PRW", 0) == 1:
                    q3 += " PRJK.FRPSTATUS2='3' and "
            if getattr(env, "MODE_URUT_BYNOTRANS", 0) == 1:
                q4 = " convert(datetime, KPTGL_PERIKSA, 105)>=convert(datetime, '{}', 105)  and convert(datetime, KPTGL_PERIKSA, 105)<=convert(datetime, '{}', 105) order by RIGHT(a.KPNO_TRANSAKSI,3) DESC".format(
                    request.GET["tglAwal"], request.GET["tglAkhir"]
                )
            else:
                q4 = " convert(datetime, KPTGL_PERIKSA, 105)>=convert(datetime, '{}', 105)  and convert(datetime, KPTGL_PERIKSA, 105)<=convert(datetime, '{}', 105) order by PRJK.FRPSTATUS,KPKD_POLY,KPTGL_PERIKSA,b.NAMAPASIEN DESC".format(
                    request.GET["tglAwal"], request.GET["tglAkhir"]
                )
            query = "{}{}{}{}".format(q1, q2, q3, q4)
            # print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "listPasienTgl":
            cursor = connection.cursor()
            query = " SELECT IIF(EMR.CPTDCREATED_AT IS NULL,'0','1') AS STATUS_EMR,RTRIM(LTRIM(PSN.NO_ASURANSI)) as NO_ASURANSI,PSN.NAMAPASIEN, convert(varchar, PSN.TGL_LAHIR, 105) as TGL_LAHIR,A.KPKD_PASIEN as NORM,PL.KODEASSESMENT"
            query += " ,PL.FMPKLINIK_ID,FMPKLINIKN,DR.FMDDOKTERN,CST.NAME as CUSTOMER"
            query += " ,A.*,CONVERT(varchar,A.KPTGL_PERIKSA,105) as TGL_INDO,PSN.ALAMAT,convert(varchar, PSN.tgl_lahir, 101) as  tgl_lahir2,IIF(PSN.JENIS_KELAMIN=1,'L','P') as JENIS_KELAMIN"
            query += " FROM KUNJUNGANPASIEN A"
            query += " LEFT JOIN PASIEN PSN ON A.KPKD_PASIEN=PSN.KD_PASIEN"
            query += " LEFT JOIN POLIKLINIK PL ON A.KPKD_POLY=PL.FMPKLINIK_ID"
            query += " LEFT JOIN CUSTOMER CST ON A.KD_CUSTOMER=CST.CUSID"
            query += " INNER JOIN DOKTER DR ON A.KPKD_DOKTER=DR.FMDDOKTER_ID"
            query += " LEFT JOIN EMRRJ_CPPT_DOKTER EMR ON A.KPNO_TRANSAKSI=EMR.CPTDNO_TRANSAKSI_RJ"
            query += " WHERE A.KPTGL_PERIKSA>='{}' AND A.KPTGL_PERIKSA<='{}' AND  LEFT(A.KPNO_TRANSAKSI,3)='{}'".format(
                request.GET["tglAwal"],
                request.GET["tglAkhir"],
                request.session["kdCabang"],
            )
            query += (
                " ORDER BY STATUS_EMR ASC, LEN(A.KD_ANTRIAN) DESC,A.KD_ANTRIAN DESC"
            )

            # print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "listPasienNotrans":
            cursor = connection.cursor()
            query = " SELECT RTRIM(LTRIM(PSN.NO_ASURANSI)) as NO_ASURANSI ,PSN.NAMAPASIEN, convert(varchar, PSN.TGL_LAHIR, 105) as TGL_LAHIR,A.KPKD_PASIEN as NORM,PL.KODEASSESMENT"
            query += " ,PL.FMPKLINIK_ID,FMPKLINIKN,DR.FMDDOKTERN,CST.NAME as CUSTOMER"
            query += " ,A.*,CONVERT(varchar,A.KPTGL_PERIKSA,105) as TGL_INDO,PSN.ALAMAT,convert(varchar, PSN.tgl_lahir, 101) as  tgl_lahir2,IIF(PSN.JENIS_KELAMIN=1,'L','P') as JENIS_KELAMIN"
            query += " FROM KUNJUNGANPASIEN A"
            query += " LEFT JOIN PASIEN PSN ON A.KPKD_PASIEN=PSN.KD_PASIEN"
            query += " LEFT JOIN POLIKLINIK PL ON A.KPKD_POLY=PL.FMPKLINIK_ID"
            query += " LEFT JOIN CUSTOMER CST ON A.KD_CUSTOMER=CST.CUSID"
            query += " INNER JOIN DOKTER DR ON A.KPKD_DOKTER=DR.FMDDOKTER_ID"
            query += " WHERE A.KPNO_TRANSAKSI='{}'".format(request.GET["NO_TRANSAKSI"])

            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "pasienRujukan":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
            cabang = Globals().dictfetchall(cursor)
            kdCabang = cabang[0]["CABANG_ID"]

            q1 = " SELECT ISNULL((SELECT TOP 1 Updateantrian FROM TOMBOL_ANTRIAN.dbo.poliklinik_antri where NO=FRPNOANTRIDOKTER AND Tanggal=convert(datetime, FRPTGL, 105)),'0') as PanggilanKe,ISNULL(STATUSANTRI,'') as STATUSANTRI,FRPNOTRANSAKSI,convert(varchar, FRPTGL, 105) as KPTGL_PERIKSA,FRPPASIEN_ID,(SELECT TOP 1 NAMAPASIEN FROM PASIEN WHERE KD_PASIEN=FRPPASIEN_ID) as NAMAPASIEN,FRPNOANTRIDOKTER,"
            q1 += " CASE WHEN STATUSANTRI IS NULL THEN 'Belum Di Panggil' ELSE 'Sudah Di Panggil' END as Status FROM  PASIEN_RUJUKAN "
            q1 += " WHERE  FRPTGL>=convert(datetime, '{}', 105)  and FRPTGL<=convert(datetime, '{}', 105) AND FRPNOANTRIDOKTER IS NOT NULL".format(
                request.GET["tglAwal"], request.GET["tglAkhir"]
            )
            if request.GET["pencarian"] == "1":
                q1 += " AND FRPDOKTER_ID='{}' ".format(request.GET["kdDokter"])
            else:
                if kdCabang != "22":
                    q1 += " AND FRPUNIT='{}'".format(request.GET["kdPoli"])
            q1 += " ORDER BY STATUSANTRI,FRPNOANTRIDOKTER"
            query = "{}".format(q1)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "chartPasienRujukan":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
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
            cursor = connection.cursor()
            cursor.execute(query)
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
            cursor = connection.cursor()
            cursor.execute(query)
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
            cursor = connection.cursor()
            cursor.execute(query)
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
            cursor.close()
        elif q == "chartPasienRujukanDokter":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
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

            cursor = connection.cursor()
            cursor.execute(query)
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
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            jumPasienDokter = result[0]["jumPasienDokter"]

            cursor = connection.cursor()
            cursor.execute(query)
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
            cursor.close()
        elif q == "chartPasienRujukanPerawat":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
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
            query += " AND FRPUNIT='{}' AND P.FMPPENUNJANG2<>'1'".format(
                request.GET["kdPoli"]
            )
            # if kdCabang!="19":
            # 	q1+="  AND FRPNOANTRIDOKTER IS NOT NULL "

            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            # ##print(query)
            jumlahPasien = result[0]["jumPasien"]

            # jumpasien perawat sudah di isi assesment
            query = " SELECT count(*) as jumPasienPerawat FROM  PASIEN_RUJUKAN A "
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
            query += " AND FRPUNIT='{}' AND P.FMPPENUNJANG2<>'1' AND A.FRPSTATUS2='3'".format(
                request.GET["kdPoli"]
            )
            # prints("jumPasienPeriksa")

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            jumPasienPerawat = result[0]["jumPasienPerawat"]

            jumPasienPerawatBelumDiPeriksa = jumlahPasien - jumPasienPerawat
            result = [
                {
                    "jumlahPasien": jumlahPasien,
                    "jumPasienPerawat": jumPasienPerawat,
                    "jumPasienPerawatBelumDiPeriksa": jumPasienPerawatBelumDiPeriksa,
                }
            ]

            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "panggilPasienRJ":
            cursor = connection.cursor()
            json_data_list = []
            edits = {}
            try:
                query = "UPDATE PASIEN_RUJUKAN SET STATUSANTRI='1' where FRPNOTRANSAKSI='{}' ".format(
                    request.GET["FRPNOTRANSAKSI"]
                )

                cursor.execute(query)
                query = "Select * from PASIEN_RUJUKAN where STATUSANTRI ='1' and FRPNOTRANSAKSI='{}'".format(
                    request.GET["FRPNOTRANSAKSI"]
                )
                cursor.execute(query)
                rows = cursor.fetchall()

                cursor2 = connections["antrian"].cursor()
                NO = request.GET["NO"]
                q = "UPDATE poliklinik_antri SET Updateantrian= ISNULL(convert (int, Updateantrian), 0 )+1 ,Status_Pen = 'True', Sound = 'False',display='False' ,Channel = '1' where NO= %s AND Tanggal = CONVERT(DATE, GETDATE()) "
                cursor2.execute(q, [NO])

                # prints(rows)
                # return HttpResponse(json_data, content_type="application/json")
                jum = int(len(rows))
                if jum > 0:
                    edits["success"] = True
                    edits["message"] = "Success Panggil"
                else:
                    edits["success"] = False
                    edits["message"] = "Gagal Panggil"
            finally:
                cursor.close()

            json_data_list.append(edits)
            json_data = json.dumps(json_data_list)
            return HttpResponse(json_data, content_type="application/json")
        else:
            edit = "not permited"
    else:
        edit = "not permited"
    return HttpResponse(edit, content_type="application/json")


def nl2br(string, is_xhtml=True):
    if is_xhtml:
        return string.replace("\n", "<br />\n")
    else:
        return string.replace("\n", "<br>\n")


def getNakes(request):
    if "sesi" in request.GET:
        sesi = request.GET["sesi"]
        if sesi == "getPerawat":
            query = "SELECT FMPPERAWAT_ID as id,(FMPPERAWAT_ID+'_'+FMPPERAWATN) as text  FROM PERAWAT where FMPPERAWATN LIKE '%{}%' ".format(
                request.GET["q"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif sesi == "getDokter":
            query = "Select DOKTER.FMDDOKTER_ID as id,(DOKTER.FMDDOKTER_ID+'_'+DOKTER.FMDDOKTERN) as text from DOKTER where FMDDOKTERN LIKE '%{}%' ".format(
                request.GET["q"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif sesi == "getKamar":
            query = "SELECT FMKAMAR_ID as id, (FMKAMAR_ID+'_'+FMKAMARN) as text FROM KAMAR_INDUK WHERE FMKAMARN  LIKE '%{}%' ".format(
                request.GET["q"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif sesi == "getPoli":
            query = "SELECT FMPKLINIK_ID as id, (FMPKLINIK_ID+'_'+FMPKLINIKN) as text  FROM POLIKLINIK WHERE  FMPKLINIKN  LIKE '%{}%' ".format(
                request.GET["q"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif sesi == "getDokter":
            query = "SELECT FMDDOKTER_ID as id,(FMDDOKTER_ID+'_'+FMDDOKTERN) as text FROM DOKTER WHERE FMDDOKTER_ID in(SELECT FMJKD_DOKTER FROM JADWAL_POLI WHERE FMJKD_KLINIK='{}' ) ".format(
                request.GET["kdPoli"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        else:
            edit = "not permited"
    else:
        edit = "not permited"
    return HttpResponse(edit, content_type="application/json")


def getDataCPPT(request):
    if "q" in request.GET:
        q = request.GET["q"]
        if q == "OpenAssesment":
            query = "select FMSBUKTI_ID, FMSKEADAAN_UMUM, FMSBB, FMSTB,FMSLK,FMSTENSI, FMSSUHU, FMSNADI, FMSRR, FMSKLU, FMSRPD, FMSRPS,"
            query += " FMSALERGI, ISNULL(FMSKETALERGI,'-') as FMSKETALERGI, USERRS, ISNULL(convert(varchar, UPDATERS, 113),'') as UPDATERS,FMSNYERIY,FMSNYERI,FMSJATUH,FMSDWS,FMSNUTRISI, FMKHNUTRISI, FMSIMPLE, FMSRWPSIKO,"
            query += " FMKMASKEP,FMSSTPSIKO,FMSGIZI From SOAPI_RJ"
            query += " WHERE FMSBUKTI_ID='{}'".format(request.GET["FMSBUKTI_ID"])

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "cabang":
            q1 = " SELECT * FROM CABANG"
            query = "{}".format(q1)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "cabangs":
            q1 = " SELECT PERUSAHAAN,CABANG_ID FROM CABANG"
            query = "{}".format(q1)
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getSOAPTemplate":
            query = " Select MST_KODE,MST_KET,MST_KDDOKTER FROM MR_SOAP_TEMPLATE"
            query += " WHERE MST_KDDOKTER='{}'".format(request.GET["MST_KDDOKTER"])
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "altertabel":
            cursor = connection.cursor()
            q = "ALTER TABLE ERESEPPAKET ADD PFKDDOKTER varchar(50);"
            cursor.execute(q)

            cursor = connection.cursor()
            q = "CREATE TABLE [dbo].[MR_SOAP_TEMPLATE]("
            q += "[MST_KODE] [varchar](MAX) NULL,"
            q += "[MST_KET] [text] NULL,"
            q += "[MST_KDDOKTER] [varchar](50) NULL"
            q += ") ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]"
            cursor.execute(q)

            query = " Select * FROM CABANG"
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "OpenDetailLabRad":
            query = "SELECT FTP_NOTRANSAKSI,FTP_NOTRANSAKSI_LAB,FTP_KDPRODUK,FTP_STATUS_CITO,FTP_KDPERIKSA,FTP_KELOMPOK FROM LAB_PERMINTAAN "
            query += " WHERE FTP_NOTRANSAKSI='{}' AND FTP_NOTRANSAKSI_LAB='{}' ".format(
                request.GET["FTP_NOTRANSAKSI"], request.GET["FTP_NOTRANSAKSI_LAB"]
            )
            query += " and FTP_KELOMPOK in (SELECT FMKKLAS_ID FROM KLAS_PRODUK_RAD_LAB where PARENT='{}' and FMKKLAS_ID=FTP_KELOMPOK)".format(
                request.GET["PARENT"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "OpenHistoryLabRad":
            query = "SELECT DISTINCT A.FTP_KDPASIEN,(CASE when ISNULL(A.FTP_STATUS,0)='0' THEN 'Belum' ELSE 'Sudah' END) as FTP_STATUS,A.FTP_NOTRANSAKSI_LAB ,D.NAMAPASIEN, A.FTP_NOTRANSAKSI,A.FTP_NOTRANSAKSI_LAB, RIGHT(A.FTP_NOTRANSAKSI_LAB, 3) as NO_URUT, CONVERT(varchar,A.FTP_TGLTRANSAKSI,105) as TGL_TRANSAKSI "
            query += " FROM LAB_PERMINTAAN A ,LAB_PERIKSA B,KLAS_PRODUK_RAD_LAB C, PASIEN D WHERE A.FTP_KDPERIKSA=B.FMB_KODEPEMERIKSAAN AND C.FMKKLAS_ID=A.FTP_KELOMPOK AND A.FTP_KDPASIEN=D.KD_PASIEN "
            query += " AND A.FTP_NOTRANSAKSI='{}' AND A.FTP_PARENT='{}' AND A.KD_CABANG=LEFT(A.FTP_NOTRANSAKSI,3) ".format(
                request.GET["FTP_NOTRANSAKSI"], request.GET["PARENT"]
            )
            query += " ORDER BY NO_URUT "

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "Opendiagnosa":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
            cabang = Globals().dictfetchall(cursor)
            query = "Select  ISNULL(MRDKD_PRWT,'-') as MRDKD_PRWT,ISNULL(MRD_PRWTN,'-') as MRD_PRWTN,MRDKD_DOKTER, MRDKD_PASIEN, MRDKD_UNIT, MRDNO_TRANSAKSI, convert(varchar, MRDTGL_DIAGNOSA, 105) as MRDTGL_DIAGNOSA, MRDDIAGNOSA_UTAMA,ISNULL( MRDPHISIK, '') as MRDPHISIK , ISNULL( MRDPENUNJANG, '') as MRDPENUNJANG,ISNULL(MRDVENTILATOR, '') as MRDVENTILATOR,ISNULL( MRDKELUHAN, '') as MRDKELUHAN, ISNULL( MRDANAMNESE, '') as MRDANAMNESE,"
            if "jns_cabang" in cabang[0]:
                jns_cabang = cabang[0]["jns_cabang"]
                if jns_cabang == "KLINIK":
                    query += " ISNULL(MRD_SISTOLE,'0') as MRD_SISTOLE,ISNULL(MRD_DIASTOLE,'0') as MRD_DIASTOLE,ISNULL(MRD_BMI,'0') as MRD_BMI,ISNULL(MRD_LPERUT,'0') as MRD_LPERUT,ISNULL(MRD_KESADARAN,'01') as MRD_KESADARAN,ISNULL(MRD_StatusPulang,'3') as MRD_StatusPulang,"
            query += " ISNULL( MRDRIWAYAT_PENYAKIT, '') as MRDRIWAYAT_PENYAKIT,  ISNULL( MRDSIO, '') as MRDSIO, ISNULL( MRDOKLUSI, '') as  MRDOKLUSI,  ISNULL( MRDPALATINUS, '') as   MRDPALATINUS,  ISNULL( MRDMANDIBULANIS, '') as  MRDMANDIBULANIS,  ISNULL( MRDPALATUM, '') as    MRDPALATUM, ISNULL( MRDSUPER_NUMERARY, '') as  MRDSUPER_NUMERARY, ISNULL( MRDDIASTERNA, '') as  MRDDIASTERNA,ISNULL( MRDANOMALI, '') as  MRDANOMALI, ISNULL( MRDLAIN, '') as  MRDLAIN, ISNULL( MRDTERAPI, '') as MRDTERAPI, MRDRENCANA,"
            query += " ISNULL( MRD_IMAGE, '') as  MRD_IMAGE ,ISNULL( MRDRENCANA_KET, '') as  MRDRENCANA_KET , MRDEDUKASI,  ISNULL( MRDEDUKASI_KET, '') as  MRDEDUKASI_KET,  ISNULL( MRDSOAPIKET, '') as  MRDSOAPIKET,  ISNULL( MRDDIAGNOSAKET, '') as  MRDDIAGNOSAKET, ISNULL( MRDANJURANPERIKSA, '') as MRDANJURANPERIKSA,ISNULL( MRDINDIKASIMEDIS, '') as MRDINDIKASIMEDIS FROM MR_DIAGNOSA"
            query += " where MRDNO_TRANSAKSI='{}'".format(request.GET["NO_TRANSAKSI"])

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "listTabLabRad":
            jenisPeriksa = request.GET["jenisPeriksa"]

            query = " SELECT * FROM KLAS_PRODUK_RAD_LAB WHERE PARENT='{}' AND FMKSHOW='1'".format(
                request.GET["jenisPeriksa"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "listCheckListLabRad":
            kelPeriksa = request.GET["kelPeriksa"]

            # query=" SELECT * FROM LAB_PERIKSA"
            query = " SELECT * FROM LAB_PERIKSA where FMB_PARENT='{}'".format(
                request.GET["kelPeriksa"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "OpendiagnosaLast3Month":
            query = "Select TOP 1  MRDNO_TRANSAKSI FROM MR_DIAGNOSA "
            query += " WHERE MRDTGL_DIAGNOSA <=CONVERT(datetime,'{}',105) AND MRDTGL_DIAGNOSA >= DATEADD(DAY, -90, CONVERT(datetime,'{}',105)) AND MRDKD_PASIEN='{}' and MRDANAMNESE is not null ORDER BY MRDTGL_DIAGNOSA ASC".format(
                request.GET["MRDTGL_DIAGNOSA"],
                request.GET["MRDTGL_DIAGNOSA"],
                request.GET["MRDKD_PASIEN"],
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenAssesmentPerawatCopyBefore":
            edit = {}
            cursors = connection.cursor()
            q = "SELECT * FROM MR_DIAGNOSA as MD LEFT JOIN SOAPI_RJ as SRJ ON MD.MRDNO_TRANSAKSI=SRJ.FMSBUKTI_ID "
            q += "where MD.MRDKD_PASIEN='{}' AND MD.MRDNO_TRANSAKSI='{}' AND MD.MRDKD_UNIT='{}' and MRDANAMNESE is not null".format(
                request.GET["MRDKD_PASIEN"],
                request.GET["MRDNO_TRANSAKSI"],
                request.GET["MRDKD_UNIT"],
            )
            cursors.execute(q)
            cekAssement = Globals().dictfetchall(cursors)
            if int(len(cekAssement)) > 0:
                edit["success"] = False
                edit["message"] = "No Assesment"
            else:
                q = "Select CONVERT(varchar,MAX(MRDTGL_DIAGNOSA) ,23) as MRDTGL_DIAGNOSA FROM MR_DIAGNOSA  "
                q += "WHERE MRDKD_PASIEN='{}' and MRDANAMNESE is not null AND MRDKD_UNIT='{}'".format(
                    request.GET["MRDKD_PASIEN"], request.GET["MRDKD_UNIT"]
                )
                cursors.execute(q)
                cekAssement2 = Globals().dictfetchall(cursors)
                if int(len(cekAssement2)) > 0:
                    # prints(cekAssement2[0]['MRDTGL_DIAGNOSA'])
                    tglAssesment = cekAssement2[0]["MRDTGL_DIAGNOSA"]

                    q = "Select * FROM MR_DIAGNOSA WHERE  "
                    q += " MRDKD_PASIEN='{}' and MRDANAMNESE is not null AND MRDKD_UNIT='{}'and MRDTGL_DIAGNOSA='{}' ".format(
                        request.GET["MRDKD_PASIEN"],
                        request.GET["MRDKD_UNIT"],
                        tglAssesment,
                    )
                    cursors.execute(q)
                    dataMR_DIAGNOSA = Globals().dictfetchall(cursors)
                    if int(len(dataMR_DIAGNOSA)) > 0:
                        # prints(dataMR_DIAGNOSA)
                        # COPY DATA MR_DIAGNOSA
                        q = "Insert into MR_DIAGNOSA ( MRDKD_PRWT,MRD_PRWTN,MRDANAMNESE,MRDKD_DOKTER, MRDKD_PASIEN, MRDKD_UNIT,MRDNO_TRANSAKSI, MRDTGL_DIAGNOSA,MRDSOAPIKET,UPDATERS,USERRS)  "
                        q += "values('%s','%s','%s','%s','%s','%s','%s',CONVERT(VARCHAR(10),CONVERT(date, '%s', 105), 23),'%s',GETDATE(),'%s');"
                        inputan = (
                            dataMR_DIAGNOSA[0]["MRDKD_PRWT"],  # values(@MRDKD_PRWT,
                            dataMR_DIAGNOSA[0]["MRD_PRWTN"],  # @MRD_PRWTN,
                            dataMR_DIAGNOSA[0]["MRDANAMNESE"],  # @MRDANAMNESE,
                            request.GET["MRDKD_DOKTER"],  # @MRDKD_DOKTER,
                            dataMR_DIAGNOSA[0]["MRDKD_PASIEN"],  # @MRDKD_PASIEN,
                            dataMR_DIAGNOSA[0]["MRDKD_UNIT"],  # @MRDKD_UNIT,
                            request.GET["MRDNO_TRANSAKSI"],  # @MRDNO_TRANSAKSI,
                            request.GET[
                                "MRDTGL_DIAGNOSA"
                            ],  # CONVERT(VARCHAR(10),CONVERT(date, @MRDTGL_DIAGNOSA, 105), 23),
                            dataMR_DIAGNOSA[0]["MRDSOAPIKET"]  # @MRDSOAPIKET,
                            # GETDATE(),
                            ,
                            dataMR_DIAGNOSA[0]["USERRS"],  # @USERRS);
                        )
                        # prints(q % inputan)
                        cursors.execute(q % inputan)

                        # COPY DATA SOAPI_RJ
                        q = "insert into SOAPI_RJ(FMSBUKTI_ID, FMSKEADAAN_UMUM, FMSBB, FMSTB, FMSTENSI, FMSSUHU, FMSNADI, FMSRR, FMSKLU, FMSRPS, FMSRPD, FMSALERGI, FMSKETALERGI, USERRS, UPDATERS, FMSNYERIY, FMSNYERI, FMSJATUH, FMSDWS, FMSNUTRISI, FMSRWPSIKO, FMSSTPSIKO, FMSIMPLE, FMSLK, FMKMASKEP, FMKHNUTRISI, FMSGIZI, FMSGIZIKET)  "
                        q += " SELECT TOP 1 '%s', FMSKEADAAN_UMUM, FMSBB, FMSTB, FMSTENSI, FMSSUHU, FMSNADI, FMSRR, FMSKLU, FMSRPS, FMSRPD, FMSALERGI, FMSKETALERGI, '%s', GETDATE(), FMSNYERIY, FMSNYERI, FMSJATUH, FMSDWS, FMSNUTRISI, FMSRWPSIKO, FMSSTPSIKO, FMSIMPLE, FMSLK, FMKMASKEP, FMKHNUTRISI, FMSGIZI, FMSGIZIKET FROM SOAPI_RJ where FMSBUKTI_ID='%s' "
                        inputan = (
                            request.GET["MRDNO_TRANSAKSI"],  # NO TRANS TUJUAN
                            request.GET["MRDKD_DOKTER"],
                            dataMR_DIAGNOSA[0][
                                "MRDNO_TRANSAKSI"
                            ],  # NO TRANS LAMA YG ADA ISINYA
                        )
                        cursors.execute(q % inputan)

                        # CEK ASSPERAWAT DWASA?ANAK COPY ASSESMENT
                        q = "Select * FROM MR_ASESMEN_PERAWAT_ANAK WHERE MRAP_NO_TRANSAKSI='{}' ".format(
                            dataMR_DIAGNOSA[0]["MRDNO_TRANSAKSI"]
                        )
                        cursors.execute(q)
                        dataAssPrw = Globals().dictfetchall(cursors)
                        if int(len(dataAssPrw)) > 0:
                            q = " insert into MR_ASESMEN_PERAWAT_ANAK ( MRAP_NO_TRANSAKSI, MRAP_RWRI, MRAP_RWPK, MRAP_GM, MRAP_KELUHANSKRG, MRAP_RWIMN, MRAP_RESIKOJATUH, MRAP_NYERI, MRAP_RWTK, MRAP_SKIRININGIZI, MRAP_KESIMPULAN, UPDATERS, MRAP_KESIMPULAN_PRWT, MRAP_NAMA_PERAWAT) "
                            q += " SELECT TOP 1 '%s', MRAP_RWRI, MRAP_RWPK, MRAP_GM, MRAP_KELUHANSKRG, MRAP_RWIMN, MRAP_RESIKOJATUH, MRAP_NYERI, MRAP_RWTK, MRAP_SKIRININGIZI, MRAP_KESIMPULAN, GETDATE(), MRAP_KESIMPULAN_PRWT, MRAP_NAMA_PERAWAT FROM MR_ASESMEN_PERAWAT_ANAK WHERE MRAP_NO_TRANSAKSI='%s' "
                            inputan = (
                                request.GET["MRDNO_TRANSAKSI"],  # NO TRANS TUJUAN
                                dataMR_DIAGNOSA[0][
                                    "MRDNO_TRANSAKSI"
                                ],  # NO TRANS LAMA YG ADA ISINYA
                            )

                            cursors.execute(q % inputan)
                        else:
                            q = " insert into MR_ASESMEN_PERAWAT_DEWASA (MRAP_NO_TRANSAKSI, MRAP_RWRI, MRAP_RWPK, MRAP_RWAL, MRAP_GM, MRAP_KELUHANSKRG, MRAP_RESIKOJATUH, MRAP_NYERI, MRAP_SKIRININGIZI, MRAP_KESIMPULAN, UPDATERS, MRAP_KESIMPULAN_PRWT, MRAP_NAMA_PERAWAT) "
                            q += " SELECT TOP 1 '%s', MRAP_RWRI, MRAP_RWPK, MRAP_RWAL, MRAP_GM, MRAP_KELUHANSKRG, MRAP_RESIKOJATUH, MRAP_NYERI, MRAP_SKIRININGIZI, MRAP_KESIMPULAN, GETDATE(), MRAP_KESIMPULAN_PRWT, MRAP_NAMA_PERAWAT FROM MR_ASESMEN_PERAWAT_DEWASA WHERE MRAP_NO_TRANSAKSI='%s' "
                            inputan = (
                                request.GET["MRDNO_TRANSAKSI"],  # NO TRANS TUJUAN
                                dataMR_DIAGNOSA[0][
                                    "MRDNO_TRANSAKSI"
                                ],  # NO TRANS LAMA YG ADA ISINYA
                            )
                            # prints(q % inputan)
                            cursors.execute(q % inputan)

                        # copy assdokter
                        cursor = connection.cursor()
                        q = "select * from CABANG"
                        cursor.execute(q)
                        cabang = Globals().dictfetchall(cursor)
                        if "jns_cabang" in cabang[0]:
                            jns_cabang = cabang[0]["jns_cabang"]
                            if jns_cabang == "RS":
                                q = " EXEC AUD_COPY_ASSDOKTER '%s','%s','%s' "
                                inputan = (
                                    request.GET["MRDKD_UNIT"],  # POLI YG DI COPY
                                    request.GET["MRDNO_TRANSAKSI"],  # NO TRANS TUJUAN
                                    dataMR_DIAGNOSA[0][
                                        "MRDNO_TRANSAKSI"
                                    ],  # NO TRANS LAMA YG ADA ISINYA
                                )
                                # prints(q % inputan)
                                cursors.execute(q % inputan)

                    edit["success"] = True
                    edit["message"] = "Refresh Assesment"
                else:
                    edit["success"] = False
                    edit["message"] = "No Assesment"
            json_data = json.dumps(edit, cls=DjangoJSONEncoder)
            edit = json_data

        elif q == "getDiagnosaKerjaICD":
            query = "SELECT MP.MRPKD_PENYAKIT,MRPNO_TRANSAKSI,P.PENYAKIT FROM MR_PENYAKIT MP "
            query += " LEFT JOIN PENYAKIT P ON MP.MRPKD_PENYAKIT=P.KD_PENYAKIT WHERE MP.MRPNO_TRANSAKSI='{}' ORDER BY MRPURUT_MASUK".format(
                request.GET["noTrans"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "OpenHistoryCppt":
            q1 = " vs.MDG_VISUAL_1,vs.MDG_VISUAL_2,vs.MDG_VISUAL_3,vs.MDG_VISUAL_4,vs.MDG_VISUAL_5,"
            q1 += " CASE"
            # anak
            q1 += " WHEN (SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT AND KODEASSESMENT IS NOT NULL)='3' THEN "
            q1 += " ISNULL((SELECT TOP 1 MRDA_PDS FROM MR_DIAGNOSA_ANAK where MRDA_NO_TRANSAKSI=MRDNO_TRANSAKSI),'-')"
            # dalam
            q1 += " WHEN(SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT AND KODEASSESMENT IS NOT NULL)='4' "
            q1 += " THEN ISNULL((SELECT TOP 1 MR_DIAGNOSA_PENYAKITDALAM.MRDPD_PDS FROM MR_DIAGNOSA_PENYAKITDALAM where MR_DIAGNOSA_PENYAKITDALAM.MRDPD_NO_TRANSAKSI=MRDNO_TRANSAKSI),'-')"
            # umum
            q1 += " WHEN(SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT AND KODEASSESMENT IS NOT NULL)='12' "
            q1 += " THEN   ISNULL((SELECT TOP 1 MR_DIAGNOSA_UMUM.MRDBU_PDS FROM MR_DIAGNOSA_UMUM where MR_DIAGNOSA_UMUM.MRDBU_NO_TRANSAKSI=MRDNO_TRANSAKSI),'-') "
            # gigi
            q1 += " WHEN(SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT AND KODEASSESMENT IS NOT NULL)='2' "
            q1 += " THEN   ISNULL((SELECT TOP 1 MR_DIAGNOSA_GIGIMULUT.MDG_PDS FROM MR_DIAGNOSA_GIGIMULUT where MR_DIAGNOSA_GIGIMULUT.MDG_NO_TRANSAKSI=MRDNO_TRANSAKSI),'-') "
            # mata
            q1 += " WHEN(SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT AND KODEASSESMENT IS NOT NULL)='9' "
            q1 += " THEN   ISNULL((SELECT TOP 1 MR_DIAGNOSA_MATA.MDM_PDS FROM MR_DIAGNOSA_MATA where MR_DIAGNOSA_MATA.MDM_NO_TRANSAKSI=MRDNO_TRANSAKSI),'-') "
            # obsgyn
            q1 += " WHEN(SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT AND KODEASSESMENT IS NOT NULL)='7' "
            q1 += " THEN  'GINEKOLOGI: '+CONVERT(VARCHAR(MAX), ISNULL((SELECT TOP 1 MR_DIAGNOSA_OBSGYN_GINEKOLOGI.MRDOG_PDS FROM MR_DIAGNOSA_OBSGYN_GINEKOLOGI where MR_DIAGNOSA_OBSGYN_GINEKOLOGI.MRDOG_NO_TRANSAKSI=MRDNO_TRANSAKSI),'-') )+' OBSTETRIK:'+ CONVERT(varchar(max),ISNULL((SELECT TOP 1 MRDOG_DS FROM MR_DIAGNOSA_OBSGYN_OBSTETRIK where MRDOG_NO_TRANSAKSI=MRDNO_TRANSAKSI),'-'))"
            # else
            q1 += " WHEN(SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT AND KODEASSESMENT IS NOT NULL)='5' THEN "
            q1 += " MRDDIAGNOSAKET"
            q1 += " ELSE '-'"
            q1 += " END  as diagnosisKerja"
            # perawatNama
            q2 = ", ISNULL(MRD_PRWTN,'-')  as FMPPERAWATN"
            q2 += ", ISNULL(MRD_DIASTOLE,'0') as MRD_DIASTOLE, ISNULL(MRD_SISTOLE,'0') as MRD_SISTOLE, ISNULL(MRD_BMI,'0') as MRD_BMI , ISNULL(MRD_LPERUT,'0') as MRD_LPERUT, ISNULL(c.FMSKETALERGI,'-') as FMSKETALERGI, ISNULL(c.FMSTENSI,'-') as FMSTENSI,ISNULL(c.FMSNADI,'-') as FMSNADI,ISNULL(c.FMSSUHU,'-') as FMSSUHU,ISNULL(c.FMSRR,'-') as FMSRR,ISNULL(c.FMSBB,'-') as FMSBB,ISNULL(c.FMSTB,'-') as FMSTB "
            q1 += q2
            query = " SELECT {},(SELECT TOP 1 KODEASSESMENT FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT) as KODEASSESMENT,MRDNO_TRANSAKSI,ISNULL((SELECT TOP 1 FMSKLU FROM SOAPI_RJ WHERE FMSBUKTI_ID=MRDNO_TRANSAKSI),'-') as keluhanUtama,ISNULL(MRDANJURANPERIKSA,'-') as anjuranPeriksa,ISNULL(MRDTERAPI,'-') as MRDTERAPI,ISNULL(convert(varchar, MRDTGL_DIAGNOSA, 106),'') as MRDTGL_DIAGNOSA,ISNULL(MRD_STATUS_PRWT,'') as MRD_STATUS_PRWT,ISNULL(convert(varchar, MR_DIAGNOSA.UPDATERS, 113),'') as UPDATERS,MRDKD_DOKTER,ISNULL((SELECT TOP 1 FMDDOKTERN FROM DOKTER WHERE FMDDOKTER_ID=MRDKD_DOKTER),'-') as FMDDOKTERN,MRDKD_PASIEN,ISNULL(MRDSOAPIKET,'(%PERAWAT%)') as MRDSOAPIKET,MRDKD_PRWT,ISNULL((SELECT TOP 1 FMPKLINIKN FROM POLIKLINIK WHERE FMPKLINIK_ID=MRDKD_UNIT),'') as FMPKLINIKN ,MRDNO_TRANSAKSI FROM MR_DIAGNOSA LEFT OUTER JOIN SOAPI_RJ c ON MRDNO_TRANSAKSI=c.FMSBUKTI_ID LEFT OUTER JOIN MR_DIAGNOSA_GIGI_VISUAL vs ON MRDNO_TRANSAKSI=vs.MDG_NO_TRANSAKSI WHERE MRDKD_PASIEN='{}' ORDER BY  convert(datetime, MRDTGL_DIAGNOSA, 103) DESC".format(
                q1, request.GET["MRDKD_PASIEN"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            return HttpResponse(json_data, content_type="application/json")
        elif q == "Openpenyakit":
            query = "Select a.MRPNO_TRANSAKSI,MRPURUT_MASUK, convert(varchar, MRPTGL_MASUK, 105) as MRPTGL_MASUK,MRPKD_PENYAKIT,b.PENYAKIT,a.MRPSTAT_DIAG,c.MSDIAGNOSANAMA,a.MRPKASUS,d.MSKASUSNAMA, ISNULL(a.MRPIMUNKE, 0 ) as MRPIMUNKE,ISNULL(b.STATUS_IMUN, 0 ) as STATUS_IMUN "
            query += " FROM  MR_PENYAKIT a,PENYAKIT b,STATUSDIAGNOSA c,STATUSKASUS d "
            query += " where a.MRPKD_PENYAKIT=b.kd_penyakit and a.MRPSTAT_DIAG=c.MSDIAGNOSAID and a.MRPKASUS=d.MSKASUSID "
            query += " and MRPNO_TRANSAKSI='{}' order by MRPURUT_MASUK ".format(
                request.GET["NO_TRANSAKSI"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "OpenTindakanMedis":
            query = "select MRTKD_TINDAKAN,MRTKD_PASIEN,MRTKD_UNIT,CONVERT(varchar,MRTTGL_MASUK,105) as MRTTGL_MASUK,MRTURUT_MASUK,MRTNOTRANSAKSI,CONVERT(varchar,MRTTGL_TINDAKAN,105) as MRTTGL_TINDAKAN,b.FMI9KETERANGAN as MRTKD_TINDAKANN from  MR_TINDAKAN a,MR_ICD9 b where "
            query += " a.MRTKD_TINDAKAN=b.FMI9KODE  and MRTNOTRANSAKSI='{}'".format(
                request.GET["NO_TRANSAKSI"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenTindakanMedisPicker":
            query = "select FMI9KODE,FMI9KETERANGAN from MR_ICD9 "
            FMI9KODE = ""
            FMI9KETERANGAN = ""
            if "FMI9KODE" in request.GET:
                FMI9KODE = request.GET["FMI9KODE"]
            if "FMI9KETERANGAN" in request.GET:
                FMI9KETERANGAN = request.GET["FMI9KETERANGAN"]
            query += " where FMI9KODE LIKE '{}{}{}' ".format("%", FMI9KODE, "%")
            query += " and FMI9KETERANGAN LIKE '{}{}{}' ".format(
                "%", FMI9KETERANGAN, "%"
            )

            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenAsesmenPerawatDewasa":
            query = " SELECT MRAP_RWRI,MRAP_RWPK,MRAP_GM,MRAP_KELUHANSKRG,MRAP_RESIKOJATUH,MRAP_NYERI,MRAP_SKIRININGIZI,MRAP_KESIMPULAN,MRAP_KESIMPULAN_PRWT,MRAP_KESIMPULAN_PRWT,MRAP_NAMA_PERAWAT FROM MR_ASESMEN_PERAWAT_DEWASA where MRAP_NO_TRANSAKSI='{}'".format(
                request.GET["MRAP_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenAsesmenPerawatAnak":
            query = " SELECT MRAP_RWRI,MRAP_RWPK,MRAP_GM,MRAP_KELUHANSKRG,MRAP_RWIMN,MRAP_RESIKOJATUH,MRAP_NYERI,MRAP_RWTK,MRAP_SKIRININGIZI,MRAP_KESIMPULAN,MRAP_KESIMPULAN_PRWT,MRAP_NAMA_PERAWAT FROM MR_ASESMEN_PERAWAT_ANAK where MRAP_NO_TRANSAKSI='{}'".format(
                request.GET["MRAP_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaAnak":
            query = " select MRDA_NO_TRANSAKSI,MRDA_RPANAK,MRDA_PDS,MRDA_RIWAYATPRENATAL,MRDA_RIWAYATVAKSINASI,MRDA_FISIK from MR_DIAGNOSA_ANAK where MRDA_NO_TRANSAKSI='{}'".format(
                request.GET["MRDA_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaJiwa":
            query = " SELECT MRDJ_NO_TRANSAKSI,MRDJ_PDS,MRDJ_KEADAAN_UMUM,MRDJ_PSIKIATRIK FROM MR_DIAGNOSA_JIWA WHERE MRDJ_NO_TRANSAKSI='{}'".format(
                request.GET["MRDJ_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaKulit":
            query = " SELECT MRDK_NO_TRANSAKSI,MRDK_RIWAYAT,MRDK_PEMERIKSAAN_FISIK,MRDK_DIAGNOSIS FROM MR_DIAGNOSA_KULIT where MRDK_NO_TRANSAKSI='{}'".format(
                request.GET["MRDK_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaMata":
            query = " SELECT MDM_NO_TRANSAKSI,MDM_OPTA,MDM_OPTA_IMG1,MDM_OPTA_IMG2,MDM_PKS,MDM_PDS FROM MR_DIAGNOSA_MATA WHERE MDM_NO_TRANSAKSI='{}'".format(
                request.GET["MDM_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaPenyakitDalam":
            query = " SELECT MRDPD_PDS,MRDPD_KEADAAN_UMUM FROM MR_DIAGNOSA_PENYAKITDALAM where MRDPD_NO_TRANSAKSI='{}'".format(
                request.GET["MRDPD_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaBedah":
            query = "SELECT MRDBU_PDS,MRDBU_KEADAAN_UMUM,MRDBU_NO_TRANSAKSI FROM MR_DIAGNOSA_BEDAH WHERE MRDBU_NO_TRANSAKSI='{}'".format(
                request.GET["MRDPD_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaFisio":
            query = "SELECT MRDF_NO_TRANSAKSI,MRDF_PRT,MRDF_PDS,MRDF_PEMERIKSAAN_FISIK FROM MR_DIAGNOSA_FISIOTERAPI WHERE MRDF_NO_TRANSAKSI='{}'".format(
                request.GET["MRDF_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaAsesDokter":
            query = "SELECT MRDBU_PDS,MRDBU_KEADAAN_UMUM,MRDBU_NO_TRANSAKSI,MRD_PENUNJANG,MRD_RIWAYAT FROM MR_DIAGNOSA_TAMBAHAN WHERE MRDBU_NO_TRANSAKSI='{}'".format(
                request.GET["MRDPD_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()

        elif q == "OpenDiagnosaUmum":
            query = "SELECT MRDBU_PDS,MRDBU_KEADAAN_UMUM,MRDBU_NO_TRANSAKSI FROM MR_DIAGNOSA_UMUM WHERE MRDBU_NO_TRANSAKSI='{}'".format(
                request.GET["MRDPD_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaOrthopedy":
            query = "SELECT MRDBU_PDS,MRDBU_KEADAAN_UMUM,MRDBU_NO_TRANSAKSI FROM MR_DIAGNOSA_ORTHO WHERE MRDBU_NO_TRANSAKSI='{}'".format(
                request.GET["MRDPD_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaGigiMulut":
            query = "SELECT MDG_NO_TRANSAKSI,MDG_RIWAYATPENYAKIT,MDG_PEMERIKSAANMULUT,MDG_OKLUSI,MDG_ODONTOGRAM,MDG_GEJALA,MDG_PDS FROM MR_DIAGNOSA_GIGIMULUT where MDG_NO_TRANSAKSI='{}'".format(
                request.GET["MRDPD_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaGigiVisual":
            query = "SELECT MDG_NO_TRANSAKSI,MDG_VISUAL_1,MDG_VISUAL_2,MDG_VISUAL_3,MDG_VISUAL_4,MDG_VISUAL_5 FROM MR_DIAGNOSA_GIGI_VISUAL WHERE MDG_NO_TRANSAKSI='{}'".format(
                request.GET["MRDPD_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaObsgynGinekologi":
            query = " SELECT MRDOG_PDS,MRDOG_FISIK,MRDOG_PALPASI,MRDOG_PERIKSA_DALAM,MRDOG_NO_TRANSAKSI FROM MR_DIAGNOSA_OBSGYN_GINEKOLOGI where MRDOG_NO_TRANSAKSI='{}'".format(
                request.GET["MRDOG_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenDiagnosaObsgynObstetri":
            query = " SELECT MRDOG_NO_TRANSAKSI,MRDOG_DS,MRDOG_GPA,MRDOG_ANTENATAL,MRDOG_RIWAYAT,MRDOG_KEADAAN_UMUM,MRDOG_STATUS_OBSTETRIK,MRDOG_PEMERIKSAAN_LAB_DARAH FROM MR_DIAGNOSA_OBSGYN_OBSTETRIK WHERE MRDOG_NO_TRANSAKSI='{}'".format(
                request.GET["MRDOG_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenRiwayatObstetri":
            query = " SELECT (SELECT FMKOBLAHIR FROM OBSGYN_KEADAAN_LAHIR WHERE FMKOBKD_LAHIR=PPNKEAADAN_LAHIR )as keadaanKehamilan"
            query += " ,(SELECT TOP 1 FMTOBTINDAKAN FROM OBSGYN_TINDAKAN_MEDIS WHERE FMTOBKD_TINDAKAN=(SELECT  TOP 1 FJOBTINDAKAN FROM OBSGIEN_JADWAL WHERE FJOBKD_PASIEN=PPNKD_RM_IBU)) as caraPersalinan"
            query += " ,convert(varchar, PPNTGL_LAHIR, 105)  as tglLahir "
            query += "  ,CASE WHEN PPNTEMPAT_LAHIR='0' THEN 'RUMAH SAKIT' "
            query += "  ELSE 'LUAR RUMAHSAKIT' END as 'tempatPenolong' "
            query += "  FROM PASIENPERINATAL WHERE PPNKD_RM_IBU='{}' ".format(
                request.GET["kdPasien"]
            )

            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        elif q == "OpenDiagnosaTHT":
            query = " SELECT MRDTH_OBATKONSUMSI,MRDTH_KONDISIUMUM,MRDTH_SISTEMKARDIORESPIRASI,MRDTH_STATUSLOKASI,MRDTH_INTRUKSIAWALDOKTER FROM MR_DIAGNOSA_THT WHERE MRDTH_NO_TRANSAKSI='{}'".format(
                request.GET["MRDTH_NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "OpenpenyakitHIS":
            query = "Select a.MRPNO_TRANSAKSI,MRPURUT_MASUK,MRPKD_PENYAKIT,b.PENYAKIT,a.MRPSTAT_DIAG,c.MSDIAGNOSANAMA,a.MRPKASUS,d.MSKASUSNAMA,a.MRPIMUNKE,convert(varchar, a.MRPTGL_MASUK, 105) as MRPTGL_MASUK"
            query += " FROM  MR_PENYAKIT a,PENYAKIT b,STATUSDIAGNOSA c,STATUSKASUS d"
            query += " where a.MRPKD_PENYAKIT=b.kd_penyakit and a.MRPSTAT_DIAG=c.MSDIAGNOSAID"
            query += " and a.MRPKASUS=d.MSKASUSID And MRPKD_PASIEN='{}'   order by MRPTGL_MASUK,MRPURUT_MASUK".format(
                request.GET["MRPKD_PASIEN"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerPenyakit":
            query = "select KD_PENYAKIT,PENYAKIT from penyakit"
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "pickerSetPenyakitCPPT":
            query = "SELECT RTRIM(MP.MRPKD_PENYAKIT) as MRPKD_PENYAKIT,P.PENYAKIT"
            query += " FROM MR_PENYAKIT MP"
            query += " LEFT JOIN PENYAKIT P ON MP.MRPKD_PENYAKIT=P.KD_PENYAKIT"
            query += " where MRPSTAT_DIAG='5' AND MRPNO_TRANSAKSI='{}' ".format(
                request.GET["NO_TRANSAKSI"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerPenyakitSearch":
            query = "	select KD_PENYAKIT,PENYAKIT from penyakit where kd_penyakit LIKE '{}{}{}' and PENYAKIT LIKE '{}{}{}'".format(
                "%", request.GET["cariKd"], "%", "%", request.GET["cariPenyakit"], "%"
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerDokterSearch":
            query = "	select FMDDOKTER_ID,FMDDOKTERN,KODEDOKTER from DOKTER where FMDDOKTER_ID LIKE '{}{}{}' and FMDDOKTERN LIKE '{}{}{}'".format(
                "%", request.GET["cariKd"], "%", "%", request.GET["cariDokter"], "%"
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerDokterSearch2":
            query = "Select c.FMKDOKTER_ID,a.FMDDOKTERN,a.KODEDOKTER,c.FMKKLINIK_ID,b.FMPKLINIKN "
            query += " from DOKTER a,POLIKLINIK b,DOKTER_KLINIK c "
            query += " WHERE c.FMKDOKTER_ID=a.FMDDOKTER_ID and "
            query += " c.FMKKLINIK_ID=b.FMPKLINIK_ID and a.FMDSTATUS=0 AND "
            query += " FMKKLINIK_ID='{}' order by FMDDOKTERN ".format(
                request.GET["FMKKLINIK_ID"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerNoRujukanSearch":
            # dataPickerNoRujukanSearch
            # query="	SELECT RUNOMOR,RUTRANSAKSI,APPOITMENT,RUPENYAKIT,RUPOLI,RUKETERANG, RUDOKTER,CONVERT(varchar,RUTANGGAL,105) as RUTANGGAL FROM RUJUKAN_KONTROL WHERE RUNOMOR LIKE '{}{}{}' AND  LEFT(RUNOMOR,5)='RSIK/' order by RUNOMOR desc".format('%',request.GET['cariKd'],'%')
            # if 'noTrans' in request.GET:
            query = "	SELECT RUNOMOR,RUTRANSAKSI,APPOITMENT,RUPENYAKIT,RUPOLI,RUKETERANG, RUDOKTER,CONVERT(varchar,RUTANGGAL,105) as RUTANGGAL FROM RUJUKAN_KONTROL WHERE RUTRANSAKSI='{}' AND  LEFT(RUNOMOR,5)='RSIK/' order by RUNOMOR desc".format(
                request.GET["noTrans"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "detailNoRujukan":
            query = "	SELECT  TOP 1 RK.APPOITMENT,RUSTATUS,RUNOMOR,RUNOMOR,CONVERT(varchar,RUTANGGAL,105) as TGLKONTROL "
            query += " ,RK.RUPENYAKIT,P.PENYAKIT,B.FMPKLINIKN,B.FMPKLINIK_ID "
            query += " ,AP.STATUS,AP.FAPJAMANTRI,AP.FAPANTRIDOKTER,FAPNAMAPASIEN,FAPALAMAT,CONVERT(varchar,FAPTGLLAHIR,105) as FAPTGLLAHIR "
            query += " ,SUBSTRING(AP.FAPANTRIDOKTER, 3, 1) AS kdAntrain,D.KODEDOKTER,SUBSTRING(AP.FAPANTRIDOKTER, 4, 1) AS TGL_SHIFT "
            query += " ,D.FMDDOKTER_ID,D.FMDDOKTERN,FAPKETERANGAN "
            query += " ,CB.PERUSAHAAN as NAMA_RS,CB.ALAMAT1 as ALAMAT_RS,CB.TELEPON as TELEPON_RS,CB.FAX,CB.KOTA "
            query += " ,RK.RUSTATUS,RK.RUKETERANG,PS.NAMAPASIEN,PS.KD_PASIEN,PS.ALAMAT,PS.NO_ASURANSI,(CASE when PS.JENIS_KELAMIN='1' THEN 'PRIA' ELSE 'WANITA' END) AS JK,AP.FAPCUSSUBID "
            query += " FROM RUJUKAN_KONTROL AS RK  "
            query += " LEFT JOIN PASIEN as PS ON RK.RUPASIEN_ID=PS.KD_PASIEN LEFT JOIN POLIKLINIK as B ON B.FMPKLINIK_ID=RK.RUPOLI  "
            query += " LEFT JOIN PENYAKIT as P ON P.KD_PENYAKIT=RK.RUPENYAKIT LEFT JOIN APPOINTMENT_PASIEN AS AP ON AP.FAPNOTRANSAKSI=RK.APPOITMENT  "
            query += " LEFT JOIN DOKTER AS D ON D.FMDDOKTER_ID=RK.RUDOKTER LEFT JOIN CABANG AS CB ON CB.ALAMAT1<>RK.APPOITMENT  "
            query += " WHERE RK.RUTRANSAKSI='{}' AND RK.RUNOMOR='{}'  ".format(
                request.GET["no_trans"], request.GET["no_suratKontrol"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerJadwalDokter":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
            cabang = Globals().dictfetchall(cursor)
            kdCabang = cabang[0]["CABANG_ID"]

            query = "	DECLARE @tglKontrol datetime; SET @tglKontrol=CONVERT(datetime,'{}',105); ".format(
                request.GET["tglKontrol"]
            )
            query += " Select (CASE WHEN DATEPART(dw,@tglKontrol)='1' then FMJHari01 WHEN DATEPART(dw, @tglKontrol)='2' THEN FMJHari02 "
            query += " WHEN DATEPART(dw, @tglKontrol)='3' THEN FMJHari03 WHEN DATEPART(dw, @tglKontrol)='4' THEN FMJHari04  "
            query += " WHEN DATEPART(dw, @tglKontrol)='5' THEN FMJHari05 WHEN DATEPART(dw, @tglKontrol)='6' THEN FMJHari06 ELSE FMJHari07 END ) as jadwal,  "
            query += " (CASE WHEN DATENAME(dw,@tglKontrol)='Sunday' then 'Minggu' WHEN DATENAME(dw, @tglKontrol)='Monday' THEN 'Senin' "
            query += " WHEN DATENAME(dw, @tglKontrol)='Tuesday' THEN 'Selasa' WHEN DATENAME(dw, @tglKontrol)='Wednesday' THEN 'Rabu'  "
            query += " WHEN DATENAME(dw, @tglKontrol)='Thursday' THEN 'Kamis' WHEN DATENAME(dw, @tglKontrol)='Friday' THEN 'Jumat' ELSE 'Sabtu' END ) as hari1,   "
            query += " FMJShift,SUM(c.FMKDLIMIT) AS LMT,KODEANTRICS  from JADWAL_POLI b,DOKTER_KOUTA c WHERE FMJKD_DOKTER='{}'   ".format(
                request.GET["kdDokter"]
            )
            if kdCabang == "01":
                query += " AND B.FMJKD_DOKTER=c.FMKDDOKTER_ID   AND LEFT(B.FMJShift,1)=LEFT(C.FMDSHIFT,1)AND FMKDSTATUS=1 "
            else:
                query += " AND B.FMJKD_DOKTER=c.FMKDDOKTER_ID   AND LEFT(B.FMJShift,1)=LEFT(C.FMDSHIFT,1)AND FMKDSTATUS=1 AND C.FMKDKELOMPOK_ID='{}'   ".format(
                    request.GET["jenisPasien"]
                )
            query += " GROUP BY (CASE WHEN DATEPART(dw,@tglKontrol)='1' then FMJHari01 WHEN DATEPART(dw, @tglKontrol)='2' THEN FMJHari02   "
            query += " WHEN DATEPART(dw, @tglKontrol)='3' THEN FMJHari03 WHEN DATEPART(dw, @tglKontrol)='4' THEN FMJHari04   "
            query += " WHEN DATEPART(dw, @tglKontrol)='5' THEN FMJHari05 WHEN DATEPART(dw, @tglKontrol)='6' THEN FMJHari06 ELSE FMJHari07 END ),FMJShift,FMKDLIMIT,KODEANTRICS   "
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerKasus":
            query = "select MSKASUSID,MSKASUSNAMA from STATUSKASUS"
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "dataPickerDiagnosa":
            query = "select MSDIAGNOSAID,MSDIAGNOSANAMA FROM STATUSDIAGNOSA"
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getKeadaanKeluar":
            query = " select FMKKRSKODE,FMKKRSKETERANGAN from MR_KEADAAN_KELUAR_RS order by FMKKRSKODE"
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        else:
            edit = "not permited"
    else:
        edit = "not permited"
    return HttpResponse(edit, content_type="application/json")


def getDataHistoryPasien(request):
    if "q" in request.GET:
        q = request.GET["q"]
        if q == "getPasienkunjungan":
            query = " select a.KPKD_POLY,c.FMPKLINIKN,convert(varchar, a.KPTGL_PERIKSA, 105) AS KPTGL_PERIKSA, "
            query += "  a.KPKD_DOKTER,FMDDOKTERN,a.KPJAM_MASUK,KPTGL_KELUAR,KPJAM_KELUAR,b.NAME ,a.KPDIAGNOSA,KPNO_TRANSAKSI from KUNJUNGANPASIEN a,customer b,POLIKLINIK c,DOKTER d "
            query += " where KPKD_PASIEN='{}' and ".format(request.GET["kdPasien"])
            query += " a.KD_CUSTOMER=b.CUSID and a.KPKD_POLY=c.FMPKLINIK_ID and  a.KPKD_DOKTER=d.FMDDOKTER_ID order by KPTGL_PERIKSA DESC"
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getPasienRWI":
            query = "  select b.FMSPESIALISASIN,c.FMKKAMARN,d.FMKNAMA_KAMAR,a.PRWITGL_INAP,  "
            query += " FMDDOKTERN,a.PRWIKPJAM_MASUK,convert(varchar, PRWITGL_KELUAR, 105) AS PRWITGL_KELUAR,PRWIJAM_KELUAR,f.name,a.PRWINO_TRANSAKSI "
            query += " from PASIENRAWATINAP a,SPESIALISASI b,KAMAR_KELAS c,KAMAR d,DOKTER e,customer f "
            query += " where PRWIKD_PASIEN='{}' and ".format(request.GET["kdPasien"])
            query += " a.PRWIKD_SPECIAL=b.FMSPESIALISASI_ID and a.PRWIKD_KELAS=c.FMKKODEKLAS and a.PRWIKD_KAMAR=d.FMKKAMAR_ID and a.PRWIKD_CUSTOMER=F.CUSID and a.PRWIKD_DOKTER=e.FMDDOKTER_ID order by PRWITGL_MASUK DESC"
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getPenyakitPasien":
            query = (
                "  Select a.MRPNO_TRANSAKSI,MRPURUT_MASUK,MRPKD_PENYAKIT,b.PENYAKIT,  "
            )
            query += (
                " a.MRPSTAT_DIAG,c.MSDIAGNOSANAMA,a.MRPKASUS,d.MSKASUSNAMA,b.NOTES "
            )
            query += "  FROM  MR_PENYAKIT a,PENYAKIT b,STATUSDIAGNOSA c,STATUSKASUS d  "
            query += " where MRPNO_TRANSAKSI='{}' And a.MRPKD_PENYAKIT=b.kd_penyakit and  ".format(
                request.GET["noTrans"]
            )
            query += " a.MRPSTAT_DIAG=c.MSDIAGNOSAID and a.MRPKASUS=d.MSKASUSID order by MRPURUT_MASUK "
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getDiagnosaPasien":
            query = "  Select a.MRDNO_TRANSAKSI,a.MRDKD_UNIT,b.FMPKLINIKN As Unit,a.MRDNO_TRANSAKSI,convert(varchar, MRDTGL_DIAGNOSA, 105) AS MRDTGL_DIAGNOSA,MRDKD_DOKTER,  "
            query += " c.FMDDOKTERN,a.MRDDIAGNOSA_UTAMA from MR_DIAGNOSA a,POLIKLINIK b,DOKTER c "
            query += "  where a.MRDKD_UNIT=b.FMPKLINIK_ID and a.MRDKD_DOKTER=c.FMDDOKTER_ID and "
            query += " a.MRDKD_PASIEN='{}' Union  ".format(request.GET["kdPasien"])
            query += "  Select a.MRDNO_TRANSAKSI,a.MRDKD_UNIT,b.FMKNAMA_KAMAR As Unit,a.MRDNO_TRANSAKSI,convert(varchar, MRDTGL_DIAGNOSA, 105) AS MRDTGL_DIAGNOSA,MRDKD_DOKTER,  "
            query += (
                " c.FMDDOKTERN,a.MRDDIAGNOSA_UTAMA from MR_DIAGNOSA a,KAMAR b,DOKTER c "
            )
            query += "  where a.MRDKD_UNIT=b.FMKKAMAR_ID and a.MRDKD_DOKTER=c.FMDDOKTER_ID and "
            query += " a.MRDKD_PASIEN='{}' Order by MRDTGL_DIAGNOSA DESC  ".format(
                request.GET["kdPasien"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getDiagnosaPenyakitD":
            query = (
                "  Select a.MRPNO_TRANSAKSI,MRPURUT_MASUK,MRPKD_PENYAKIT,b.PENYAKIT,  "
            )
            query += (
                " a.MRPSTAT_DIAG,c.MSDIAGNOSANAMA,a.MRPKASUS,d.MSKASUSNAMA,b.NOTES "
            )
            query += "  FROM  MR_PENYAKIT a,PENYAKIT b,STATUSDIAGNOSA c,STATUSKASUS d  "
            query += " where MRPNO_TRANSAKSI='{}' And a.MRPKD_PENYAKIT=b.kd_penyakit and  ".format(
                request.GET["noTrans"]
            )
            query += " a.MRPSTAT_DIAG=c.MSDIAGNOSAID and a.MRPKASUS=d.MSKASUSID order by MRPURUT_MASUK "
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getTransLab":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
            cabang = Globals().dictfetchall(cursor)
            kdCabang = cabang[0]["CABANG_ID"]
            if kdCabang == "35":
                query = " Select KPNO_TRANSAKSI AS MLHNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) AS MLHTGL_MASUK from KUNJUNGANPASIEN A,hasilLIS B where a.KPNO_TRANSAKSI=b.NOLAB_RS "
                query += " and  b.NORM='{}' ".format(request.GET["kdPasien"])
                query += " group by KPNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) union select KPNO_TRANSAKSI AS MLHNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) AS MLHTGL_MASUK from KUNJUNGANPASIEN A,SENDTOHIS B where a.KPNO_TRANSAKSI=b.BillingNomor "
                query += " and  KPKD_PASIEN='{}' group by KPNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) ORDER  by MLHTGL_MASUK DESC ".format(
                    request.GET["kdPasien"]
                )
            else:
                query = "Select KPNO_TRANSAKSI AS MLHNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) AS MLHTGL_MASUK from KUNJUNGANPASIEN A,LAB_HASIL B where a.KPNO_TRANSAKSI=b.MLHNO_TRANSAKSI "
                query += " and  MLHKD_PASIEN='{}' ".format(request.GET["kdPasien"])
                query += "  group by KPNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) union select KPNO_TRANSAKSI AS MLHNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) AS MLHTGL_MASUK from KUNJUNGANPASIEN A,SENDTOHIS B where a.KPNO_TRANSAKSI=b.BillingNomor "
                query += " and  KPKD_PASIEN='{}' group by KPNO_TRANSAKSI, convert(varchar, KPTGL_PERIKSA, 105) ORDER  by MLHTGL_MASUK DESC".format(
                    request.GET["kdPasien"]
                )
            # ##print(query)

            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getTransLabD":
            cursor = connection.cursor()
            q = "select * from CABANG"
            cursor.execute(q)
            cabang = Globals().dictfetchall(cursor)
            kdCabang = cabang[0]["CABANG_ID"]

            query = " SELECT LAB_TEST.MTLLABN as LabNama,LAB_PERIKSA.FMB_NAMAPEMERIKSAAN as LabMetode"
            query += " ,KLAS_PRODUK_RAD_LAB.FMKKLASN  as KelompokPx,LAB_HASIL.MLHHASIL as LabHasil,LAB_TEST.MTLSATUAN as LabSatuan"
            query += " ,CASE WHEN (SELECT JENIS_KELAMIN FROM PASIEN where KD_PASIEN=LAB_HASIL.MLHKD_PASIEN)='1' THEN "
            query += " LAB_TEST.MTLNORMAL_LAKI2 ELSE LAB_TEST.MTLNORMAL_WANITA END as LabHargaNorm"
            query += " ,LAB_TEST.MTLKD_LAB as LabAutoNomor,LAB_TEST.MTLKETERANGAN as LabKeterangan,LAB_HASIL.MLHPRINT as LabStatus"
            query += " FROM LAB_HASIL "
            query += " LEFT JOIN LAB_PERIKSA ON LAB_HASIL.MLHKD_LAB=LAB_PERIKSA.FMB_KODEPEMERIKSAAN"
            query += " LEFT JOIN LAB_TEST ON LAB_HASIL.MLHKD_LAB=LAB_TEST.MTLKD_LAB"
            query += " LEFT JOIN KLAS_PRODUK_RAD_LAB ON LAB_TEST.MTLPRODUK = KLAS_PRODUK_RAD_LAB.FMKKLAS_ID"
            query += " where MLHNO_TRANSAKSI='{}' ".format(
                request.GET["noTrans"], request.GET["noTrans"]
            )

            cursor = connection.cursor()
            cursor.execute(query)
            ##print(query)
            result = []
            result = Globals().dictfetchall(cursor)
            if (int(len(result))) > 0:
                json_data = json.dumps(result, cls=DjangoJSONEncoder)
                edit = json_data
                cursor.close()
            else:
                if kdCabang == "35":
                    query = "SELECT TARIF_NAME as LabNama,PARAMETER_NAME as LabMetode,KEL_PEMERIKSAAN as KelompokPx,HASIL as LabHasil,SATUAN as LabSatuan,NILAI_RUJUKAN as LabHargaNorm,URUT_BOUND as LabAutoNomor ,'' as LabKeterangan,'' as LabStatus  "
                    query += " FROM hasilLIS"
                    query += " where NOLAB_RS='{}' ORDER BY LabAutoNomor".format(
                        request.GET["noTrans"]
                    )
                else:
                    query = "Select LabAutoNomor, BillingNomor, LabHeaderID, LabNomor, LabKode, LabNama, LabMetode, LabHasil, LabSatuan, LabHargaNorm, LabKeterangan, UserDate, LabStatus,"
                    query += " KelompokPx , ValUserName From SENDTOHIS where BillingNomor='{}' ".format(
                        request.GET["noTrans"]
                    )
                # ##print(query)
                cursor = connection.cursor()
                cursor.execute(query)
                result = []
                result = Globals().dictfetchall(cursor)
                json_data = json.dumps(result, cls=DjangoJSONEncoder)
                edit = json_data
                cursor.close()
        elif q == "getTransRad":
            query = "Select MRHNO_TRANSAKSI,convert(varchar, MRHTGL_MASUK, 105) AS MRHTGL_MASUK from RAD_HASIL  "
            query += " where MRHKD_PASIEN='{}' group by MRHNO_TRANSAKSI,MRHTGL_MASUK ORDER  by MRHTGL_MASUK DESC ".format(
                request.GET["kdPasien"]
            )
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
        elif q == "getTransRadD":
            query = " Select a.MRHKD_PRODUK,MRHHASIL,b.FMPPRODUKN FROM RAD_HASIL a,produk b "
            query += " Where a.MRHKD_PRODUK=b.FMPPRODUK_ID and  "
            query += " MRHNO_TRANSAKSI='{}'".format(request.GET["noTrans"])
            # ##print(query)
            cursor = connection.cursor()
            cursor.execute(query)
            result = []
            result = Globals().dictfetchall(cursor)
            json_data = json.dumps(result, cls=DjangoJSONEncoder)
            edit = json_data
            cursor.close()
            # return HttpResponse(json_data, content_type="application/json")
        else:
            edit = "not permited"
    else:
        edit = "not permited"
    return HttpResponse(edit, content_type="application/json")


## ERESEP ##
def eResepPage(request):
    try:
        del request.session["FDRRACIK_ID"]
        request.session.modified = True
    except Exception as e:
        error = e
    # Check Session
    if "userauth" in request.session:
        is_login = request.session["userauth"]
    else:
        is_login = False

    # Code
    if is_login:
        response = render(request, "emr/eresep/home.html", {})
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def eResepRacikPage(request):
    # Check Session
    if "userauth" in request.session:
        is_login = request.session["userauth"]
    else:
        is_login = False

    # Code
    if is_login:
        response = render(request, "emr/eresepracikan/home.html", {})
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


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


def crudRacikanResep(request):
    json_data_list = []
    edit = {}
    if request.method == "POST":
        q = request.POST["q"]
        now = datetime.now()
        if q == "entryRacikanResep":
            cursor = connection.cursor()
            try:
                tglRaw = request.POST["Tanggal"]
                tgl = tglRaw.split("-")
                tglConv = "{}-{}-{}".format(tgl[2], tgl[1], tgl[0])
                ks = "NULL"
                isi = "'{}'".format(request.POST["KPKD_DOKTER"])
                isi += " ,'{}'".format(tglConv)
                isi += " , '{}' ".format(request.POST["FHRNO_TRANSAKSI"])
                isi += " , '{}' ".format(request.POST["FERCKNBENTUK_ID"])
                isi += " , '{}' ".format(request.POST["FERCKNBENTUKS"])
                isi += " , '{}' ".format(request.POST["FERCKNBENTUKN"])
                isi += " , '{}' ".format(request.POST["FERCKNQTYRMW"])
                isi += " , '{}' ".format(request.POST["FERCKNQTY"])
                isi += " , '{}' ".format(request.POST["FERCKNDOSIS"])
                isi += " , '{}' ".format(request.POST["FERCKNDOSIS2"])
                isi += " , '{}' ".format(request.POST["FERCKNSIGNAF"])
                isi += " , '{}' ".format(request.POST["FERCKNSIGNAS"])
                isi += " , '{}' ".format(request.POST["FERCKNSIGNAW"])
                isi += " , '{}' ".format(nl2br(request.POST["FERCKNSIGNA"]))
                isi += " , '{}' ".format(request.POST["FERRACIK_ID"].strip())
                isi += " , '{}' ".format(request.POST["FERRACIKDNO"])
                isi += " , '{}' ".format(request.POST["FERRACIKDBRG_ID"])
                isi += " , '{}' ".format(request.POST["FERRACIKDBRGN"])
                isi += " , '{}' ".format(request.POST["FERRACIKDKK"])
                isi += " , '{}' ".format(request.POST["FERRACIKDSATKK"])
                isi += " , '{}' ".format(request.POST["FERRACIKDQTYJENIS"])
                isi += " , '{}' ".format(request.POST["FERRACIKDQTY"])
                isi += " , '{}' ".format(request.POST["FERDKEBQTY"])
                isi += " , '{}' ".format(request.POST["FERDKEBQTY2"])
                isi += " , '{}' ".format(request.POST["FERDKEBSATUAN"])
                isi += " , '{}' ".format(request.POST["FERDDOSIS"])
                isi += " , '{}' ".format(request.POST["StatusAUD"])

                query = "EXEC AUD_ERESEPRACIK {}".format(isi)
                # prints(query)
                cursor.execute(query)
                result_set = cursor.fetchall()
                # prints(result_set)

                # edit= json.loads(result_set)
                # edit= json.dumps(result_set)
                # edit['success']=True
                # edit['message']="Method Valid"

                if int(len(result_set)) > 0:
                    edit["success"] = True
                    edit["message"] = "" + result_set[0][0]
                else:
                    edit["success"] = False
                    edit["message"] = "Gagal Insert "
            finally:
                cursor.close()

        elif q == "entryRacikanResep2":
            # cursor =  connection.cursor()
            query = "SET NOCOUNT ON; DECLARE @ListRacikan ListMR_Racikan2; "
            query += " DECLARE @KD_DOKTER varchar(20);   "
            query += " DECLARE @FDRRACIK_ID varchar(60);  "
            query += " DECLARE @NO_TRANSAKSI varchar(60); "
            query += " DECLARE @TANGGAL datetime;  "
            query += " SET @KD_DOKTER='{}' ".format(request.POST["DOKTER_ID"])
            query += " SET @FDRRACIK_ID='{}' ".format(
                Globals().input(request.POST, "FDRRACIK_ID", "NULL")
            )
            query += " SET @NO_TRANSAKSI='{}' ".format(request.POST["NO_TRANSAKSI"])
            # query+=" SET @TANGGAL=CONVERT(datetime,'{}',105) ".format(request.POST['TANGGAL'])
            query += " SET @TANGGAL='{}' ".format(request.POST["TANGGAL"])
            ListRacikan = json.loads(request.POST["ListRacikan"])
            # print(ListRacikan)
            for value in ListRacikan:
                query += " INSERT INTO @ListRacikan (FERCKNBENTUKN,FERCKNBENTUKS,FERCKNBENTUK_ID,FERCKNDOSIS,FERCKNDOSIS2,FERCKNQTY,FERCKNQTYRMW,FERCKNSIGNA,FERCKNSIGNAF,FERCKNSIGNAS,FERCKNSIGNAW,FERDDOSIS,FERDKEBQTY,FERDKEBQTY2,FERDKEBSATUAN,FERRACIKDBRGN,FERRACIKDBRG_ID,FERRACIKDKK,FERRACIKDNO,FERRACIKDQTY,FERRACIKDQTYJENIS,FERRACIKDSATKK,FERRACIK_ID,FHRNO_TRANSAKSI,KPKD_DOKTER,Tanggal)"
                query += " VALUES("
                query += " '%s' " % value["FERCKNBENTUKN"]  # FERCKNBENTUKN,
                query += " ,'%s' " % value["FERCKNBENTUKS"]  # FERCKNBENTUKS,
                query += " ,'%s' " % value["FERCKNBENTUK_ID"]  # FERCKNBENTUK_ID,
                query += " ,'%s' " % value["FERCKNDOSIS"]  # FERCKNDOSIS,
                query += " ,'%s' " % value["FERCKNDOSIS2"]  # FERCKNDOSIS2,
                query += " ,'%s' " % value["FERCKNQTY"]  # FERCKNQTY,
                query += " ,'%s' " % value["FERCKNQTYRMW"]  # FERCKNQTYRMW,
                query += " ,'%s' " % value["FERCKNSIGNA"]  # FERCKNSIGNA,
                query += " ,'%s' " % value["FERCKNSIGNAF"]  # FERCKNSIGNAF,
                query += " ,'%s' " % value["FERCKNSIGNAS"]  # FERCKNSIGNAS,
                query += " ,'%s' " % value["FERCKNSIGNAW"]  # FERCKNSIGNAW,
                query += " ,'%s' " % value["FERDDOSIS"]  # FERDDOSIS,
                query += " ,'%s' " % value["FERDKEBQTY"]  # FERDKEBQTY,
                query += " ,'%s' " % value["FERDKEBQTY2"]  # FERDKEBQTY2,
                query += " ,'%s' " % value["FERDKEBSATUAN"]  # FERDKEBSATUAN,
                query += " ,'%s' " % value["FERRACIKDBRGN"]  # FERRACIKDBRGN,
                query += " ,'%s' " % value["FERRACIKDBRG_ID"]  # FERRACIKDBRG_ID,
                query += " ,'%s' " % value["FERRACIKDKK"]  # FERRACIKDKK,
                query += " ,'%s' " % value["FERRACIKDNO"]  # FERRACIKDNO,
                query += " ,'%s' " % value["FERRACIKDQTY"]  # FERRACIKDQTY,
                query += " ,'%s' " % value["FERRACIKDQTYJENIS"]  # FERRACIKDQTYJENIS,
                query += " ,'%s' " % value["FERRACIKDSATKK"]  # FERRACIKDSATKK,
                query += " ,@FDRRACIK_ID "  # FERRACIK_ID,
                query += " ,@NO_TRANSAKSI "  # FHRNO_TRANSAKSI,
                query += " ,@KD_DOKTER "  # KPKD_DOKTER,
                query += " ,@TANGGAL "  # Tanggal
                query += " );"
            # query+=" EXEC EMRRJ_ERESEP_RACIKAN @NO_TRANSAKSI,@KD_DOKTER,%s,@TANGGAL,@ListRacikan,'%s'" % ( Globals().input(request.POST,'FDRRACIK_ID',None),request.POST['DOKTER_ID'])
            query += " EXEC EMRRJ_ERESEP_RACIKAN @NO_TRANSAKSI,@KD_DOKTER,%s,@TANGGAL,@ListRacikan,%s"
            # print(query)
            # cursor.execute(query)
            # result_set = cursor.fetchall()
            # print(query)
            NORESEPRACIK = Globals().input(request.POST, "FDRRACIK_ID", None)
            if NORESEPRACIK == "NULL":
                NORESEPRACIK = None
            # print("EMRRJ_ERESEP_RACIKAN")
            # print(query, [NORESEPRACIK, request.POST["DOKTER_ID"]])
            result_set = Globals().getDataSP(
                query, [NORESEPRACIK, request.POST["DOKTER_ID"]], setIndex=2
            )
            # print(result_set)
            if int(len(result_set)) > 0:
                # FDRRACIK_ID=result_set[0][0]
                FDRRACIK_ID = result_set[0]["FERRACIK_ID"]
                query = " DECLARE @ListRacikan ListMR_Racikan2; "
                query += " DECLARE @KD_DOKTER varchar(20);   "
                query += " DECLARE @FDRRACIK_ID varchar(60);  "
                query += " DECLARE @NO_TRANSAKSI varchar(60); "
                query += " DECLARE @TANGGAL datetime;  "
                query += " SET @KD_DOKTER='{}' ".format(request.POST["DOKTER_ID"])
                query += " SET @FDRRACIK_ID='{}' ".format(FDRRACIK_ID)
                query += " SET @NO_TRANSAKSI='{}' ".format(request.POST["NO_TRANSAKSI"])
                # query+=" SET @TANGGAL=CONVERT(datetime,'{}',105) ".format(request.POST['TANGGAL'])
                query += " SET @TANGGAL='{}'".format(request.POST["TANGGAL"])
                # query+=" EXEC EMRRJ_ERESEP_RACIKAN_TRANSFER @NO_TRANSAKSI,%s,@KD_DOKTER,@FDRRACIK_ID,@TANGGAL,@KD_DOKTER" % (Globals().input(request.POST,'FDRBUKTI_ID',None))
                NORESEP = Globals().input(request.POST, "FDRBUKTI_ID", None)
                if NORESEP == "NULL":
                    NORESEP = None
                query += " EXEC EMRRJ_ERESEP_RACIKAN_TRANSFER @NO_TRANSAKSI,%s,@KD_DOKTER,@FDRRACIK_ID,@TANGGAL,@KD_DOKTER"
                # print("EMRRJ_ERESEP_RACIKAN_TRANSFER")
                # print(query, [NORESEP])
                # cursor.execute(query)
                result_set2 = Globals().executeQuery(query, [NORESEP])
                edit["success"] = True
                edit["message"] = "" + FDRRACIK_ID
            else:
                edit["success"] = False
                edit["message"] = "Gagal Insert "

        elif q == "deleteRacikanResep":
            cursor = connection.cursor()
            query = "DELETE FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}' ".format(
                request.POST["FERRACIKD_ID"]
            )
            cursor.execute(query)
            query = "DELETE FROM ERESEPRACIK WHERE FERRACIK_ID='{}' ".format(
                request.POST["FERRACIKD_ID"]
            )
            cursor.execute(query)
            query = "DELETE FROM ERESEPDOKTERD WHERE FDRRACIK_ID='{}' ".format(
                request.POST["FERRACIKD_ID"]
            )
            cursor.execute(query)

            # result_set = cursor.fetchall()
            edit["success"] = True
            edit["message"] = "Sukses Hapus"
        elif q == "deleteItemRacikanResep":
            cursor = connection.cursor()
            query = "DELETE FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}' AND FERRACIKDNO='{}'".format(
                request.POST["FERRACIKD_ID"], request.POST["FERRACIKDNO"]
            )
            cursor.execute(query)
            # result_set = cursor.fetchall()
            edit["success"] = True
            edit["message"] = "Sukses Hapus"
        elif q == "deleteEntryResepRJRacikan":
            cursor = connection.cursor()
            query = "DELETE FROM ERESEPDOKTERD WHERE FDRRACIK_ID='{}' AND FDRBUKTI_ID='{}'".format(
                request.POST["FDRRACIK_ID"], request.POST["FDRBUKTI_ID"]
            )
            cursor.execute(query)
            # prints(query)
            # result_set = cursor.fetchall()
            edit["success"] = True
            edit["message"] = "Sukses Hapus"
        else:
            edit["success"] = False
            edit["message"] = "Method Not Valid"
    else:
        edit["success"] = False
        edit["message"] = "Method Not Valid"
    json_data_list.append(edit)
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def crudResepRJ(request):
    json_data_list = []
    edit = {}
    if request.method == "POST":
        q = request.POST["q"]
        now = datetime.now()
        if q == "entryResepRJ":
            cursorUpdate = connection.cursor()
            try:
                NODATE = "{}".format(now.strftime("%Y-%m-%d"))
                if "FDRRACIK_ID" in request.POST:
                    FDRRACIK_ID = request.POST["FDRRACIK_ID"]  # RACIKID
                else:
                    FDRRACIK_ID = "NULL"  # RACIKID

                print
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
                # param=[request.POST['DOKTER_ID'],request.POST['TANGGAL'],NORESEPRJ,request.POST['BUKTI_ID'],'NULL',request.POST['BRG_ID'],request.POST['BRGN'],request.POST['SATUAN'],request.POST['QTY'],request.POST['QTYOUT'],request.POST['DOSIS'],request.POST['SIGNAF'],request.POST['DOSIS2'],request.POST['SIGNAS'],request.POST['SIGNAW'],request.POST['SIGNA'],request.session['user_id'],FDRRACIK_ID,NODATE,'NULL','NULL',request.POST['StatusAUD']]

                try:
                    # cursor.execute(query)
                    # print(query, [])
                    result_set = Globals().getDataSP(query, [], setIndex=2)
                    # print(result_set)

                    # edit= json.dumps(result_set)
                    # prints(result_set)
                    if "FDRRACIK_ID" in request.POST:
                        queryFDRRACIK_ID = "UPDATE ERESEPDOKTERD SET FDRRESEP=(SELECT MIN(FDRRESEP) FROM ERESEPDOKTERD WHERE FDRRACIK_ID='{}') WHERE FDRRACIK_ID='{}'".format(
                            request.POST["FDRRACIK_ID"], request.POST["FDRRACIK_ID"]
                        )
                        cursorUpdate.execute(queryFDRRACIK_ID)

                        # prints(queryFDRRACIK_ID)
                        # prints("update racik")

                    if request.POST["StatusAUD"] == "A":
                        # result_set = cursor.fetchall()

                        if int(len(result_set)) > 0:
                            edit["success"] = True
                            edit["message"] = "" + result_set[0]["FDRBUKTI_ID"]

                            if "SIGNAMODE" in request.POST:
                                queryFDRRACIK_ID = "UPDATE ERESEPDOKTERD SET FDRSIGNAMODE='{}' WHERE FDRBUKTI_ID='{}' AND FDRBRG_ID='{}'".format(
                                    request.POST["SIGNAMODE"],
                                    result_set[0]["FDRBUKTI_ID"],
                                    request.POST["BRG_ID"],
                                )
                                cursorUpdate.execute(queryFDRRACIK_ID)
                        else:
                            edit["success"] = False
                            edit["message"] = "Gagal Insert"
                    else:
                        edit["success"] = True
                        edit["message"] = "Sukses {}".format(request.POST["StatusAUD"])
                except Exception as e:
                    # print(e)
                    edit["success"] = False
                    edit["message"] = str(e)
            finally:
                cursorUpdate.close()
        elif q == "editResepRJ":
            cursor = connection.cursor()
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
                cursor.execute(query)
                # result_set = cursor.fetchall()
                # edit= json.dumps(result_set)
                edit["success"] = True
                # edit['message']=result_set[0][0]
                edit["message"] = "Sukses"
            finally:
                cursor.close()
        elif q == "saveEResepManual":
            query = " "
            query += " DECLARE @KD_DOKTER varchar(20);   "
            query += " DECLARE @FDRRACIK_ID varchar(20);  "
            query += " DECLARE @NO_TRANSAKSI varchar(20); "
            query += " DECLARE @TANGGAL datetime;  "
            query += " SET @KD_DOKTER='{}' ".format(request.POST["DOKTER_ID"])
            query += " SET @NO_TRANSAKSI='{}' ".format(request.POST["NO_TRANSAKSI"])
            # query+=" SET @TANGGAL=CONVERT(datetime,'{}',105) ".format(request.POST['TANGGAL'])
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
            cursor = connection.cursor()
            try:
                query = "update  ERESEPDOKTER set FHRSTATUS=1,FHRRESEPTEXT='{}' where  FHRNO_TRANSAKSI='{}'".format(
                    getEresepTxT(request.POST["KPNO_TRANSAKSI"]),
                    request.POST["FHRNO_TRANSAKSI"],
                )
                edit["success"] = True
                edit["message"] = "Success Kirim"
                cursor.execute(query)
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

            finally:
                cursor.close()
        elif q == "copyResepRJ":
            cursor = connection.cursor()
            try:
                query = "EXEC DUPLICATE_RESEP '{}','{}',NULL,NULL".format(
                    request.POST["NO_RESEP"], request.POST["NO_TRANS"]
                )
                edit["success"] = True
                edit["message"] = "Method Valid"
                cursor.execute(query)
                copyResep = Globals().dictfetchall(cursor)
                # prints(copyResep)

                query = (
                    "select  * FROM ERESEPDOKTER  where  FHRNO_TRANSAKSI='{}'".format(
                        copyResep[0]["nomor"]
                    )
                )
                cursor.execute(query)
                rows = cursor.fetchall()

                jum = int(len(rows))
                if jum < 1:
                    edit["success"] = False
                    edit["message"] = "Gagal Buat Resep"
                else:
                    edit["success"] = True
                    edit["message"] = "Success Buat Resep"
            finally:
                cursor.close()
        elif q == "deleteObatResep":
            cursor = connection.cursor()
            try:
                query = "delete from ERESEPDOKTERD where FDRBUKTI_ID ='{}' and FDRRESEP='{}'".format(
                    request.POST["FDRBUKTI_ID"], request.POST["FDRRESEP"]
                )
                edit["success"] = True
                edit["message"] = "Method Valid"
                cursor.execute(query)
                query = "Select * from ERESEPDOKTERD where FDRBUKTI_ID ='{}' and FDRRESEP='{}'".format(
                    request.POST["FDRBUKTI_ID"], request.POST["FDRRESEP"]
                )
                cursor.execute(query)
                rows = cursor.fetchall()
                # prints(rows)
                # return HttpResponse(json_data, content_type="application/json")
                jum = int(len(rows))
                if jum > 0:
                    edit["success"] = False
                    edit["message"] = "Gagal Hapus"
                else:
                    edit["success"] = True
                    edit["message"] = "Success Hapus"

            finally:
                cursor.close()
        elif q == "batalkanResepRJ":
            cursor = connection.cursor()
            try:
                query = "UPDATE ERESEPDOKTER SET FHRSTATUS='0' where FHRBUKTI_ID='{}'".format(
                    request.POST["FHRBUKTI_ID"]
                )
                edit["success"] = True
                edit["message"] = "Method Valid"
                cursor.execute(query)
                query = "Select * from ERESEPDOKTER where FHRBUKTI_ID ='{}' and FHRSTATUS='0'".format(
                    request.POST["FHRBUKTI_ID"]
                )
                cursor.execute(query)
                rows = cursor.fetchall()
                # prints(rows)
                # return HttpResponse(json_data, content_type="application/json")
                jum = int(len(rows))
                if jum > 0:
                    edit["success"] = False
                    edit["message"] = "Success Batal Resep"
                else:
                    edit["success"] = True
                    edit["message"] = "Gagal Batal Resep"

            finally:
                cursor.close()
        elif q == "updatePengobatanResepRJ":
            cursor = connection.cursor()
            try:
                queryFDRRACIK_ID = (
                    " UPDATE MR_DIAGNOSA SET MRDTERAPI='%s' WHERE MRDNO_TRANSAKSI='%s'"
                )
                # cursor.execute(queryFDRRACIK_ID,[request.POST['MRDTERAPI'],request.POST['MRDNO_TRANSAKSI']])
                cursor.execute(
                    queryFDRRACIK_ID
                    % (request.POST["MRDTERAPI"], request.POST["MRDNO_TRANSAKSI"])
                )

                edit["success"] = True
                edit["message"] = "Success Update"

            finally:
                cursor.close()

        else:
            edit["success"] = False
            edit["message"] = "Method Not Valid"
    else:
        edit["success"] = False
        edit["message"] = "Method Not Valid"
    json_data_list.append(edit)
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def pickerHistoryResepManual(request):
    query = " SELECT TOP 5 B.KPKD_PASIEN,C.FMDDOKTERN,CONVERT(varchar,A.FHRUPDATE,105) as TGL,A.FHRRESEPTEXT FROM ERESEPDOKTER A "
    query += " LEFT JOIN KUNJUNGANPASIEN B ON A.FHRBUKTI_ID=B.KPNO_TRANSAKSI"
    query += " LEFT JOIN DOKTER C ON B.KPKD_DOKTER=C.FMDDOKTER_ID"
    query += " where FHRRESEPTEXT IS NOT NULL"
    # query+=" AND B.KPKD_PASIEN='{}'".format(request.GET['kdPasien'])
    query += " AND A.KD_CABANG='{}'".format(request.session["kdCabang"])
    query += " ORDER BY A.FHRUPDATE DESC"

    cursor = connection.cursor()
    cursor.execute(query)
    result = []
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    edit = json_data
    cursor.close()
    return HttpResponse(edit, content_type="application/json")


## ERESEP ##
def getAlergiPasien(request):
    query = " SELECT TOP 1 * FROM ALERGI_PASIEN "
    query += " WHERE ALERGI_PASIEN.ALPKD_PASIEN='{}' ".format(request.GET["kdPasien"])
    query += " ORDER BY ALERGI_PASIEN.ALPUPDATED_AT"

    cursor = connection.cursor()
    cursor.execute(query)
    result = []
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    edit = json_data
    cursor.close()
    return HttpResponse(edit, content_type="application/json")


def upload_image(request):
    if request.method == "POST":
        img_url = "-"
        img_url1 = "-"
        namaImage = ""
        if "imagev1" in request.FILES:
            image = request.FILES["imagev1"]
        elif "imagev2" in request.FILES:
            image = request.FILES["imagev2"]
        elif "imagev3" in request.FILES:
            image = request.FILES["imagev3"]
        elif "imagev4" in request.FILES:
            image = request.FILES["imagev4"]
        else:
            image = request.FILES["imagev5"]

        image_types = [
            "image/png",
            "image/jpg",
            "image/jpeg",
            "image/pjpeg",
            "image/gif",
        ]

        if image.content_type not in image_types:
            data = json.dumps({"status": 405, "error": _("Bad image format.")})
            return HttpResponse(data, content_type="application/json", status=405)
        # prints(image.name)
        tmp_file = os.path.join(
            settings.UPLOAD_PATH + "emr/gigi-mulut/visual", image.name
        )
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)
        path = default_storage.save(tmp_file, ContentFile(image.read()))
        img_url = path

        cursor = connection.cursor()
        statusAUD = ""
        if "imagev1" in request.FILES:
            statusAUD = "1"
            data = json.dumps({"status": 200, "imagev1": img_url})
        elif "imagev2" in request.FILES:
            statusAUD = "2"
            data = json.dumps({"status": 200, "imagev2": img_url})
        elif "imagev3" in request.FILES:
            statusAUD = "3"
            data = json.dumps({"status": 200, "imagev3": img_url})
        elif "imagev4" in request.FILES:
            statusAUD = "4"
            data = json.dumps({"status": 200, "imagev4": img_url})
        else:
            statusAUD = "5"
            data = json.dumps({"status": 200, "imagev5": img_url})

        try:
            q = "exec AUD_MR_DIAGNOSA_GIGI_VISUAL %s, %s, %s"
            cursor.execute(q, [request.POST["MDG_NO_TRANSAKSI"], img_url, statusAUD])
        finally:
            cursor.close()

        return HttpResponse(data, content_type="application/json")

    return HttpResponse(_("Invalid request!"))


def getPDFCRM(request):
    json_data_list = []
    edit = {}
    cursor = connection.cursor()
    if request.method == "GET":
        q = request.GET["q"]
        now = datetime.now()
        if q == "getPDFCRM":
            try:
                cursor = connection.cursor()
                q = "select * from CABANG WHERE CABANG_ID={}".format(
                    request.session["kdCabang"]
                )
                cursor.execute(q)
                cabang = Globals().dictfetchall(cursor)
                fileCabang = cabang[0]["CRM_FILE"]
                norm = request.GET["norm"]
                url = "{}{}".format(fileCabang, norm)
                arr = os.listdir(url)

                if len(arr) > 0:
                    edit["success"] = True
                    lst = []
                    arr.sort()
                    for pn in arr:
                        d = {}
                        d["button"] = "Lihat Riwayat"
                        d["nama"] = pn
                        d["url"] = "{}/{}".format(url, pn)
                        lst.append(d)
                    edit["data"] = lst
                else:
                    edit["success"] = False
                    edit["data"] = []
            except:
                edit["success"] = False
                edit["data"] = []
            # ##print(query)

        else:
            edit["success"] = False
            edit["message"] = "Method Not Valid"
    else:
        edit["success"] = False
        edit["message"] = "Method Not Valid"
    json_data_list.append(edit)
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def pdf_view(request):
    name_file = request.GET["name_file"]
    filelocation = request.GET["files"]
    try:
        response = FileResponse(
            open(filelocation, "rb"), content_type="application/pdf"
        )
        response["Content-Disposition"] = "filename={}".format(name_file)
        return response
    except FileNotFoundError:
        raise Http404()


##### INPUT ICD10
def findStatusKasus(request):
    cursor = connection.cursor()
    if "id" in request.GET:
        q = "SELECT * FROM STATUSKASUS WHERE MSKASUSID = %s ORDER BY MSKASUSID ASC "
        cursor.execute(q, [request.GET["id"]])
    else:
        q = "SELECT * FROM STATUSKASUS ORDER BY MSKASUSID ASC "
        cursor.execute(q)

    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


def findStatusDiagnosaKlaim(request):
    cursor = connection.cursor()
    q = "SELECT * FROM STATUSDIAGNOSA WHERE MSDIAGUTAMA > 0 ORDER BY MSDIAGUTAMA ASC "
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


def findStatusDiagnosaKlaimAwal(request):
    cursor = connection.cursor()
    q = (
        "SELECT * FROM STATUSDIAGNOSA WHERE MSDIAGNOSAID ="
        + getattr(env, "REKAMMEDIS_MSDIAGNOSAID_DIAGNOSA_AWAL", "0")
        + " ORDER BY MSDIAGUTAMA ASC "
    )
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


def getDignosaKerjaCPPT(request):
    cursor = connection.cursor()
    q = " SELECT A.*,B.MSKASUSNAMA,C.MSDIAGNOSANAMA,D.PENYAKIT FROM MR_PENYAKIT A"
    q += " JOIN STATUSKASUS B ON B.MSKASUSID = A.MRPKASUS "
    q += " JOIN STATUSDIAGNOSA C ON C.MSDIAGNOSAID = A.MRPSTAT_DIAG "
    q += " JOIN PENYAKIT D ON D.KD_PENYAKIT  = A.MRPKD_PENYAKIT"
    q += " WHERE MRPNO_TRANSAKSI = %s"
    proc_param = [Globals().input(request.GET, "no_transaksi_ri")]
    cursor.execute(q, proc_param)
    result_set = Globals().dictfetchall(cursor)
    json_data = json.dumps(result_set, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


def getDiagnosaPenyakit(request):
    cursor = connection.cursor()
    if "id" in request.GET:
        q = " select KD_PENYAKIT,PENYAKIT,NOTES "
        q += " from penyakit  order by KD_PENYAKIT "
        q += " WHERE KD_PENYAKIT = %s "
        cursor.execute(q, [request.GET["id"]])
    elif "filter" in request.GET:
        if request.GET["filter"] == "top_20":
            key = "%" + request.GET["key"] + "%"
            spesialis = request.GET["spesialis"]
            q = " SELECT TOP 20 a.MRPKD_PENYAKIT as KD_PENYAKIT,b.PENYAKIT,b.NOTES , count(*) as jumlah"
            q += " From MR_PENYAKIT a "
            q += " inner join Penyakit b on a.MRPKD_PENYAKIT=b.KD_PENYAKIT  "
            q += " inner join PASIENRAWATINAP d on a.MRPNO_TRANSAKSI = d.PRWINO_TRANSAKSI"
            q += " INNER JOIN TRANSAKSIPASIENINAP e on e.FTNO_TRANSAKSI = d.PRWINO_TRANSAKSI and e.FTNO_URUT = d.PRWINO_URUT"
            q += " inner join SPESIALISASI c on c.FMSPESIALISASI_ID = d.PRWIKD_SPECIAL"
            q += " where STATUS_APP=0 "
            q += " and c.FMSPESIALISASI_ID = %s "
            q += " and a.MRPKD_PENYAKIT like %s or b.PENYAKIT like %s or b.NOTES like %s  "
            q += " GROUP BY a.MRPKD_PENYAKIT,b.PENYAKIT,b.NOTES"
            q += " order by jumlah desc"
            cursor.execute(q, [spesialis, key, key, key])
        elif request.GET["filter"] == "top_20_rj":
            key = "%" + request.GET["key"] + "%"
            spesialis = request.GET["spesialis"]
            query = " SELECT TOP 20 a.MRPKD_PENYAKIT as KD_PENYAKIT,b.PENYAKIT,b.NOTES,count(*)  From MR_PENYAKIT a,Penyakit b,POLIKLINIK c "
            query += " where STATUS_APP=0 and "
            query += " a.MRPKD_UNIT=c.FMPKLINIK_ID and "
            query += " a.MRPKD_PENYAKIT=b.KD_PENYAKIT and "
            query += " c.FMPKLINIK_ID='{}'  GROUP BY a.MRPKD_PENYAKIT,b.PENYAKIT,b.NOTES ORDER BY count(*) DESC".format(
                spesialis
            )
            cursor.execute(query)
        else:
            key = "%" + request.GET["key"] + "%"
            q = " select TOP 100 KD_PENYAKIT,PENYAKIT,NOTES from penyakit "
            q += " WHERE KD_PENYAKIT like %s or PENYAKIT like %s or NOTES like %s order by KD_PENYAKIT "
            cursor.execute(q, [key, key, key])
    elif "key" in request.GET:
        key = "%" + request.GET["key"] + "%"
        q = " select TOP 100 KD_PENYAKIT,PENYAKIT,NOTES from penyakit "
        q += " WHERE KD_PENYAKIT like %s or PENYAKIT like %s or NOTES like %s order by KD_PENYAKIT "
        cursor.execute(q, [key, key, key])
    else:
        q = " select KD_PENYAKIT,PENYAKIT,NOTES "
        q += " from penyakit  order by KD_PENYAKIT "
        cursor.execute(q)

    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


##### INPUT ICD10 ##########


##### CPPT ##########


def page_cppt(request):
    if "userauth" in request.session:
        is_login = request.session["userauth"]
    else:
        is_login = False

    MODE_DISABLE_HISLAMA = 0
    # if getattr(env, 'MODE_DISABLE_HISLAMA',0)==1:
    # 	MODE_DISABLE_HISLAMA=1
    # Code
    if "noTrans" in request.session:
        NOTRANS = request.session["noTrans"]
    else:
        NOTRANS = "-"
    if is_login:
        response = render(
            request,
            "emr/cppt/home.html",
            {"MODE_DISABLE_HISLAMA": MODE_DISABLE_HISLAMA, "NOTRANS": NOTRANS},
        )
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def save_cppt(request):
    if request.method == "POST":
        cursor = connection.cursor()
        edit = ""
        i = 1
        upload_paths = []

        q = "SET NOCOUNT ON;"
        q += " DECLARE @ListDiagnosa ListMR_PENYAKIT; "
        q += " DECLARE @ListTindakan ListMR_TINDAKAN2; "
        ListDiagnosa = json.loads(request.POST["diagnosaKerja"])
        ListTindakan = json.loads(request.POST["tindakan"])
        for value in ListDiagnosa:
            q += " INSERT INTO @ListDiagnosa (MRPURUT_MASUK, MRPKD_PENYAKIT,MRPSTAT_DIAG,MRPKASUS) "
            q += (
                " VALUES ("
                + str(i)
                + " , '"
                + value["MRPKD_PENYAKIT"]
                + "', '"
                + value["MRPSTAT_DIAG"]
                + "', '"
                + value["MRPKASUS"]
                + "');"
            )
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
        q += " %s ;"  # @STATUS_AUD nvarchar(5) = 'A'

        proc_param = [
            Globals().input(
                request.POST, "notrans"
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
            None
            if Globals().input(request.POST, "TTVTSISTOL") == ""
            else Globals().input(request.POST, "TTVTSISTOL"),  # @TTVTSISTOL int  NULL,
            None
            if Globals().input(request.POST, "TTVDIASTOL") == ""
            else Globals().input(request.POST, "TTVDIASTOL"),  # @TTVDIASTOL int  NULL,
            None
            if Globals().input(request.POST, "TTVNADI") == ""
            else Globals().input(request.POST, "TTVNADI"),  # @TTVNADI int  NULL,
            None
            if Globals().input(request.POST, "TTVNAFAS") == ""
            else Globals().input(request.POST, "TTVNAFAS"),  # @TTVNAFAS int  NULL,
            None
            if Globals().input(request.POST, "TTVSUHU") == ""
            else Globals().input(request.POST, "TTVSUHU"),  # @TTVSUHU float  NULL,
            None
            if Globals().input(request.POST, "TTVBERAT_BADAN") == ""
            else Globals().input(
                request.POST, "TTVBERAT_BADAN"
            ),  # @TTVBERAT_BADAN float  NULL,
            None
            if Globals().input(request.POST, "TTVTINGGI_BADAN") == ""
            else Globals().input(
                request.POST, "TTVTINGGI_BADAN"
            ),  # @TTVTINGGI_BADAN float  NULL,
            None
            if Globals().input(request.POST, "TTVO2") == ""
            else Globals().input(request.POST, "TTVO2"),  # @TTVO2 int  NULL,
            None
            if Globals().input(request.POST, "TTVKESADARAN") == ""
            else Globals().input(
                request.POST, "TTVKESADARAN"
            ),  # @TTVKESADARAN varchar (150) NULL,
            None
            if Globals().input(request.POST, "TTV_LINGKAR_KEPALA") == ""
            else Globals().input(
                request.POST, "TTV_LINGKAR_KEPALA"
            ),  # @TTV_LINGKAR_KEPALA float  NULL,
            None
            if Globals().input(request.POST, "TTV_HPHT") == ""
            else Globals().input(request.POST, "TTV_HPHT"),  # @TTV_HPHT datetime  NULL,
            None
            if Globals().input(request.POST, "TTV_HPL") == ""
            else Globals().input(request.POST, "TTV_HPL"),  # @TTV_HPL datetime  NULL,
            None
            if Globals().input(request.POST, "TTV_LINGKAR_PERUT") == ""
            else Globals().input(
                request.POST, "TTV_LINGKAR_PERUT"
            ),  # @TTV_LINGKAR_PERUT float NULL,
            None
            if Globals().input(request.POST, "TTV_UH") == ""
            else Globals().input(request.POST, "TTV_UH"),  # @TTV_UH float NULL,
            "A",  # @STATUS_AUD nvarchar(5) = 'A'
        ]
        cursor.execute(q, proc_param)
        result_set = Globals().fetchResult(cursor, 3)
        cursor.close()
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
                    qBPJS, [Globals().input(request.POST, "notrans")]
                )
                if len(cekQBridging) > 0:
                    saveFormPcares = ""
                    saveFormPcares = str(saveFormPcare(request))
                    if saveFormPcares == "OK":
                        savePcareKunjungan = ""
                        # try:
                        # savePcareKunjungan=str(views_pcare.bridgingPostRujukanSpesialis(request))
                        savePcareKunjungan = {}
                        savePcareKunjungan = views_pcare.bridgingPostRujukanSpesialis(
                            request
                        )
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
                        # except Exception as e:
                        # 	error=e
                        # 	edit= json.dumps({'success':False,'message':str(error)})

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


def validasiPcare(request):
    edit = {}
    if request.POST["StatusPulang"] == "4":
        if request.POST["opsiRujuk_rbs"] == "1":
            if request.POST["kondisiKhususKategori"] == "":
                edit["success"] = False
                edit["message"] = "Silahkan Pilih Kategori pada kondisi khusus"

                json_data = json.dumps(edit, cls=DjangoJSONEncoder)
                return json_data
            if request.POST["catatanRujukan"] == "":
                edit["success"] = False
                edit["message"] = "Catatan Wajib di isi"

                json_data = json.dumps(edit, cls=DjangoJSONEncoder)
                return json_data

    if request.POST["opsiRujuk_rbs"] == "2":
        if request.POST["spesialisRujukan"] == "":
            edit["success"] = False
            edit["message"] = "Subs Spesialis Wajib di isi"

            json_data = json.dumps(edit, cls=DjangoJSONEncoder)
            return json_data

    if request.POST["tglRujukan"] == "":
        edit["success"] = False
        edit["message"] = "Tgl Rencana Rujukan Wajib di isi"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data

    if request.POST["ppkRujukan"] == "":
        edit["success"] = False
        edit["message"] = "PPK Rujukan Wajib di isi"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data

    if request.POST["noBPJS"] == "":
        edit["success"] = False
        edit["message"] = "Bridging Wajib Menggunakan NO.BPJS!"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data
    if request.POST["CPTD_KELUHANUTAMA"] == "":
        edit["success"] = False
        edit["message"] = "Keluhan harus disi!"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data
    if (
        request.POST["TTV_LINGKAR_PERUT"] == ""
        or request.POST["TTV_LINGKAR_PERUT"] == "0"
    ):
        edit["success"] = False
        edit["message"] = "LingkarPerut harus disi untuk bridging kunjungan pcare!"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data
    if request.POST["TTVTSISTOL"] == "" or request.POST["TTVTSISTOL"] == "0":
        edit["success"] = False
        edit["message"] = "sistole harus disi untuk bridging kunjungan pcare!"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data
    if request.POST["TTVDIASTOL"] == "" or request.POST["TTVDIASTOL"] == "0":
        edit["success"] = False
        edit["message"] = "diastole harus disi untuk bridging kunjungan pcare!"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data

    cursorqDdataPenyakit = connection.cursor()
    qDdataPenyakit = "SELECT * FROM MR_PENYAKIT where MRPNO_TRANSAKSI='{}' AND MR_PENYAKIT.MRPSTAT_DIAG='5' ".format(
        request.POST["notrans"]
    )
    cursorqDdataPenyakit.execute(qDdataPenyakit)
    dataPenyakit = Globals().dictfetchall(cursorqDdataPenyakit)
    if int(len(dataPenyakit)) == 0:
        edit["success"] = False
        edit["message"] = "diagnosa wajib disi"

        json_data = json.dumps(edit, cls=DjangoJSONEncoder)
        return json_data

    edit["success"] = True
    edit["message"] = "Sukses Validasi"
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return json_data


def panggilDisplayNode(request):
    if request.POST["antrianJenis"] == "1":
        data = {
            "NO": request.POST["no_antri"],
            "id_poli": request.POST["id_poli"],
            "KdPoli": request.POST["id_poli"],
            "nama_poli": request.POST["nama_poli"],
            "id_dokter": request.POST["id_dokter"],
            "kode_dokter": request.POST["kode_dokter"],
            "nama_dokter": request.POST["nama_dokter"],
            "Pendaftaran": request.POST["Pendaftaran"],
            "tanggal": request.POST["tanggal"],
            "jam": request.POST["jam"],
            "cabang": request.POST["cabang"],
            "no_antri": request.POST["no_antri"],
            "Channel": request.POST["channel"],
            "antrianJenis": request.POST["antrianJenis"],
        }

        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        url = getattr(env, "URL_SOCKET", "http://localhost:3000") + "/playCS"
        resp = requests.post(
            url, data=json_data, headers={"Content-type": "application/json"}
        )
    elif request.POST["antrianJenis"] == "2":
        data = {
            "NO": request.POST["no_antri"],
            "id_poli": request.POST["id_poli"],
            "KdPoli": request.POST["id_poli"],
            "nama_poli": request.POST["nama_poli"],
            "id_dokter": request.POST["id_dokter"],
            "kode_dokter": request.POST["kode_dokter"],
            "nama_dokter": request.POST["nama_dokter"],
            "Pendaftaran": request.POST["Pendaftaran"],
            "tanggal": request.POST["tanggal"],
            "jam": request.POST["jam"],
            "cabang": request.POST["cabang"],
            "no_antri": request.POST["no_antri"],
            "Channel": request.POST["channel"],
            "antrianJenis": request.POST["antrianJenis"],
        }

        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        url = getattr(env, "URL_SOCKET", "http://localhost:3000") + "/playPOLI"
        resp = requests.post(
            url, data=json_data, headers={"Content-type": "application/json"}
        )

    if resp.status_code == 200:
        # print ('OK!')
        edit = json.dumps({"success": True, "message": "Sukses Panggil"})
    else:
        edit = json.dumps({"success": False, "message": "Gagal Panggil"})
        # print ('Boo!')
    return HttpResponse(edit, content_type="application/json")


def getDetailCPPT(request):
    q = " SELECT CONVERT(varchar,A.CPTDCREATED_AT,113) as TTVUPDATED_ATS,A.*,TTV.*,MK.*,CONVERT(date,TTV.TTV_HPHT) as TTV_HPHTS,CONVERT(date,TTV.TTV_HPL) as TTV_HPLS FROM  EMRRJ_CPPT_DOKTER A "
    q += " LEFT JOIN EMRRJ_TTV TTV ON A.CPTDNO_TRANSAKSI_RJ=TTV.TTVNO_TRANSAKSI_RJ"
    q += " LEFT JOIN MR_KUNJUNGAN_KLINIK_BRIDGING MK ON MK.MRDNO_TRANSAKSI=A.CPTDNO_TRANSAKSI_RJ"
    q += " WHERE A.CPTDNO_TRANSAKSI_RJ='{}'".format(request.GET["NO_TRANSAKSI"])
    cursor = connection.cursor()
    cursor.execute(q)
    result = []
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    edit = json_data
    cursor.close()
    return HttpResponse(edit, content_type="application/json")


def getCPPTPasien(request):
    if request.GET["TGL_AWAL"] == request.GET["TGL_AKHIR"]:
        q = " SELECT TOP 5 KP.KPKD_PASIEN,CONVERT(varchar,KP.KPTGL_PERIKSA,105) TGL_KUNJUNGAN "
    else:
        q = " SELECT KP.KPKD_PASIEN,CONVERT(varchar,KP.KPTGL_PERIKSA,105) TGL_KUNJUNGAN "
    q += " ,KP.KPNO_TRANSAKSI,PL.FMPKLINIKN,PL.FMPKLINIK_ID,DR.FMDDOKTERN,CB.PERUSAHAAN,KP.KPKD_DOKTER"
    q += " ,TTV.*,A.*,CONVERT(date,TTV.TTV_HPHT) as TTV_HPHTS,CONVERT(date,TTV.TTV_HPL) as TTV_HPLS,ISNULL(ED.FHRRESEPTEXT,'-') as RESEP"
    q += " FROM KUNJUNGANPASIEN KP"
    q += " INNER JOIN EMRRJ_CPPT_DOKTER A ON KP.KPNO_TRANSAKSI=A.CPTDNO_TRANSAKSI_RJ"
    q += " LEFT JOIN POLIKLINIK PL ON KP.KPKD_POLY=PL.FMPKLINIK_ID"
    q += " LEFT JOIN DOKTER DR ON KP.KPKD_DOKTER=DR.FMDDOKTER_ID"
    q += " LEFT JOIN CABANG CB ON A.KD_CABANG=CB.CABANG_ID"
    q += " LEFT JOIN EMRRJ_TTV TTV ON A.CPTDNO_TRANSAKSI_RJ=TTV.TTVNO_TRANSAKSI_RJ"
    q += " LEFT JOIN ERESEPDOKTER ED ON KP.KPNO_TRANSAKSI=ED.FHRBUKTI_ID"
    q += " WHERE KP.KPKD_PASIEN='{}' ".format(request.GET["NORM"])
    if request.GET["TGL_AWAL"] != request.GET["TGL_AKHIR"]:
        q += " AND KP.KPTGL_PERIKSA>='{}' AND KP.KPTGL_PERIKSA<='{}'".format(
            request.GET["TGL_AWAL"], request.GET["TGL_AKHIR"]
        )
    q += " ORDER BY KP.KPTGL_PERIKSA DESC"
    cursor = connection.cursor()
    cursor.execute(q)
    result = []
    no = 0
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    edit = json_data
    cursor.close()
    return HttpResponse(edit, content_type="application/json")


def getHPL(request):
    q = "EXEC GET_HITUNG_HPL '%s'" % (request.GET["TTV_HPHT"])
    cursor = connection.cursor()
    cursor.execute(q)
    result = []
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    edit = json_data
    cursor.close()
    return HttpResponse(edit, content_type="application/json")


def getEresepTxT(noTrans):
    pengobatan = " "
    # q1="Select a.FDRRESEP, FDRBRG_ID,FDRBRG_ID2, FDRBRGN, FDRSATUAN,  CAST(FDRQTY AS int) as FDRQTY, CONVERT(varchar(MAX),FDRQTYOUT) as FDRQTYOUT,CONVERT(varchar(MAX),FDRDOSIS) as  FDRDOSIS, FDRSIGNAF,CONVERT(varchar(MAX),FDRDOSIS2) as FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
    # q2=" ISNULL(CASE WHEN a.FDRSTATUS=0 THEN "
    # q2+="' da '"
    # q2+="+(SELECT NAME_BRG FROM BARANG WHERE BARANGC=a.FDRBRG_ID2)+' '"
    # q2+=" ELSE '' END,'') as FDRBRGDA,"
    # q2+=" b.FHRNO_TRANSAKSI, FHRBUKTI_ID, convert(varchar, FHRDATE, 20) as FHRDATE, FHRUSER,convert(varchar, FHRUPDATE, 20) as FHRUPDATE, FHRSTATUS,CONVERT(varchar(MAX),c.HJUAL) as HJUAL,CONVERT(varchar(MAX),(a.FDRQTY*c.Hjual))  As Total "
    # q3=" from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c "
    # q4=" where a.FDRSTATUS2 IS NOT NULL and a.FDRRACIK_ID='NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ORDER BY FDRRESEP".format(noTrans)
    # query="{}{}{}{}".format(q1,q2,q3,q4)
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
    # print(query)
    dataResepNonRacik = Globals().getDataQuery(query, [])
    #  pengobatan+=obj.FDRBRGN+' '+obj.FDRSIGNA+ ' '+obj.FDRBRGDA+' No.'+obj.FDRQTY+' ; ';

    for isidataResepNonRacik in dataResepNonRacik:
        pengobatan += "\n %s %s %s No. %s;" % (
            isidataResepNonRacik["FDRBRGN"],
            isidataResepNonRacik["FDRSIGNA"],
            isidataResepNonRacik["FDRBRGDA"],
            isidataResepNonRacik["FDRQTY"],
        )
    # print(dataResepNonRacik)

    no = 1
    # queryAwal="Select DISTINCT a.FDRRACIK_ID from ERESEPDOKTERD a,ERESEPDOKTER b,Barang c  where a.FDRRACIK_ID<>'NULL' and a.FDRBUKTI_ID=b.FHRNO_TRANSAKSI and A.FDRBRG_ID=c.barangc and b.FHRBUKTI_ID='{}' ".format(noTrans)
    queryAwal = " SELECT DISTINCT a.FDRRACIK_ID"
    queryAwal += " FROM ERESEPDOKTERD AS a"
    queryAwal += " INNER JOIN ERESEPDOKTER AS b ON a.FDRBUKTI_ID = b.FHRNO_TRANSAKSI"
    queryAwal += " INNER JOIN BARANG AS c ON a.FDRBRG_ID = c.BARANGC"
    queryAwal += " WHERE (b.FHRBUKTI_ID = %s) AND (a.FDRRACIK_ID <> 'NULL')"
    dataResepRacikH = Globals().getDataQuery(queryAwal, [noTrans])
    # print(queryAwal)
    if int(len(dataResepRacikH)) > 0:
        pengobatan += "\n #Racikan: "
    for isidataResepRacikH in dataResepRacikH:
        q1 = "Select a.FDRRESEP, FDRBRG_ID, FDRBRGN, FDRSATUAN, FDRQTY, FDRQTYOUT, FDRDOSIS, FDRSIGNAF, FDRDOSIS2, FDRSIGNAS, FDRSIGNAW, FDRSIGNA, FDRBUKTI_ID,"
        q2 = " ISNULL(CASE WHEN a.FDRSTATUS=0 THEN "
        q2 += "' da '"
        q2 += "+(SELECT NAME_BRG FROM BARANG WHERE BARANGC=a.FDRBRG_ID2 and BRANCH=LEFT(b.FHRBUKTI_ID,3))+' '"
        q2 += " ELSE '' END,'') as FDRBRGDA,"
        # if kdCabang=="13":
        # 	q2+=" (SELECT TOP 1 CONVERT(varchar(max),FERDKEBQTY2)+' '+FERRACIKDQTYJENIS FROM ERESEPRACIKD WHERE FERRACIKD_ID='{}' AND FERRACIKDBRG_ID=FDRBRG_ID AND CEILING(FERRACIKDQTY)=FDRQTY) as FDRKEB,".format(isidataResepRacikH['FDRRACIK_ID'])
        # else:
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

            # print(pengobatan)
            # print(int(len(dataResepRacikD)))
            if no == int(len(dataResepRacikD)):
                pengobatan += "\n %s" % (isidataResepRacikD["FDRSIGNA"])
            no += 1

    query = "SELECT ISNULL(FHRRESEPTEXT,'') as FHRRESEPTEXT,FHRNO_TRANSAKSI  FROM ERESEPDOKTER where FHRBUKTI_ID='{}'".format(
        noTrans
    )
    dataResepManual = Globals().getDataQuery(query, [])

    if int(len(pengobatan)) > 5:
        dataResepManual = ""
    pengobatan += "\n"

    for isidataResepManual in dataResepManual:
        pengobatan += "\n %s " % (isidataResepManual["FHRRESEPTEXT"])

    return pengobatan


def printResep(request):
    # Check Session
    if "userauth" in request.session:
        is_login = request.session["userauth"]
    else:
        is_login = False

    # Code
    if is_login:
        response = render(request, "emr/eresep/report.html", {})
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


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
        # print(qKunjunganKlinikBrd)
        # print(inputan)
        qKunjunganKlinikBrd = qKunjunganKlinikBrd % inputan
        Globals().executeQuery(qKunjunganKlinikBrd, [])

    return "OK"


##### CPPT ##########

##### ELAB ##########


def page_elab(request):
    if "userauth" in request.session:
        is_login = request.session["userauth"]
    else:
        is_login = False

    if is_login:
        response = render(request, "emr/elab/home.html", {})
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def page_erad(request):
    if "userauth" in request.session:
        is_login = request.session["userauth"]
    else:
        is_login = False

    if is_login:
        response = render(request, "emr/erad/home.html", {})
        response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
    else:
        return redirect("/login")


def save_elabrad(request):
    edit = {}
    edit["success"] = False
    edit["message"] = "not permited"
    if request.method == "POST":
        edit = {}
        edit["success"] = False
        edit["message"] = "gagal insert"

        q = "exec ADD_LAB_PERMINTAAN  %s,%s, %s, %s, %s, %s, %s, %s , %s"
        # prints(query)
        # cursor.execute(q, [request.POST['FTP_NOTRANSAKSI'],request.POST['FTP_KDPASIEN'],request.POST['FTP_UNIT'],request.POST['FTP_STATUS_CITO'],request.POST['FTP_KDPERIKSA'],request.POST['FAPTGL_APPOITMENTs'],request.POST['FTP_NOTRANSAKSI_LAB'],request.POST['FTP_PARENT'],'A'])
        param = [
            request.POST["FTP_NOTRANSAKSI"],
            request.POST["FTP_KDPASIEN"],
            request.POST["FTP_UNIT"],
            request.POST["FTP_STATUS_CITO"],
            request.POST["FTP_KDPERIKSA"],
            request.POST["FAPTGL_APPOITMENTs"],
            request.POST["FTP_NOTRANSAKSI_LAB"],
            request.POST["FTP_PARENT"],
            "A",
        ]
        result = Globals().getDataSP(q, param, setIndex=2)
        # print(result)
        q = " UPDATE LAB_PERMINTAAN SET FTP_CUSID=%s WHERE FTP_NOTRANSAKSI=%s AND FTP_NOTRANSAKSI_LAB=%s AND KD_CABANG=LEFT(FTP_NOTRANSAKSI,3)"
        Globals().executeQuery(
            q,
            [
                request.POST["FTP_CUSID"],
                request.POST["FTP_NOTRANSAKSI"],
                result[0]["NOTRANSLAB"],
            ],
        )
        edit["success"] = True
        edit["message"] = result[0]["NOTRANSLAB"]
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


def delElabRad(request):
    edit = {}
    cursor = connection.cursor()
    try:
        query = "DELETE LAB_PERMINTAAN WHERE FTP_NOTRANSAKSI='{}' AND FTP_KDPERIKSA='{}' AND FTP_NOTRANSAKSI_LAB='{}'".format(
            request.POST["FTP_NOTRANSAKSI"],
            request.POST["FTP_KDPERIKSA"],
            request.POST["FTP_NOTRANSAKSI_LAB"],
        )
        edit["success"] = True
        edit["message"] = "Method Valid"
        cursor.execute(query)
        query = "Select * from  LAB_PERMINTAAN WHERE FTP_NOTRANSAKSI='{}' AND FTP_KDPERIKSA='{}' AND FTP_NOTRANSAKSI_LAB='{}'".format(
            request.POST["FTP_NOTRANSAKSI"],
            request.POST["FTP_KDPERIKSA"],
            request.POST["FTP_NOTRANSAKSI_LAB"],
        )
        cursor.execute(query)
        rows = cursor.fetchall()
        # prints(rows)
        # return HttpResponse(json_data, content_type="application/json")
        jum = int(len(rows))
        if jum > 0:
            edit["success"] = False
            edit["message"] = "Gagal Hapus"
        else:
            edit["success"] = True
            edit["message"] = "Success Hapus"

    finally:
        cursor.close()
    json_data = json.dumps(edit, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")


##### ELAB ##########


##### RIWAYAT EMR ##########


def getRiwayatPemeriksaanByNORM(request):
    cursor = connection.cursor()
    no_rm = Globals().input(request.GET, "norm")
    # CPPT DOKTER
    q = " SELECT A.CPTDCREATED_AT as created_at_raw,dbo.EMR_GET_USER(A.CPTDUSER_ID) as USER_EMR,A.CPTDNO_TRANSAKSI_RJ as no_transaksi_kj, A.CPTDNO_TRANSAKSI_RJ as no_transaksi, CONVERT(varchar,A.CPTDCREATED_AT,105) as created_at "
    q += " ,convert(varchar, A.CPTDCREATED_AT, 8) as created_at_time,'CPPT_DR' as jenis_trans  "
    q += "  , '-1' as STATUS,'CPPT DOKTER' as pemeriksaan  , A.CPTDCREATED_AT as created_at_raw"
    q += "  from EMRRJ_CPPT_DOKTER  A"
    q += " LEFT JOIN KUNJUNGANPASIEN B ON A.CPTDNO_TRANSAKSI_RJ=B.KPNO_TRANSAKSI   "
    q += " LEFT JOIN PASIEN C ON B.KPKD_PASIEN=C.KD_PASIEN  "
    q += " WHERE B.KPKD_PASIEN = '%s' " % (no_rm)
    # CPPT PERAWAT
    q += " UNION "
    q += " SELECT A.CPTPCREATED_AT as created_at_raw,dbo.EMR_GET_USER(A.CPTPUSER_ID) as USER_EMR,A.CPTPNO_TRANSAKSI_RJ as no_transaksi_kj, A.CPTPNO_TRANSAKSI_RJ as no_transaksi, CONVERT(varchar,A.CPTPCREATED_AT,105) as created_at  "
    q += " ,convert(varchar, A.CPTPCREATED_AT, 8) as created_at_time,'CPPT_PRW' as jenis_trans "
    q += " , '-1' as STATUS,'CPPT PERAWAT' as pemeriksaan  , A.CPTPCREATED_AT as created_at_raw "
    q += " from EMRRJ_CPPT_PERAWAT  A "
    q += " LEFT JOIN KUNJUNGANPASIEN B ON A.CPTPNO_TRANSAKSI_RJ=B.KPNO_TRANSAKSI "
    q += " LEFT JOIN PASIEN C ON B.KPKD_PASIEN=C.KD_PASIEN "
    q += " WHERE B.KPKD_PASIEN = '%s' " % (no_rm)
    q += " ORDER BY 1 DESC  "
    # print(q)
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


def getRiwayatPemeriksaanByNORMDetail(request):
    cursor = connection.cursor()
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
        q += " +'; L.Kepala: '+cast(BBB.TTV_LINGKAR_KEPALA as varchar(max)) "
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
    cursor.execute(q)
    result = Globals().dictfetchall(cursor)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    cursor.close()
    return HttpResponse(json_data, content_type="application/json")


##### RIWAYAT EMR ##########
