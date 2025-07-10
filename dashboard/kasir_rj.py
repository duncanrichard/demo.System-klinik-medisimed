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


def kasir_rj(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "kasir_rj")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "kasir_rj", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "kasir_rj", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/kasir/base.html', {
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

def getdataProduk(request):
    nama = '%'+request.GET['nama']+'%'
    jenis_tarip = request.GET['jenis_tarip']
    q = ' SELECT top 100 A.FMPPRODUK_ID as ID_PRODUK, FMPKLAS_ID, FMPPRODUKN as NAMA_PRODUK, A.FMPPOSFLAG, FMPUNITPRODUK, FMPUNITKLASPRODUK, FMPJENISTARIP, FMPADMINISTRASI, '
    q +=' FMPJASADOKTER, FMPPOSTMANUAL, FMPHIDDEN, FMPPOSTPAKET, FMPUNITKLASPRODUK2, FMPNOACC, FMPProdukBPjs, '
    q += ' B.FMKKLASN,C.FMKKLAS_ID as kd_induk, C.FMKKLASN AS induk, D.FTGKODE, D.FTGNAMA, E.FTUKODE, '
    q += ' E.FTUNAMA, F.FMNOACCKETERANGAN ,G.FMTTARIF as HJUAL,isnull(G.FMTTGL_BERLAKU,getdate()) AS TGL_BERLAKU,FMTDISC_KONSUMEN,FMTFEE_RESELER, '
    q += " ISNULL((SELECT TOP 1 H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='2' ORDER BY FMTCTGL_BERLAKU DESC) ,0) AS FEE_DOKTER, "
    q += " ISNULL((SELECT TOP 1 H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='5' ORDER BY FMTCTGL_BERLAKU DESC) ,0) AS FEE_BC, "
    q += " ISNULL((SELECT TOP 1 H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='7' ORDER BY FMTCTGL_BERLAKU DESC) ,0) AS FEE_PERAWAT "
    q += ' FROM PRODUK AS A JOIN KLAS_PRODUK AS B ON A.FMPKLAS_ID=B.FMKKLAS_ID AND B.FMKJENISTARIP = %s AND A.FMPJENISTARIP = %s '
    q += ' LEFT JOIN KLAS_PRODUK AS C ON B.PARENT = C.FMKKLAS_ID AND C.FMKJENISTARIP = %s '
    q += ' LEFT JOIN PRODUK_GOLONGAN AS D ON A.FMPUNITKLASPRODUK = D.FTGKODE '
    q += ' LEFT JOIN PRODUK_UNIT AS E ON A.FMPUNITPRODUK = E.FTUKODE '
    q += ' LEFT JOIN PRODUK_NOACC AS F ON A.FMPNOACC = F.FMNOACC '
    q += ' LEFT JOIN TARIF AS G ON A.FMPPRODUK_ID=G.FMTKD_PRODUK AND G.FMTJENISTARIF=A.FMPJENISTARIP '
    q += ' AND FMTTGL_BERLAKU in (SELECT MAX(FMTTGL_BERLAKU) AS TGL_AKHIR FROM TARIF WHERE FMTKD_PRODUK =A.FMPPRODUK_ID AND FMTJENISTARIF =A.FMPJENISTARIP) '
    q += ' WHERE A.FMPPRODUKN like %s ORDER BY A.FMPPRODUKN '
    result = Globals().getDataQuery(q, [jenis_tarip,jenis_tarip,jenis_tarip,nama])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getIdDataProduk(request):
    kode = request.GET['kode']
    jenis_tarip = request.GET['jenis_tarip']
    q = ' SELECT A.FMPPRODUK_ID as ID_PRODUK, FMPKLAS_ID, FMPPRODUKN as NAMA_PRODUK, A.FMPPOSFLAG, FMPUNITPRODUK, FMPUNITKLASPRODUK, FMPJENISTARIP, FMPADMINISTRASI, '
    q +=' FMPJASADOKTER, FMPPOSTMANUAL, FMPHIDDEN, FMPPOSTPAKET, FMPUNITKLASPRODUK2, FMPNOACC, FMPProdukBPjs, '
    q += ' B.FMKKLASN,C.FMKKLAS_ID as kd_induk, C.FMKKLASN AS induk, D.FTGKODE, D.FTGNAMA, E.FTUKODE, '
    q += ' E.FTUNAMA, F.FMNOACCKETERANGAN ,G.FMTTARIF as HJUAL,isnull(G.FMTTGL_BERLAKU,getdate()) AS TGL_BERLAKU,FMTDISC_KONSUMEN,FMTFEE_RESELER, '
    q += " ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='2') ,0) AS FEE_DOKTER, "
    q += " ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='5') ,0) AS FEE_BC, "
    q += " ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='7') ,0) AS FEE_PERAWAT "
    q += ' FROM PRODUK AS A JOIN KLAS_PRODUK AS B ON A.FMPKLAS_ID=B.FMKKLAS_ID AND B.FMKJENISTARIP = %s AND A.FMPJENISTARIP = %s '
    q += ' LEFT JOIN KLAS_PRODUK AS C ON B.PARENT = C.FMKKLAS_ID AND C.FMKJENISTARIP = %s '
    q += ' LEFT JOIN PRODUK_GOLONGAN AS D ON A.FMPUNITKLASPRODUK = D.FTGKODE '
    q += ' LEFT JOIN PRODUK_UNIT AS E ON A.FMPUNITPRODUK = E.FTUKODE '
    q += ' LEFT JOIN PRODUK_NOACC AS F ON A.FMPNOACC = F.FMNOACC '
    q += ' LEFT JOIN TARIF AS G ON A.FMPPRODUK_ID=G.FMTKD_PRODUK AND G.FMTJENISTARIF=A.FMPJENISTARIP '
    q += ' AND FMTTGL_BERLAKU in (SELECT MAX(FMTTGL_BERLAKU) AS TGL_AKHIR FROM TARIF WHERE FMTKD_PRODUK =A.FMPPRODUK_ID AND FMTJENISTARIF =A.FMPJENISTARIP) '
    q += ' WHERE A.FMPPRODUK_ID = %s ORDER BY A.FMPPRODUKN '
    result = Globals().getDataQuery(q, [jenis_tarip,jenis_tarip,jenis_tarip,kode])
    if len(result)==0:
        data={
            'status':'gagal',
            'pesen':'data tidak ditemukan',
            'data':None
        }
    else:
        data={
            'status':'ok',
            'pesen':'data ditemukan',
            'data':result[0]
        }
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDiscCustomer(request):
    cabang_id = request.session['kdCabang']
    tgl_berlaku = request.GET['tgl_berlaku']
    kode_produk = request.GET['kode_produk']
    
    q = 'SELECT PRODUK_ID, CABANG_ID, DISC1, DISC2, DISC3, DISC4, TGL_BERLAKU, TGL_BERAKHIR, FKUNCI, [USER], [UPDATE]  '
    q += 'FROM  DISCCUSTOMER a  inner join PRODUK b on a.PRODUK_ID=b.FMPPRODUK_ID  '
    q += ' where a.FKUNCI=1 and CABANG_ID= %s and TGL_BERLAKU= %s and TGL_BERAKHIR= %s and PRODUK_ID= %s   order by PRODUK_ID '
    result = Globals().getDataQuery(q,[cabang_id,tgl_berlaku,tgl_berlaku,kode_produk])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getdokter(request):
    cabang_id = request.session['kdCabang']
    q ="select ROW_NUMBER() OVER (ORDER BY NAMA_DOKTER) AS NO, nakes.* from (SELECT a.FMDDOKTER_ID AS ID_DOKTER,FMDDOKTERN AS NAMA_DOKTER from  DOKTER a where  KD_CABANG=%s and a.FMDSTATUS='0'  "
    q +="UNION select a.FMPPERAWAT_ID AS ID_DOKTER,A.FMPPERAWATN AS NAMA_DOKTER from  PERAWAT a where  KD_CABANG=%s and a.FMPSTATUS='0') as nakes "
    result = Globals().getDataQuery(q,[cabang_id,cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getperawat(request):
    cabang_id = request.session['kdCabang']
    q = " select ROW_NUMBER() OVER (ORDER BY ID_PERAWAT) AS NO, nakes.* from (select a.FMPPERAWAT_ID AS ID_PERAWAT,a.FMPPERAWATN AS NAMA_PERAWAT  "
    q += " from  PERAWAT a where  KD_CABANG=%s and a.FMPSTATUS='0'  "
    q += " union SELECT a.FMDDOKTER_ID AS ID_PERAWAT,FMDDOKTERN AS NAMA_PERAWAT  "
    q += " from  DOKTER a where  KD_CABANG=%s and a.FMDSTATUS='0' ) as nakes order by NAMA_PERAWAT "
    result = Globals().getDataQuery(q,[cabang_id,cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getBC(request):
    cabang_id = request.session['kdCabang']
    q = "select ROW_NUMBER() OVER (ORDER BY FMPPERAWATN) AS NO, a.FMPPERAWAT_ID AS ID_BC,A.FMPPERAWATN AS NAMA_BC from  PERAWAT a where  KD_CABANG=%s and a.FMPSTATUS='0' order by FMPPERAWATN "
    result = Globals().getDataQuery(q,[cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getIdDokterProduk(request):
    id_produk = request.GET['id_produk']
    jenis_tarip = request.GET['jenis_tarip']
    komponent = request.GET['komponent']
    q = " select a.FMTCKD_PRODUK, a.FMTCKD_COMPONENT,b.COMPONENT,a.FMTCTARIF,a.FMTCTARIFPROSEN from TARIF_KOMPONENT a inner join PRODUK_COMPONENT b on a.FMTCKD_COMPONENT=b.KD_COMPONENT "
    q +=" where a.FMTCKD_PRODUK= %s and a.FMTCJENISTARIF= %s and b.JASAKOMPONENT= %s  "
    q += ' AND a.FMTCTGL_BERLAKU in (SELECT MAX(FMTTGL_BERLAKU) AS TGL_AKHIR FROM TARIF c WHERE FMTKD_PRODUK =A.FMTCKD_PRODUK AND c.FMTJENISTARIF =A.FMTCJENISTARIF) '
    result = Globals().getDataQuery(q, [id_produk,jenis_tarip,komponent])
    if len(result)==0:
        data={
            'status':'gagal',
            'pesen':'data tidak ditemukan',
            'data':None
        }
    else:
        data={
            'status':'ok',
            'pesen':'data ditemukan',
            'data':result[0]
        }
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def SP_AUD_TRANSAKSI(request):
    # DETAIL
    FD_NO = json.loads(request.POST['FD_NO'])
    FD_ID_PRODUK = json.loads(request.POST['FD_ID_PRODUK'])
    FD_NAMA_PRODUK = json.loads(request.POST['FD_NAMA_PRODUK'])
    FD_HARGA = json.loads(request.POST['FD_HARGA'])
    FD_QTY = json.loads(request.POST['FD_QTY'])
    FD_DISC = json.loads(request.POST['FD_DISC'])
    FD_DISC2 = json.loads(request.POST['FD_DISC2'])
    FD_DISC3 = json.loads(request.POST['FD_DISC3'])
    FD_DISC4 = json.loads(request.POST['FD_DISC4'])
    FD_DISCKONSUMEN = json.loads(request.POST['FD_DISCKONSUMEN'])
    FD_DISCRESELER = json.loads(request.POST['FD_DISCRESELER'])
    FD_FEEDOKTER = json.loads(request.POST['FD_FEEDOKTER'])
    FD_FEEBC = json.loads(request.POST['FD_FEEBC'])
    FD_FEEPERAWAT = json.loads(request.POST['FD_FEEPERAWAT'])
    FD_BUKTI_ID = json.loads(request.POST['FD_BUKTI_ID'])
    

    FHD_NO = json.loads(request.POST['FHD_NO'])
    FHD_ID_DOKTER = json.loads(request.POST['FHD_ID_DOKTER'])
    FHD_NAMA_DOKTER = json.loads(request.POST['FHD_NAMA_DOKTER'])

    FHB_NO = json.loads(request.POST['FHB_NO'])
    FHB_ID_BC = json.loads(request.POST['FHB_ID_BC'])
    FHB_NAMA_BC = json.loads(request.POST['FHB_NAMA_BC'])

    FHP_NO = json.loads(request.POST['FHP_NO'])
    FHP_ID_PERAWAT = json.loads(request.POST['FHP_ID_PERAWAT'])
    FHP_NAMA_PERAWAT = json.loads(request.POST['FHP_NAMA_PERAWAT'])

    FBY_NO = json.loads(request.POST['FBY_NO'])
    FBY_NOFAKTUR = json.loads(request.POST['FBY_NOFAKTUR'])
    FBY_TUNAI = json.loads(request.POST['FBY_TUNAI'])

    # header
    FH_BUKTI_ID = request.POST['FH_BUKTI_ID']
    FH_REGISTER_ID = request.POST['FH_REGISTER_ID']
    FH_DATE = request.POST['FH_DATE']
    FH_PASIEN_ID = request.POST['FH_PASIEN_ID']
    FH_RESELER_ID = request.POST['FH_RESELER_ID']
    FH_PAKET_ID = request.POST['FH_PAKET_ID']
    USERRS = request.session['user_id']
    KD_CABANG= request.session['kdCabang']
    FH_NOTA= request.POST['FH_NOTA']
    status_aud = request.POST['StatusAUD']

    q = "SET NOCOUNT ON;"
    q += "DECLARE @LIST_TRANSAKSI TRANSAKSID;"
    q += "DECLARE @LIST_DOKTER LIST_DOKTER;"
    q += "DECLARE @LIST_BC LIST_BC;"
    q += "DECLARE @LIST_PERAWAT LIST_PERAWAT;"
    q += "DECLARE @LIST_BAYAR MASTERCOMPONENT;"
    q += "DECLARE @NOW datetime; "
    q += "SET @NOW = GETDATE(); "

    proc_param = []
    i = 0
    for x in FD_NO:
        q += "INSERT INTO @LIST_TRANSAKSI (NO, ID_PODUK, NAMA_PRODUK, HARGA, QTY, DISC, DISC2, DISC3, DISC4, DISCKONSUMEN, DISCRESELER, FEEDOKTER, FEEBC, FEEPERAWAT, BUKTI_ID) "
        q += "VALUES ("
        q += FD_NO[i] + ","
        q += "'" + FD_ID_PRODUK[i] + "',"
        q += "'" + FD_NAMA_PRODUK[i] + "',"
        q += FD_HARGA[i] + ","
        q += FD_QTY[i] + ","
        q += FD_DISC[i] + ","
        q += FD_DISC2[i] + ","
        q += FD_DISC3[i] + ","
        q += FD_DISC4[i] + ","
        q += FD_DISCKONSUMEN[i] + ","
        q += FD_DISCRESELER[i] + ","
        q += FD_FEEDOKTER[i] + ","
        q += FD_FEEBC[i] + ","
        q += FD_FEEPERAWAT[i] + ","
        q += "'" + FD_BUKTI_ID[i] + "');"
        i += 1

    i = 0
    for x in FHD_NO:
        q += "INSERT INTO @LIST_DOKTER (NO, ID_DOKTER, NAMA_DOKTER,BUKTI_ID) "
        q += "VALUES ("
        q += FHD_NO[i] + ","
        q += "'" + FHD_ID_DOKTER[i] + "',"
        q += "'" + FHD_NAMA_DOKTER[i] + "',"
        q += "'" + FH_BUKTI_ID + "');"
        i += 1

  
    i = 0
    for x in FHB_NO:
        q += "INSERT INTO @LIST_BC (NO, ID_BC, NAMA_BC, BUKTI_ID) "
        q += "VALUES ("
        q += FHB_NO[i] + ","
        q += "'" + FHB_ID_BC[i] + "',"
        q += "'" + FHB_NAMA_BC[i] + "',"
        q += "'" + FH_BUKTI_ID + "');"
        i += 1

    i = 0
    for x in FHP_NO:
        q += "INSERT INTO @LIST_PERAWAT (NO, ID_PERAWAT, NAMA_PERAWAT, BUKTI_ID) "
        q += "VALUES ("
        q += FHP_NO[i] + ","
        q += "'" + FHP_ID_PERAWAT[i] + "',"
        q += "'" + FHP_NAMA_PERAWAT[i] + "',"
        q += "'" + FH_BUKTI_ID + "');"
        i += 1

    i = 0
    for x in FBY_NO:
        q += "INSERT INTO @LIST_BAYAR (FCDKD_COMPONENT, COMPONENT, FCDTARIF) "
        q += "VALUES ("
        q += FBY_NO[i] + ","
        q += "'" + FBY_NOFAKTUR[i] + "',"
        q +=  FBY_TUNAI[i] + ");"
        i += 1

    q += "EXEC IMD_AUD_TRANSAKSI "
    q += "'" + FH_BUKTI_ID + "',"
    q += "'" + FH_REGISTER_ID + "',"
    q += "'" + FH_DATE + "',"
    q += "'" + FH_PASIEN_ID + "',"
    q += "'" + FH_RESELER_ID + "',"
    q += "'" + FH_PAKET_ID + "',"
    q += "'" + USERRS + "',"
    q += "'" + KD_CABANG + "',"
    q += "'" + FH_NOTA + "',"
    q += "'" + status_aud + "', "
    q += "@LIST_TRANSAKSI,"
    q += "@LIST_DOKTER,"
    q += "@LIST_BC,"
    q += "@LIST_PERAWAT,"
    q += "@LIST_BAYAR"

    if (status_aud=='D') :
        user = {
        'user_id': request.session['user_id'],
        'user_name': request.session['user_name'],
        'user_priv': request.session['user_priv'],
        }
        data = []
        data.append({"query": "select * from TRANSAKSIPASIEN where FTNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        data.append({"query": "select * from TRANSAKSIPASIEND where FDTNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        data.append({"query": "select * from TRANSAKSIBAYARD where FTBNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        
        Globals().create_log('Hapus LogDelete.txt', 'IMMODERMA', data, user)
    try:
        result = Globals().getDataSP(q)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)

def getTransaksi(request):
    no_bukti = '%'+request.GET['no_bukti']+'%'
    no_nota = '%'+request.GET['no_nota']+'%'
    pasien = '%'+request.GET['pasien']+'%'
    nama_pasien = '%'+request.GET['nama_pasien']+'%'
    tipe = request.GET['tipe']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")
    KD_CABANG= request.session['kdCabang']

    if(tipe == 'mutasi_by_bulan'):
        q = "select  top 100 A.FTNO_TRANSAKSI,A.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN  "
        q +="from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI "
        q +="inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN  "
        q +="where (FTNO_TRANSAKSI like %s) and (isnull(FTNO_NOTA,'') like %s) and (KPKD_PASIEN like %s) and "
        q += "(NAMAPASIEN like %s) and (YEAR(FTTGL_TRANSAKSI) = %s) and (MONTH(FTTGL_TRANSAKSI) = %s) and a.KD_CABANG= %s order by FTNO_TRANSAKSI"
        result = Globals().getDataQuery(q, [no_bukti,no_nota, pasien, nama_pasien, tanggal.year, tanggal.month,KD_CABANG])
    else:
        q = "select  top 100 A.FTNO_TRANSAKSI,A.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN  "
        q +="from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI "
        q +="inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN  "
        q +="where (FTNO_TRANSAKSI like %s) and (isnull(FTNO_NOTA,'') like %s) and (KPKD_PASIEN like %s) and "
        q += "(NAMAPASIEN like %s) and (FTTGL_TRANSAKSI = %s AND a.KD_CABANG= %s )  order by FTNO_TRANSAKSI"
        result = Globals().getDataQuery(q, [no_bukti,no_nota, pasien, nama_pasien, tanggal,KD_CABANG])

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getTransaksiByBukti(request):
    no_bukti = request.GET['no_bukti']
    KD_CABANG= request.session['kdCabang']

    q = "select  A.FTNO_TRANSAKSI,a.FTNO_KUNJUNGAN,A.FTNO_NOTA, convert(varchar, a.FTTGL_TRANSAKSI, 23) as TANGGAL,B.KPKD_PASIEN,c.NAMAPASIEN,FTNO_DEPOSIT, "
    q += "d.FDTNOMER as NO,d.FDTKD_PRODUK as ID_PRODUK,d.FDTKDPRODUKN as NAMA_PRODUK,FDTQTY as QTY,d.FDTHARGA as HARGA,FDT_DISCKONSUMEN as DISCKONSUMEN,d.FDT_DISC as DISC,d.FDT_DISC2 as DISC2,d.FDT_DISC3 as DISC3,d.FDT_DISC4 as DISC4, "
    q += "d.FD_DISCRESELER as DISCRESELER,d.FD_FEEDOKTER as FEEDOKTER,d.FD_FEEBC as FEEBC,d.FD_FEEPERAWAT as FEEPERAWAT,d.FDTNO_FAKTUR as NOFAKTUR,d.FDTJENISTRANSAKSI,a.USERRS,a.UPDATERS,a.KD_RESELER,e.NAMA_RESELER,a.FKUNCI "
    q += "from TRANSAKSIPASIEN a inner join KUNJUNGANPASIEN b ON A.FTNO_KUNJUNGAN=B.KPNO_TRANSAKSI  "
    q += "inner join PASIEN c on b.KPKD_PASIEN=c.KD_PASIEN   "
    q += "inner join TRANSAKSIPASIEND d on a.FTNO_TRANSAKSI=d.FDTNO_TRANSAKSI "
    q += "left join RESELER e on a.KD_RESELER=e.KD_RESELER "
    q += "where (FTNO_TRANSAKSI=%s AND a.KD_CABANG= %s) "
    result = Globals().getDataQuery(q, [no_bukti,KD_CABANG])

    q = "Select ROW_NUMBER() OVER (ORDER BY NAMA_DOKTER) AS NO,* from (SELECT a.FMDDOKTER_ID AS ID_DOKTER,FMDDOKTERN AS NAMA_DOKTER "
    q += "from  DOKTER a inner join TRANSAKSIDOKTERD b on a.FMDDOKTER_ID=b.FDDKD_DOKTER "
    q += "where FDDNO_TRANSAKSI=%s and KD_CABANG=%s and a.FMDSTATUS='0' union "
    q += "select a.FMPPERAWAT_ID AS ID_DOKTER,FMPPERAWATN AS NAMA_DOKTER "
    q += "from  PERAWAT a inner join TRANSAKSIDOKTERD b on a.FMPPERAWAT_ID=b.FDDKD_DOKTER "
    q += "where FDDNO_TRANSAKSI=%s and KD_CABANG=%s and a.FMPSTATUS='0') as ZYX  "
    q += "order by NAMA_DOKTER "
    result2 = Globals().getDataQuery(q, [no_bukti,KD_CABANG,no_bukti,KD_CABANG])

    q = "select ROW_NUMBER() OVER (ORDER BY FMPPERAWATN) AS NO, a.FMPPERAWAT_ID AS ID_BC ,A.FMPPERAWATN AS NAMA_BC  "
    q += "from  PERAWAT a inner join TRANSAKSIBCD b on a.FMPPERAWAT_ID=b.FDBC_ID "
    q += "where  FDBCNO_TRANSAKSI=%s and KD_CABANG=%s and a.FMPSTATUS='0' order by FMPPERAWATN "
    result3 = Globals().getDataQuery(q, [no_bukti,KD_CABANG])

    q = "select ROW_NUMBER() OVER (ORDER BY NAMA_PERAWAT) AS NO,* from (Select a.FMDDOKTER_ID AS ID_PERAWAT,A.FMDDOKTERN AS NAMA_PERAWAT   "
    q += "from  DOKTER a inner join TRANSAKSIPERAWATD b on a.FMDDOKTER_ID=b.FDPKD_PERAWAT "
    q += "where b.FDPNO_TRANSAKSI=%s and  KD_CABANG=%s and a.FMDSTATUS='0' union "
    q += "select a.FMPPERAWAT_ID AS ID_PERAWAT,A.FMPPERAWATN AS NAMA_PERAWAT   "
    q += "from  PERAWAT a inner join TRANSAKSIPERAWATD b on a.FMPPERAWAT_ID=b.FDPKD_PERAWAT "
    q += "where b.FDPNO_TRANSAKSI=%s and  KD_CABANG=%s and a.FMPSTATUS='0') as ZYX "
    q += "order by NAMA_PERAWAT  "
    result4 = Globals().getDataQuery(q, [no_bukti,KD_CABANG,no_bukti,KD_CABANG])

    q = "select ROW_NUMBER() OVER (ORDER BY FTBNO_TRANSAKSI) AS NO,FTBNO_TRANSAKSI as NO_TRANSAKSI, FTBTGL_TRANSAKSI, FTBTUNAI as TUNAI, isnull(FTBPIUTANG,0) as PIUTANG, isnull(FTBJAMINPERUSAHAAN,0) as JAMINAN, USERRS, UPDATERS, FTBNAMAPEMBAYAR, FTBJUMLAH_UANG, FTBKEMBALIAN_UANG, isnull(FTBNO_FAKTUR,'') as NOFAKTUR,   "
    q += "FTBTGL_FAKTUR, FTBNILAI_FAKTUR, FTBNOKARTU01, FTBNOKARTU02, FTBNOKARTU03, FTBNOKARTU04, FTBDEBITKREDIT01, FTBDEBITKREDIT02, FTBDEBITKREDIT03, FTBDEBITKREDIT04, FTBNILAIBANK01,  "
    q += "FTBNILAIBANK02, FTBNILAIBANK03, FTBNILAIBANK04, FTBBANK01, FTBBANK02, FTBBANK03, FTBBANK04, NO_VOUCHER01, NO_VOUCHER02, NO_VOUCHER03, NO_VOUCHER04, NILAI_VOUCHER01, NILAI_VOUCHER02,  "
    q += "NILAI_VOUCHER03, NILAI_VOUCHER04, "
    q += "(ISNULL(FTBNILAIBANK01,0)+ISNULL(FTBNILAIBANK02,0)+ISNULL(FTBNILAIBANK03,0)+ISNULL(FTBNILAIBANK04,0)) as BANK, "
    q += "(ISNULL(NILAI_VOUCHER01,0)+ISNULL(NILAI_VOUCHER02,0)+ISNULL(NILAI_VOUCHER03,0)+ISNULL(NILAI_VOUCHER04,0)) as VOUCHER "
    q += "FROM TRANSAKSIBAYARD a where  a.FTBNO_TRANSAKSI=%s "
    result5 = Globals().getDataQuery(q, [no_bukti])

    json_data = json.dumps({
		'data1':result,'data2':result2,'data3':result3,'data4':result4,'data5':result5
	}, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def cetakBilling(request):
	nomor = request.GET['no_bukti']
	terbilang= request.GET['terbilang']
	tanggal_waktu_cetak = datetime.now().strftime('%Y-%m-%d')
	jam = str(datetime.now().strftime('%H:%M:%S'))
	user = request.session['user_priv']
	# pilihcetak=request.GET['pilihcetak']
	pdf_file = Globals().generateReportDB(
		"Billingkasir.jrxml", 
		'Billingkasir', 
		user,
		{
			'nomor': nomor,
			'nama_rs': request.session['nama_cabang'],
			'tanggal_waktu_cetak': Globals().tanggalIndo(tanggal_waktu_cetak),
			'terbilang': terbilang,
			'user': user,

		} ,
		# list_format=[pilihcetak]
	)
	json_data = json.dumps(pdf_file, cls=DjangoJSONEncoder)
	return HttpResponse(json_data, content_type="application/json")

def getTpay(request):
    kode = request.GET['kode']
    tipe = request.GET['tipe']
    if(tipe == 'tpay'):
        q = "SELECT tpay_id AS KODE, nama AS NAMA, KREDIT FROM TPAY WHERE tpay_id= %s ORDER BY tpay_id "
        result = Globals().getDataQuery(q,[kode])
    else:
        q = "SELECT tpay_id AS KODE, nama AS NAMA, KREDIT FROM TPAY ORDER BY tpay_id "
        result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getVoucherPay(request):
    # novoucher = request.GET['novoucher']
    tipe = request.GET['tipe']
    if(tipe == 'idvoucher'):
        q = " SELECT  NO_VOUCHER, TGL_TRANSAKSI, NILAI_VOUCHER, STATUS_VOUCHER, NORM_VOUCHER, EXPR_VOUCHER, GROUP_VOUCHER FROM  VOUCHER_PASIEN a "
        q += " WHERE a.NO_VOUCHER = %s and STATUS_VOUCHER = 0 "
        q += " ORDER BY a.NO_VOUCHER "
        
        result = Globals().getDataQuery(q,)
    else :
        q = " SELECT  NO_VOUCHER, TGL_TRANSAKSI, NILAI_VOUCHER, STATUS_VOUCHER, NORM_VOUCHER, EXPR_VOUCHER, GROUP_VOUCHER FROM  VOUCHER_PASIEN  a "
        q += " WHERE STATUS_VOUCHER = 0 "
        q += " ORDER BY a.NO_VOUCHER "
        
        result = Globals().getDataQuery(q)

    json_data = json.dumps(result,cls=DjangoJSONEncoder)
    edit=json_data
    return HttpResponse(edit, content_type="application/json")

def SP_AUD_BAYAR_TRANSAKSI(request):
    FH_BUKTI_ID = request.POST['FH_BUKTI_ID']
    FH_NAMA_PEMBAYAR = request.POST['FH_NAMA_PEMBAYAR']
    FH_DATE = request.POST['FH_DATE']
    FH_DATE_PIUTANG = request.POST['FH_DATE_PIUTANG']
    FH_TUNAI = request.POST['FH_TUNAI']
    FH_TUNAI_PHISIK = request.POST['FH_TUNAI_PHISIK']
    FH_TOTAL_BANK1 = request.POST['FH_TOTAL_BANK1']
    FH_TOTAL_BANK2 = request.POST['FH_TOTAL_BANK2']
    FH_TOTAL_BANK3 = request.POST['FH_TOTAL_BANK3']
    FH_TOTAL_BANK4 = request.POST['FH_TOTAL_BANK4']
    FH_ID_EDC1 = request.POST['FH_ID_EDC1']
    FH_ID_EDC2 = request.POST['FH_ID_EDC2']
    FH_ID_EDC3 = request.POST['FH_ID_EDC3']
    FH_ID_EDC4 = request.POST['FH_ID_EDC4']
    FH_NO_KARTU1 = request.POST['FH_NO_KARTU1']
    FH_NO_KARTU2 = request.POST['FH_NO_KARTU2']
    FH_NO_KARTU3 = request.POST['FH_NO_KARTU3']
    FH_NO_KARTU4 = request.POST['FH_NO_KARTU4']
    FH_JENIS_KARTU1 = request.POST['FH_JENIS_KARTU1']
    FH_JENIS_KARTU2 = request.POST['FH_JENIS_KARTU2']
    FH_JENIS_KARTU3 = request.POST['FH_JENIS_KARTU3']
    FH_JENIS_KARTU4 = request.POST['FH_JENIS_KARTU4']
    FH_TOTAL_VOUCHER1 = request.POST['FH_TOTAL_VOUCHER1']
    FH_TOTAL_VOUCHER2 = request.POST['FH_TOTAL_VOUCHER2']
    FH_TOTAL_VOUCHER3 = request.POST['FH_TOTAL_VOUCHER3']
    FH_TOTAL_VOUCHER4 = request.POST['FH_TOTAL_VOUCHER4']
    FH_NO_VOUCHER1 = request.POST['FH_NO_VOUCHER1']
    FH_NO_VOUCHER2 = request.POST['FH_NO_VOUCHER2']
    FH_NO_VOUCHER3 = request.POST['FH_NO_VOUCHER3']
    FH_NO_VOUCHER4 = request.POST['FH_NO_VOUCHER4']
    FH_TOTAL_DIJAMIN = request.POST['FH_TOTAL_DIJAMIN']
    FH_TOTAL_PIUTANG = request.POST['FH_TOTAL_PIUTANG']
    USERRS = request.session['user_id']
    status_aud = request.POST['StatusAUD']

    q = "SET NOCOUNT ON;"
    q += "EXEC IMD_AUD_PEMBAYARAN_KASIR "
    q += "'" + FH_BUKTI_ID + "',"
    q += " %s,"
    q += "'" + FH_DATE + "',"
    q += "'" + FH_DATE_PIUTANG + "',"
    q += "'" + FH_TUNAI + "',"
    q += "'" + FH_TUNAI_PHISIK + "',"
    q += "'" + FH_TOTAL_BANK1 + "',"
    q += "'" + FH_TOTAL_BANK2 + "',"
    q += "'" + FH_TOTAL_BANK3 + "',"
    q += "'" + FH_TOTAL_BANK4 + "',"
    q += "'" + FH_ID_EDC1 + "',"
    q += "'" + FH_ID_EDC2 + "',"
    q += "'" + FH_ID_EDC3 + "',"
    q += "'" + FH_ID_EDC4 + "',"
    q += "'" + FH_NO_KARTU1 + "',"
    q += "'" + FH_NO_KARTU2 + "',"
    q += "'" + FH_NO_KARTU3 + "',"
    q += "'" + FH_NO_KARTU4 + "',"
    q += "'" + FH_JENIS_KARTU1 + "',"
    q += "'" + FH_JENIS_KARTU2 + "',"
    q += "'" + FH_JENIS_KARTU3 + "',"
    q += "'" + FH_JENIS_KARTU4 + "',"
    q += "'" + FH_TOTAL_VOUCHER1 + "',"
    q += "'" + FH_TOTAL_VOUCHER2 + "',"
    q += "'" + FH_TOTAL_VOUCHER3 + "',"
    q += "'" + FH_TOTAL_VOUCHER4 + "',"
    q += "'" + FH_NO_VOUCHER1 + "',"
    q += "'" + FH_NO_VOUCHER2 + "',"
    q += "'" + FH_NO_VOUCHER3 + "',"
    q += "'" + FH_NO_VOUCHER4 + "',"
    q += "'" + FH_TOTAL_DIJAMIN + "',"
    q += "'" + FH_TOTAL_PIUTANG + "',"
    q += "'" + USERRS + "',"
    q += "'" + status_aud + "' "

    if (status_aud=='D') :
        user = {
        'user_id': request.session['user_id'],
        'user_name': request.session['user_name'],
        'user_priv': request.session['user_priv'],
        }
        data = []
        data.append({"query": "select * from TRANSAKSIPASIEN where FTNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        data.append({"query": "select * from TRANSAKSIPASIEND where FDTNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        data.append({"query": "select * from TRANSAKSIBAYARD where FTBNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        
        Globals().create_log('Hapus LogDelete.txt', 'IMMODERMA', data, user)
    try:
        result = Globals().getDataSP(q,[FH_NAMA_PEMBAYAR])
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)

def findDepositPaket(request):
    kd_pasien = request.GET['kd_pasien']
    KD_CABANG= request.session['kdCabang']
    jenis_deposit = Globals().input(request.GET, 'jenis_deposit',0)
    q ="""
        select    
        distinct  A.FDPNO_DEPOSIT, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,FDPNOMINAL,isnull(FDPNOMINAL_SISA,0) as FDPNOMINAL_SISA,(isnull(a.FDPNOMINAL,0)-isnull(FDPNOMINAL_SISA,0)) as Sisasaldo  
        ,A.FDPKD_PAKET,d.FMPKPAKETN 
        ,isnull((SELECT sum(z.FDTQTY) as QTY FROM TRANSAKSIPASIEN x inner join TRANSAKSIPASIEND z on x.FTNO_TRANSAKSI=z.FDTNO_TRANSAKSI where z.FDTNO_FAKTUR = a.FDPNO_DEPOSIT AND z.FDTKD_PRODUK = b.FDPDKD_PRODUK),0) as qtypakai  
        from DEPOSIT_PAKET a inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN 
        left join DEPOSIT_PAKETD b on a.FDPNO_DEPOSIT=b.FDPDNO_DEPOSIT 
        left join PRODUK_PAKET d on a.FDPKD_PAKET=d.FMPKKD_PAKET 
        WHERE FDPSTATUS = 1 AND A.FDPKD_PASIEN = %s and a.FDP_JENIS_DEPOSITO=%s 
        and isnull(a.FDPNOMINAL,0)-isnull(FDPNOMINAL_SISA,0)<>0  
        AND a.FDPKD_CABANG= %s 
        order by TANGGAL asc
    """
    result = Globals().getDataQuery(q , [kd_pasien,jenis_deposit,KD_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")	

def findDepositPaketD(request):
    kd_pasien = request.GET['kd_pasien']
    KD_CABANG= request.session['kdCabang']
    jenis_deposit = Globals().input(request.GET, 'jenis_deposit',0)
    q  = """
        select * from 
        (select   
        distinct  A.FDPNO_DEPOSIT, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,FDPNOMINAL,isnull(FDPNOMINAL_SISA,0) as FDPNOMINAL_SISA,(isnull(a.FDPNOMINAL,0)-isnull(FDPNOMINAL_SISA,0)) as Sisasaldo 
        ,b.FDPDQTY ,A.FDPKD_PAKET,d.FMPKPAKETN 
        ,isnull((SELECT sum(z.FDTQTY) as QTY FROM TRANSAKSIPASIEN x inner join TRANSAKSIPASIEND z on x.FTNO_TRANSAKSI=z.FDTNO_TRANSAKSI where z.FDTNO_FAKTUR = a.FDPNO_DEPOSIT AND z.FDTKD_PRODUK = b.FDPDKD_PRODUK),0) as qtypakai 
        from DEPOSIT_PAKET a inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN 
        inner join DEPOSIT_PAKETD b on a.FDPNO_DEPOSIT=b.FDPDNO_DEPOSIT 
        left join PRODUK_PAKET d on a.FDPKD_PAKET=d.FMPKKD_PAKET  
        WHERE FDPSTATUS = 1 AND A.FDPKD_PASIEN = %s and FDP_JENIS_DEPOSITO=%s 
        AND a.FDPKD_CABANG= %s 
        ) as dd where dd.FDPDQTY <> qtypakai 
        order by TANGGAL asc
    """
    result = Globals().getDataQuery(q , [kd_pasien,jenis_deposit,KD_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")	

def getGridPaketprodukpasien(request):
    no_bukti = request.GET['no_bukti']
    nominal_deposit= request.GET['nominal_deposit']
    databukti=no_bukti.split(',')
    KD_CABANG= request.session['kdCabang']
    q = "select A.FDPNO_DEPOSIT as NOFAKTUR, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,C.ALAMAT, "
    q += "a.FDPKD_PAKET,a.FDPKETERANGAN,isnull(a.FDPSTATUS,0) as FDPSTATUS,a.USERRS,a.UPDATERS,d.FMPKPAKETN,  "
    q += "ROW_NUMBER() OVER (ORDER BY FMPPRODUKN) AS NO,b.FDPDKD_PRODUK as ID_PRODUK, 1 as QTY, FDPDTARIF as HARGA,  "
    q += "FDPD_DISCKONSUMEN as DISCKONSUMEN, FDPD_DISC1 as DISC, FDPD_DISC2 as DISC2, FDPD_DISC3 as DISC3, FDPD_DISC4/FDPDQTY as DISC4,e.FMPPRODUKN as NAMA_PRODUK,G.FMTFEE_RESELER AS DISCRESELER, "
    q += "ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE b.FDPDKD_PRODUK=H.FMTCKD_PRODUK  AND I.JASAKOMPONENT='2') ,0) AS FEEDOKTER, "
    q += "ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE b.FDPDKD_PRODUK=H.FMTCKD_PRODUK  AND I.JASAKOMPONENT='5') ,0) AS FEEBC, "
    q += "ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE b.FDPDKD_PRODUK=H.FMTCKD_PRODUK  AND I.JASAKOMPONENT='7') ,0) AS FEEPERAWAT "
    q += "from DEPOSIT_PAKET a inner join DEPOSIT_PAKETD b on a.FDPNO_DEPOSIT=b.FDPDNO_DEPOSIT   "
    q += "inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN  "
    q += "left join PRODUK_PAKET d on a.FDPKD_PAKET=d.FMPKKD_PAKET "
    q += "left join PRODUK e on b.FDPDKD_PRODUK=e.FMPPRODUK_ID "
    q += "left join TARIF AS G ON b.FDPDKD_PRODUK=G.FMTKD_PRODUK AND G.FMTTGL_BERLAKU in (SELECT MAX(FMTTGL_BERLAKU) AS TGL_AKHIR FROM TARIF WHERE FMTKD_PRODUK =b.FDPDKD_PRODUK) "
    q += "where A.FDPNO_DEPOSIT in( "
    i=0
    for x in databukti:
        if i==0:
            q +="'"+ x +"'"
        else :
            q +=",'"+ x +"'"
        i+=1

    q += ")  "
    q += "AND FDPSTATUS = 1 AND a.FDPKD_CABANG= %s order by NO "
    result = Globals().getDataQuery(q , [KD_CABANG])


    q = "SELECT *,ISNULL(TOTAL_JAMINAN,0)+ISNULL(Detail_sisa,0) AS JAMINAN FROM (select ROW_NUMBER() OVER (ORDER BY FDPNO_DEPOSIT) AS NO,A.FDPNO_DEPOSIT as NOFAKTUR, convert(varchar, getdate(), 23) as TANGGAL,  "
    q += " IIF(FDP_JENIS_DEPOSITO=1,0,%s) as TOTAL_JAMINAN,0 as PIUTANG,0 as BANK,0 as VOUCHER,0 as TUNAI, "
    q += "(select sum(dbo.fungsiCalculasiDeposit(FDPDTARIF,1,FDPD_DISCKONSUMEN,FDPD_DISC1,FDPD_DISC2,FDPD_DISC3,FDPD_DISC4))   "
    q += "FROM DEPOSIT_PAKETD b where b.FDPDNO_DEPOSIT=a.FDPNO_DEPOSIT) as Detail_sisa   "
    q += "from DEPOSIT_PAKET a   "
    q += "where A.FDPNO_DEPOSIT in( "
    i=0
    for x in databukti:
        if i==0:
            q +="'"+ x +"'"
        else :
            q +=",'"+ x +"'"
        i+=1
    q += ")  "
    q += "AND FDPSTATUS = 1 AND a.FDPKD_CABANG= %s ) AS XYZ order by NOFAKTUR "
    result5 = Globals().getDataQuery(q , [nominal_deposit,KD_CABANG])

    json_data = json.dumps({
		'data1':result,'data5':result5
	}, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def SP_BATAL_BAYAR(request):
    FH_BUKTI_ID = request.POST['FH_BUKTI_ID']
    USERRS = request.session['user_id']
    status_aud = request.POST['StatusAUD']

    q = "SET NOCOUNT ON;"
    q += "EXEC IMD_BATAL_PEMBAYARAN "
    q += "'" + FH_BUKTI_ID + "',"
    q += "'" + USERRS + "',"
    q += "'" + status_aud + "' "

    if (status_aud=='D') :
        user = {
        'user_id': request.session['user_id'],
        'user_name': request.session['user_name'],
        'user_priv': request.session['user_priv'],
        }
        data = []
        data.append({"query": "select * from TRANSAKSIBAYARD where FTBNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        
        Globals().create_log('Hapus LogDelete.txt', 'IMMODERMA', data, user)
    try:
        result = Globals().getDataSP(q)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)

def SP_UBAH_PAKET(request):
    FH_BUKTI_ID = request.POST['FH_BUKTI_ID']
    USERRS = request.session['user_id']

    q = "SET NOCOUNT ON;"
    q += "EXEC IMD_UBAH_PAKET "
    q += "'" + FH_BUKTI_ID + "',"
    q += "'" + USERRS + "' "


    user = {
    'user_id': request.session['user_id'],
    'user_name': request.session['user_name'],
    'user_priv': request.session['user_priv'],
    }
    data = []
    data.append({"query": "select * from DEPOSIT_PAKET a left join DEPOSIT_PAKETD b on a.FDPNO_DEPOSIT=b.FDPDNO_DEPOSIT where FDPNO_DEPOSIT = '" + FH_BUKTI_ID + "'"})
    
    Globals().create_log('Hapus LogDelete.txt', 'IMMODERMA', data, user)

    try:
        result = Globals().getDataSP(q)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)

def Cekdepositfarmasi(request):
    bukti = request.GET['bukti']
    KD_CABANG= request.session['kdCabang']
    q ="select a.FHFJBUKTI_ID from FJINKOTA a where a.FHFJBUKTI_ID = %s and a.FHFJBRANCH = %s "
    result = Globals().getDataQuery(q , [bukti,KD_CABANG])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")	

def getPembelianByBuktiPembelian(request):
	KD_CABANG= request.session['kdCabang']
	no_bukti = request.GET['no_bukti']
	q = "select FTNO_NOTA from TRANSAKSIPASIEN  "
	q += "where FTNO_NOTA = %s and KD_CABANG= %s "
	result = Globals().getDataQuery(q, [no_bukti,KD_CABANG])
	
	if len(result)==0:
		data={
			'status':'gagal',
			'pesen':'data tidak ditemukan',
			'data':None
		}
	else:
		data={
			'status':'ok',
			'pesen':'data ditemukan',
			'data':result[0]
		}
	json_data = json.dumps(data, cls=DjangoJSONEncoder)
	
	return HttpResponse(json_data, content_type="application/json")