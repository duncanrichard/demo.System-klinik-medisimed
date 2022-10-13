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


def jasamedis001(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "jasamedis001")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "jasamedis001", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "jasamedis001", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/printjasamedis001/printjasamedis001.html', {
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
    kodemedis_dari = request.GET['kodemedis_dari']
    kodemedis_sampai = request.GET['kodemedis_sampai']
    tanggal_dr = request.GET['tanggal_dr']
    tanggal_sd = request.GET['tanggal_sd']
    pilihan= request.GET['pilihan']
    KD_CABANG= request.session['kdCabang']
    if (pilihan=='1'):
        q = "select  A.FTNO_TRANSAKSI as NO_TRANSAKSI,a.FTNO_KUNJUNGAN as NO_REGISTRASI,a.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN, "
        q += "d.FDTNOMER as NO,d.FDTKD_PRODUK as ID_PRODUK,d.FDTKDPRODUKN as NAMA_PRODUK,FDTQTY as QTY,d.FDTHARGA as HARGA,FDT_DISCKONSUMEN as DISCKONSUMEN,d.FDT_DISC as DISC,d.FDT_DISC2 as DISC2,d.FDT_DISC3 as DISC3,d.FDT_DISC4 as DISC4, "
        q += "d.FD_DISCRESELER as DISCRESELER,d.FD_FEEDOKTER as FEE_MEDIS,d.FDTNO_FAKTUR as NOFAKTUR,d.FDTJENISTRANSAKSI,a.USERRS,a.UPDATERS,a.KD_RESELER,e.NAMA_RESELER,a.FKUNCI,f.FDDKD_DOKTER AS KODE_MEDIS,g.FMDDOKTERN AS NAMA_MEDIS, "
        q += "(SELECT COUNT(*) FROM TRANSAKSIDOKTERD H WHERE H.FDDNO_TRANSAKSI=A.FTNO_TRANSAKSI) AS JUMLAH_MEDIS "
        q += "from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI  "
        q += "inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN   "
        q += "inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI "
        q += "left join RESELER e on a.KD_RESELER=e.KD_RESELER "
        q += "inner join TRANSAKSIDOKTERD f on f.FDDNO_TRANSAKSI=a.FTNO_TRANSAKSI "
        q += "inner join DOKTER g on f.FDDKD_DOKTER=g.FMDDOKTER_ID "
        q += "where (FD_FEEDOKTER<>0 and f.FDDKD_DOKTER>=%s AND f.FDDKD_DOKTER<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
        q += "UNION select  A.FTNO_TRANSAKSI as NO_TRANSAKSI,a.FTNO_KUNJUNGAN as NO_REGISTRASI,a.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN, "
        q += "d.FDTNOMER as NO,d.FDTKD_PRODUK as ID_PRODUK,d.FDTKDPRODUKN as NAMA_PRODUK,FDTQTY as QTY,d.FDTHARGA as HARGA,FDT_DISCKONSUMEN as DISCKONSUMEN,d.FDT_DISC as DISC,d.FDT_DISC2 as DISC2,d.FDT_DISC3 as DISC3,d.FDT_DISC4 as DISC4, "
        q += "d.FD_DISCRESELER as DISCRESELER,d.FD_FEEDOKTER as FEE_MEDIS,d.FDTNO_FAKTUR as NOFAKTUR,d.FDTJENISTRANSAKSI,a.USERRS,a.UPDATERS,a.KD_RESELER,e.NAMA_RESELER,a.FKUNCI,f.FDDKD_DOKTER AS KODE_MEDIS,g.FMPPERAWATN AS NAMA_MEDIS, "
        q += "(SELECT COUNT(*) FROM TRANSAKSIDOKTERD H WHERE H.FDDNO_TRANSAKSI=A.FTNO_TRANSAKSI) AS JUMLAH_MEDIS "
        q += "from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI  "
        q += "inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN   "
        q += "inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI "
        q += "left join RESELER e on a.KD_RESELER=e.KD_RESELER "
        q += "inner join TRANSAKSIDOKTERD f on f.FDDNO_TRANSAKSI=a.FTNO_TRANSAKSI "
        q += "inner join PERAWAT g on f.FDDKD_DOKTER=g.FMPPERAWAT_ID "
        q += "where (FD_FEEDOKTER<>0 and f.FDDKD_DOKTER>=%s AND f.FDDKD_DOKTER<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
        result = Globals().getDataQuery(q, [kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG,kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG])
    elif (pilihan=='2'):
        q = "select  A.FTNO_TRANSAKSI as NO_TRANSAKSI,a.FTNO_KUNJUNGAN as NO_REGISTRASI,a.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN, "
        q += "d.FDTNOMER as NO,d.FDTKD_PRODUK as ID_PRODUK,d.FDTKDPRODUKN as NAMA_PRODUK,FDTQTY as QTY,d.FDTHARGA as HARGA,FDT_DISCKONSUMEN as DISCKONSUMEN,d.FDT_DISC as DISC,d.FDT_DISC2 as DISC2,d.FDT_DISC3 as DISC3,d.FDT_DISC4 as DISC4, "
        q += "d.FD_DISCRESELER as DISCRESELER,d.FD_FEEBC as FEE_MEDIS,d.FDTNO_FAKTUR as NOFAKTUR,d.FDTJENISTRANSAKSI,a.USERRS,a.UPDATERS,a.KD_RESELER,e.NAMA_RESELER,a.FKUNCI,f.FDBC_ID AS KODE_MEDIS,g.FMPPERAWATN AS NAMA_MEDIS, "
        q += "(SELECT COUNT(*) FROM TRANSAKSIBCD H WHERE H.FDBCNO_TRANSAKSI=A.FTNO_TRANSAKSI) AS JUMLAH_MEDIS "
        q += "from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI  "
        q += "inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN   "
        q += "inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI "
        q += "left join RESELER e on a.KD_RESELER=e.KD_RESELER "
        q += "inner join TRANSAKSIBCD f on f.FDBCNO_TRANSAKSI=a.FTNO_TRANSAKSI "
        q += "inner join PERAWAT g on f.FDBC_ID=g.FMPPERAWAT_ID "
        q += "where (FD_FEEBC<>0 and f.FDBC_ID>=%s AND f.FDBC_ID<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
        result = Globals().getDataQuery(q, [kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG])
    else:
        q = "select  A.FTNO_TRANSAKSI as NO_TRANSAKSI,a.FTNO_KUNJUNGAN as NO_REGISTRASI,a.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN, "
        q += "d.FDTNOMER as NO,d.FDTKD_PRODUK as ID_PRODUK,d.FDTKDPRODUKN as NAMA_PRODUK,FDTQTY as QTY,d.FDTHARGA as HARGA,FDT_DISCKONSUMEN as DISCKONSUMEN,d.FDT_DISC as DISC,d.FDT_DISC2 as DISC2,d.FDT_DISC3 as DISC3,d.FDT_DISC4 as DISC4, "
        q += "d.FD_DISCRESELER as DISCRESELER,d.FD_FEEPERAWAT as FEE_MEDIS,d.FDTNO_FAKTUR as NOFAKTUR,d.FDTJENISTRANSAKSI,a.USERRS,a.UPDATERS,a.KD_RESELER,e.NAMA_RESELER,a.FKUNCI,f.FDPKD_PERAWAT AS KODE_MEDIS,g.FMDDOKTERN AS NAMA_MEDIS, "
        q += "(SELECT COUNT(*) FROM TRANSAKSIPERAWATD H WHERE H.FDPNO_TRANSAKSI=A.FTNO_TRANSAKSI) AS JUMLAH_MEDIS "
        q += "from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI  "
        q += "inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN   "
        q += "inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI "
        q += "left join RESELER e on a.KD_RESELER=e.KD_RESELER "
        q += "inner join TRANSAKSIPERAWATD f on f.FDPNO_TRANSAKSI=a.FTNO_TRANSAKSI "
        q += "inner join DOKTER g on f.FDPKD_PERAWAT=g.FMDDOKTER_ID "
        q += "where (FD_FEEPERAWAT<>0 and f.FDPKD_PERAWAT>=%s AND f.FDPKD_PERAWAT<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
        q += "UNION select  A.FTNO_TRANSAKSI as NO_TRANSAKSI,a.FTNO_KUNJUNGAN as NO_REGISTRASI,a.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN, "
        q += "d.FDTNOMER as NO,d.FDTKD_PRODUK as ID_PRODUK,d.FDTKDPRODUKN as NAMA_PRODUK,FDTQTY as QTY,d.FDTHARGA as HARGA,FDT_DISCKONSUMEN as DISCKONSUMEN,d.FDT_DISC as DISC,d.FDT_DISC2 as DISC2,d.FDT_DISC3 as DISC3,d.FDT_DISC4 as DISC4, "
        q += "d.FD_DISCRESELER as DISCRESELER,d.FD_FEEPERAWAT as FEE_MEDIS,d.FDTNO_FAKTUR as NOFAKTUR,d.FDTJENISTRANSAKSI,a.USERRS,a.UPDATERS,a.KD_RESELER,e.NAMA_RESELER,a.FKUNCI,f.FDPKD_PERAWAT AS KODE_MEDIS,g.FMPPERAWATN AS NAMA_MEDIS, "
        q += "(SELECT COUNT(*) FROM TRANSAKSIPERAWATD H WHERE H.FDPNO_TRANSAKSI=A.FTNO_TRANSAKSI) AS JUMLAH_MEDIS "
        q += "from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI  "
        q += "inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN   "
        q += "inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI "
        q += "left join RESELER e on a.KD_RESELER=e.KD_RESELER "
        q += "inner join TRANSAKSIPERAWATD f on f.FDPNO_TRANSAKSI=a.FTNO_TRANSAKSI "
        q += "inner join PERAWAT g on f.FDPKD_PERAWAT=g.FMPPERAWAT_ID "
        q += "where (FD_FEEPERAWAT<>0 and f.FDPKD_PERAWAT>=%s AND f.FDPKD_PERAWAT<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
        result = Globals().getDataQuery(q, [kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG,kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG])


    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def proses_rekap(request):
    kodemedis_dari = request.GET['kodemedis_dari']
    kodemedis_sampai = request.GET['kodemedis_sampai']
    tanggal_dr = request.GET['tanggal_dr']
    tanggal_sd = request.GET['tanggal_sd']
    KD_CABANG= request.session['kdCabang']
    q  ="select SUM(TOTAL) AS TOTAL,KODE_MEDIS,NAMA_MEDIS from ( "
    q +="select  convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,  "
    q +="(dbo.fungsiCalculasifeemedis(FDTHARGA,FDTQTY,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4,FD_FEEDOKTER,(SELECT COUNT(*) FROM TRANSAKSIDOKTERD H WHERE H.FDDNO_TRANSAKSI=A.FTNO_TRANSAKSI)  )) as TOTAL, "
    q +="f.FDDKD_DOKTER AS KODE_MEDIS,g.FMDDOKTERN AS NAMA_MEDIS  "
    q +="from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI   "
    q +="inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN    "
    q +="inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI  "
    q +="left join RESELER e on a.KD_RESELER=e.KD_RESELER  "
    q +="inner join TRANSAKSIDOKTERD f on f.FDDNO_TRANSAKSI=a.FTNO_TRANSAKSI  "
    q +="inner join DOKTER g on f.FDDKD_DOKTER=g.FMDDOKTER_ID  "
    q +="where (FD_FEEDOKTER<>0 and f.FDDKD_DOKTER>=%s AND f.FDDKD_DOKTER<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
    q +="UNION select  convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,  "
    q +="(dbo.fungsiCalculasifeemedis(FDTHARGA,FDTQTY,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4,FD_FEEDOKTER,(SELECT COUNT(*) FROM TRANSAKSIDOKTERD H WHERE H.FDDNO_TRANSAKSI=A.FTNO_TRANSAKSI)  )) as TOTAL, "
    q +="f.FDDKD_DOKTER AS KODE_MEDIS,g.FMPPERAWATN AS NAMA_MEDIS  "
    q +="from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI   "
    q +="inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN    "
    q +="inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI  "
    q +="left join RESELER e on a.KD_RESELER=e.KD_RESELER  "
    q +="inner join TRANSAKSIDOKTERD f on f.FDDNO_TRANSAKSI=a.FTNO_TRANSAKSI  "
    q +="inner join PERAWAT g on f.FDDKD_DOKTER=g.FMPPERAWAT_ID  "
    q +="where (FD_FEEDOKTER<>0 and f.FDDKD_DOKTER>=%s AND f.FDDKD_DOKTER<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
    q +="UNION select  convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,  "
    q +="(dbo.fungsiCalculasifeemedis(FDTHARGA,FDTQTY,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4,FD_FEEPERAWAT,(SELECT COUNT(*) FROM TRANSAKSIPERAWATD H WHERE H.FDPNO_TRANSAKSI=A.FTNO_TRANSAKSI)  )) as TOTAL, "
    q +="f.FDPKD_PERAWAT AS KODE_MEDIS,g.FMDDOKTERN AS NAMA_MEDIS  "
    q +="from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI   "
    q +="inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN    "
    q +="inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI  "
    q +="left join RESELER e on a.KD_RESELER=e.KD_RESELER  "
    q +="inner join TRANSAKSIPERAWATD f on f.FDPNO_TRANSAKSI=a.FTNO_TRANSAKSI  "
    q +="inner join DOKTER g on f.FDPKD_PERAWAT=g.FMDDOKTER_ID  "
    q +="where (FD_FEEPERAWAT<>0 and f.FDPKD_PERAWAT>=%s AND f.FDPKD_PERAWAT<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
    q +="UNION select  convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,  "
    q +="(dbo.fungsiCalculasifeemedis(FDTHARGA,FDTQTY,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4,FD_FEEPERAWAT,(SELECT COUNT(*) FROM TRANSAKSIPERAWATD H WHERE H.FDPNO_TRANSAKSI=A.FTNO_TRANSAKSI)  )) as TOTAL, "
    q +="f.FDPKD_PERAWAT AS KODE_MEDIS,g.FMPPERAWATN AS NAMA_MEDIS  "
    q +="from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI   "
    q +="inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN    "
    q +="inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI  "
    q +="left join RESELER e on a.KD_RESELER=e.KD_RESELER  "
    q +="inner join TRANSAKSIPERAWATD f on f.FDPNO_TRANSAKSI=a.FTNO_TRANSAKSI  "
    q +="inner join PERAWAT g on f.FDPKD_PERAWAT=g.FMPPERAWAT_ID  "
    q +="where (FD_FEEPERAWAT<>0 and f.FDPKD_PERAWAT>=%s AND f.FDPKD_PERAWAT<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
    q +="UNION select  convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,  "
    q +="(dbo.fungsiCalculasifeemedis(FDTHARGA,FDTQTY,FDT_DISCKONSUMEN,FDT_DISC,FDT_DISC2,FDT_DISC3,FDT_DISC4,FD_FEEBC,(SELECT COUNT(*) FROM TRANSAKSIBCD H WHERE H.FDBCNO_TRANSAKSI=A.FTNO_TRANSAKSI)  )) as TOTAL, "
    q +="f.FDBC_ID AS KODE_MEDIS,g.FMPPERAWATN AS NAMA_MEDIS  "
    q +="from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI   "
    q +="inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN    "
    q +="inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI  "
    q +="left join RESELER e on a.KD_RESELER=e.KD_RESELER  "
    q +="inner join TRANSAKSIBCD f on f.FDBCNO_TRANSAKSI=a.FTNO_TRANSAKSI  "
    q +="inner join PERAWAT g on f.FDBC_ID=g.FMPPERAWAT_ID  "
    q +="where (FD_FEEBC<>0 and f.FDBC_ID>=%s AND f.FDBC_ID<=%s and FTTGL_TRANSAKSI>=%s AND FTTGL_TRANSAKSI<=%s AND a.KD_CABANG= %s) "
    q +=") as zxy group by NAMA_MEDIS,KODE_MEDIS order  by KODE_MEDIS,NAMA_MEDIS "
    result = Globals().getDataQuery(q, [kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG,kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG,kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG,kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG,kodemedis_dari,kodemedis_sampai,tanggal_dr,tanggal_sd,KD_CABANG])


    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
