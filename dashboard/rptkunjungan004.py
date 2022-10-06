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


def rptkunjungan004(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "rptkunjungan004")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "rptkunjungan004", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "rptkunjungan004", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/printkunjungan004/printkunjungan004.html', {
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

def proses_excel(request):
    tanggal_dr = request.GET['tanggal_dr']
    tanggal_sd = request.GET['tanggal_sd']
    KD_CABANG= request.session['kdCabang']
    q = "select ROW_NUMBER() OVER(ORDER BY SUM(TOTAL) desc) AS NO , KD_PASIEN,NAMAPASIEN,SUM(TOTAL) AS TOTAL from( "
    q += "select f.KD_PASIEN,f.NAMAPASIEN, d.FDTKD_PRODUK as ID_TREATMENT,d.FDTKDPRODUKN as NAMA_TREATMENT, "
    q += "sum(FDTQTY) as QTY, d.FDTHARGA  as HARGA,(sum(FDTQTY)*d.FDTHARGA) as JUMLAH, "
    q += "(sum(FDTQTY)*d.FDTHARGA)-(select sum(dbo.fungsiCalculasiDeposit(FDTHARGA,1,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4))) AS DISCOUNT , "
    q += "(select sum(dbo.fungsiCalculasiDeposit(FDTHARGA,1,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4))) as TOTAL  "
    q += "from TRANSAKSIPASIEN c inner join TRANSAKSIPASIEND d on c.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI   "
    q += "inner join KUNJUNGANPASIEN e on c.FTNO_KUNJUNGAN=e.KPNO_TRANSAKSI  "
    q += "inner join PASIEN f on e.KPKD_PASIEN=f.KD_PASIEN  "
    q += "where (c.FTTGL_TRANSAKSI >= %s and FTTGL_TRANSAKSI<=%s  ) and d.FDTKD_PRODUK <>'ADL002' and (c.KD_CABANG = %s)   "
    q += "group by  f.KD_PASIEN,f.NAMAPASIEN,d.FDTKD_PRODUK,d.FDTKDPRODUKN,d.FDTHARGA  "
    q += "UNION "
    q += "select  f.KD_PASIEN,f.NAMAPASIEN, d.FDFJBRG_ID as ID_TREATMENT,d.FDFJBRGN as NAMA_TREATMENT,sum(FDFJQTY) as QTY,   " 
    q += "d.FDFJHJUAL  as HARGA,(sum(FDFJQTY)*d.FDFJHJUAL) as JUMLAH,(sum(FDFJQTY)*d.FDFJHJUAL)-(select sum(dbo.fungsiCalculasiDeposit(FDFJHJUAL,FDFJQTY,FDFJDISC1,0,0,0,FDFJDISC4))) AS DISCOUNT    "
    q += ",(select sum(dbo.fungsiCalculasiDeposit(FDFJHJUAL,1,FDFJDISC1,0,0,0,FDFJDISC4))) as TOTAL    "
    q += "from FJINKOTA c inner join FJINKOTAD d on c.FHFJBUKTI_ID=d.FDFJBUKTI_ID  "   
    q += "inner join PASIEN f on c.FHFJCUST_ID=f.KD_PASIEN  "
    q += "where (c.FHFJDATE >= %s and FHFJDATE<=%s ) and (c.FHFJBRANCH =%s)   "  
    q += "group by  f.KD_PASIEN,f.NAMAPASIEN,d.FDFJBRG_ID,d.FDFJBRGN,d.FDFJHJUAL "
    q += ") as ZYXorder GROUP BY KD_PASIEN,NAMAPASIEN order by TOTAL desc  "
    result = Globals().getDataQuery(q, [tanggal_dr,tanggal_sd,KD_CABANG,tanggal_dr,tanggal_sd,KD_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getHistoryBeliBarang(request):
    id_pasien = request.GET['id_pasien']
    tanggal_dr = request.GET['tanggal_dr']
    tanggal_sd = request.GET['tanggal_sd']
    KD_CABANG= request.session['kdCabang']
    q = "select ROW_NUMBER() OVER(ORDER BY qty desc) AS NO,* from(select  d.FDTKD_PRODUK as ID_TREATMENT,d.FDTKDPRODUKN as NAMA_TREATMENT,sum(FDTQTY) as QTY, "
    q += "d.FDTHARGA  as HARGA,(sum(FDTQTY)*d.FDTHARGA) as JUMLAH,(sum(FDTQTY)*d.FDTHARGA)-(select sum(dbo.fungsiCalculasiDeposit(FDTHARGA,1,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4))) AS DISCOUNT "
    q += ",(select sum(dbo.fungsiCalculasiDeposit(FDTHARGA,1,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4))) as TOTAL "
    q += "from TRANSAKSIPASIEN c inner join TRANSAKSIPASIEND d on c.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI  "
    q += "inner join KUNJUNGANPASIEN e on c.FTNO_KUNJUNGAN=e.KPNO_TRANSAKSI "
    q += "where e.KPKD_PASIEN= %s and (c.FTTGL_TRANSAKSI >= %s and FTTGL_TRANSAKSI<=%s  ) and (c.KD_CABANG = %s)  "
    q += "group by  d.FDTKD_PRODUK,d.FDTKDPRODUKN,d.FDTHARGA  "
    q += "union select  d.FDFJBRG_ID as ID_TREATMENT,d.FDFJBRGN as NAMA_TREATMENT,sum(FDFJQTY) as QTY,   "
    q += "d.FDFJHJUAL  as HARGA,(sum(FDFJQTY)*d.FDFJHJUAL) as JUMLAH,(sum(FDFJQTY)*d.FDFJHJUAL)-(select sum(dbo.fungsiCalculasiDeposit(FDFJHJUAL,FDFJQTY,FDFJDISC1,0,0,0,FDFJDISC4))) AS DISCOUNT   "
    q += ",(select sum(dbo.fungsiCalculasiDeposit(FDFJHJUAL,1,FDFJDISC1,0,0,0,FDFJDISC4))) as TOTAL   "
    q += "from FJINKOTA c inner join FJINKOTAD d on c.FHFJBUKTI_ID=d.FDFJBUKTI_ID    "
    q += "where c.FHFJCUST_ID= %s and (c.FHFJDATE >= %s and FHFJDATE<=%s  ) and (c.FHFJBRANCH = %s)    "
    q += "group by  d.FDFJBRG_ID,d.FDFJBRGN,d.FDFJHJUAL ) as ZYXorder order by qty desc   "
    result = Globals().getDataQuery(q, [id_pasien,tanggal_dr,tanggal_sd,KD_CABANG,id_pasien,tanggal_dr,tanggal_sd,KD_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
