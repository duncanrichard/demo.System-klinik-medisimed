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
from openpyxl import Workbook


def daftar_paket(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "daftar_paket")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "daftar_paket", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "daftar_paket", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/daftar_paket/base.html', {
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
    q += " ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='2' AND H.FMTCTGL_BERLAKU IN (SELECT MAX(FMTCTGL_BERLAKU) FROM TARIF_KOMPONENT WHERE FMTCKD_PRODUK = A.FMPPRODUK_ID)) ,0) AS FEE_DOKTER, "
    q += " ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='5' AND H.FMTCTGL_BERLAKU IN (SELECT MAX(FMTCTGL_BERLAKU) FROM TARIF_KOMPONENT WHERE FMTCKD_PRODUK = A.FMPPRODUK_ID)) ,0) AS FEE_BC, "
    q += " ISNULL((SELECT H.FMTCTARIFPROSEN FROM TARIF_KOMPONENT AS H INNER JOIN PRODUK_COMPONENT AS I ON H.FMTCKD_COMPONENT=I.KD_COMPONENT WHERE A.FMPPRODUK_ID=H.FMTCKD_PRODUK AND A.FMPJENISTARIP=H.FMTCJENISTARIF AND I.JASAKOMPONENT='7' AND H.FMTCTGL_BERLAKU IN (SELECT MAX(FMTCTGL_BERLAKU) FROM TARIF_KOMPONENT WHERE FMTCKD_PRODUK = A.FMPPRODUK_ID)) ,0) AS FEE_PERAWAT "
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

def getpaketprodukByBukti(request):
    no_bukti = request.GET['no_bukti']
    databukti=no_bukti.split(',')
    q = "select ROW_NUMBER() OVER(ORDER BY FMPDKD_PRODUK) AS NO,a.FMPKKD_PAKET,a.FMPKPAKETN,c.FMPPRODUKN as NAMA_PRODUK,a.USERRS,a.UPDATERS,a.FMPKQTY,a.FMPKSTATUS,convert(varchar, a.FMPTGL, 23) as TANGGAL, "
    q += "b.FMPDKD_PRODUK as ID_PRODUK,b.FMPDQTY as QTY,b.FMPDTARIF as HARGA,b.FMPD_DISCKONSUMEN as DISCKONSUMEN,b.FMPD_DISC as DISC,b.FMPD_DISC2 as DISC2,b.FMPD_DISC3 as DISC3,b.FMPD_DISC4 as DISC4  "
    q += "from PRODUK_PAKET a inner join PRODUK_PAKETD b on a.FMPKKD_PAKET=b.FMPDKD_PAKET "
    q += "inner join PRODUK c on b.FMPDKD_PRODUK=c.FMPPRODUK_ID  "
    q += "where FMPKKD_PAKET in( "
    i=0
    for x in databukti:
        if i==0:
            q +="'"+ x +"'"
        else :
            q +=",'"+ x +"'"
        i+=1

    q += ") order by NO "
    result = Globals().getDataQuery(q)

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def SP_AUD_DAFTAR_PAKET(request):
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

    # header
    FH_BUKTI_ID = request.POST['FH_BUKTI_ID']
    FH_DATE = request.POST['FH_DATE']
    FH_ID_PASIEN = request.POST['FH_ID_PASIEN']
    FH_JENIS_DEPOSITO = request.POST['FH_JENIS_DEPOSITO']
    FH_DEPOSITO_TUNAI = request.POST['FH_DEPOSITO_TUNAI']
    FH_KD_PAKET = request.POST['FH_KD_PAKET']
    FH_KETERANGAN= request.POST['FH_KETERANGAN']
    USERRS = request.session['user_id']
    KD_CABANG= request.session['kdCabang']
    status_aud = request.POST['StatusAUD']

    q = "SET NOCOUNT ON;"
    q += "DECLARE @LIST_TRANSAKSI TRANSAKSID;"
    q += "DECLARE @NOW datetime; "
    q += "SET @NOW = GETDATE(); "

    proc_param = []
    i = 0
    for x in FD_NO:
        q += "INSERT INTO @LIST_TRANSAKSI (NO, ID_PODUK, NAMA_PRODUK, HARGA, QTY, DISC, DISC2, DISC3, DISC4, DISCKONSUMEN, BUKTI_ID) "
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
        q += "'" + FH_BUKTI_ID + "');"
        i += 1



    q += "EXEC IMD_AUD_DAFTAR_PAKET_PRODUK "
    q += "'" + FH_BUKTI_ID + "',"
    q += "'" + FH_DATE + "',"
    q += "'" + FH_ID_PASIEN + "',"
    q += "'" + FH_JENIS_DEPOSITO + "',"
    q += "'" + FH_DEPOSITO_TUNAI + "',"
    q += "'" + FH_KD_PAKET + "',"
    q += "'" + FH_KETERANGAN + "',"
    q += "'" + KD_CABANG + "',"
    q += "'" + USERRS + "',"
    q += "'" + status_aud + "', "
    q += "@LIST_TRANSAKSI"

    if (status_aud=='D') :
        user = {
        'user_id': request.session['user_id'],
        'user_name': request.session['user_name'],
        'user_priv': request.session['user_priv'],
        }
        data = []
        data.append({"query": "select * from DEPOSIT_PAKET where FDPNO_DEPOSIT = '" + FH_BUKTI_ID + "'"})
        data.append({"query": "select * from DEPOSIT_PAKETD where FDPDNO_DEPOSIT = '" + FH_BUKTI_ID + "'"})
        data.append({"query": "select * from TRANSAKSIBAYARD where FTBNO_TRANSAKSI = '" + FH_BUKTI_ID + "'"})
        
        Globals().create_log('Hapus LogDelete.txt', 'IMMODERMA', data, user)
    try:
        result = Globals().getDataSP(q)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print(q)

def getDaftarPaketTransaksi(request):
    no_bukti = '%'+request.GET['no_bukti']+'%'
    pasien = '%'+request.GET['pasien']+'%'
    nama_pasien = '%'+request.GET['nama_pasien']+'%'
    tipe = request.GET['tipe']
    tanggal = datetime.strptime(request.GET['tanggal'], "%Y-%m-%d")
    KD_CABANG= request.session['kdCabang']

    if(tipe == 'daftar_paket_by_bulan'):
        q = "select  top 100 A.FDPNO_DEPOSIT, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,a.FDPNOMINAL  "
        q +="from DEPOSIT_PAKET a inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN   "
        q +="where (FDPNO_DEPOSIT like %s) and (FDPKD_PASIEN like %s) and "
        q += "(NAMAPASIEN like %s) and (YEAR(FDPTGL_DEPOSIT) = %s) and (MONTH(FDPTGL_DEPOSIT) = %s) and a.FDPKD_CABANG= %s order by FDPNO_DEPOSIT"
        result = Globals().getDataQuery(q, [no_bukti, pasien, nama_pasien, tanggal.year, tanggal.month,KD_CABANG])
    else:
        q = "select  top 100 A.FDPNO_DEPOSIT, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,a.FDPNOMINAL  "
        q +="from DEPOSIT_PAKET a inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN "
        q +="where (FDPNO_DEPOSIT like %s) and (FDPKD_PASIEN like %s) and "
        q += "(NAMAPASIEN like %s) and (FDPTGL_DEPOSIT = %s AND a.FDPKD_CABANG= %s )  order by FDPNO_DEPOSIT"
        result = Globals().getDataQuery(q, [no_bukti, pasien, nama_pasien, tanggal,KD_CABANG])

    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getDaftarPaketTransaksiByBukti(request):
    no_bukti = request.GET['no_bukti']
    KD_CABANG= request.session['kdCabang']

    q = "select  A.FDPNO_DEPOSIT, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,C.ALAMAT,a.FDPNOMINAL, "
    q += "a.FDP_JENIS_DEPOSITO,a.FDPKD_PAKET,a.FDPKETERANGAN,isnull(a.FDPSTATUS,0) as FDPSTATUS,a.USERRS,a.UPDATERS,  "
    q += "ROW_NUMBER() OVER (ORDER BY FMPPRODUKN) AS NO,b.FDPDKD_PRODUK as ID_PRODUK, FDPDQTY as QTY, FDPDTARIF as HARGA,  "
    q += "FDPD_DISCKONSUMEN as DISCKONSUMEN, FDPD_DISC1 as DISC, FDPD_DISC2 as DISC2, FDPD_DISC3 as DISC3, FDPD_DISC4 as DISC4,d.FMPPRODUKN as NAMA_PRODUK "
    q += "from DEPOSIT_PAKET a left join DEPOSIT_PAKETD b on a.FDPNO_DEPOSIT=b.FDPDNO_DEPOSIT   "
    q += "inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN  "
    q += "left join PRODUK d on b.FDPDKD_PRODUK=d.FMPPRODUK_ID "
    q += "where (FDPNO_DEPOSIT=%s AND a.FDPKD_CABANG= %s) "
    result = Globals().getDataQuery(q, [no_bukti,KD_CABANG])
    
    q = "select ROW_NUMBER() OVER (ORDER BY FTBNO_TRANSAKSI) AS NO,FTBNO_TRANSAKSI as NO_TRANSAKSI, FTBTGL_TRANSAKSI, FTBTUNAI as TUNAI, isnull(FTBPIUTANG,0) as PIUTANG, isnull(FTBJAMINPERUSAHAAN,0) as JAMINAN, USERRS, UPDATERS, FTBNAMAPEMBAYAR, FTBJUMLAH_UANG, FTBKEMBALIAN_UANG, isnull(FTBNO_FAKTUR,'') as NOFAKTUR,   "
    q += "FTBTGL_FAKTUR, FTBNILAI_FAKTUR, FTBNOKARTU01, FTBNOKARTU02, FTBNOKARTU03, FTBNOKARTU04, FTBDEBITKREDIT01, FTBDEBITKREDIT02, FTBDEBITKREDIT03, FTBDEBITKREDIT04, FTBNILAIBANK01,  "
    q += "FTBNILAIBANK02, FTBNILAIBANK03, FTBNILAIBANK04, FTBBANK01, FTBBANK02, FTBBANK03, FTBBANK04, NO_VOUCHER01, NO_VOUCHER02, NO_VOUCHER03, NO_VOUCHER04, NILAI_VOUCHER01, NILAI_VOUCHER02,  "
    q += "NILAI_VOUCHER03, NILAI_VOUCHER04, "
    q += "(ISNULL(FTBNILAIBANK01,0)+ISNULL(FTBNILAIBANK02,0)+ISNULL(FTBNILAIBANK03,0)+ISNULL(FTBNILAIBANK04,0)) as BANK, "
    q += "(ISNULL(NILAI_VOUCHER01,0)+ISNULL(NILAI_VOUCHER02,0)+ISNULL(NILAI_VOUCHER03,0)+ISNULL(NILAI_VOUCHER04,0)) as VOUCHER "
    q += "FROM TRANSAKSIBAYARD a where  a.FTBNO_TRANSAKSI=%s "
    result5 = Globals().getDataQuery(q, [no_bukti])

    json_data = json.dumps({
		'data1':result,'data5':result5
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
		"Billingdeposit.jrxml", 
		'Billingdeposit', 
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

def getpaketbayar(request):
    bukti = request.GET['bukti']
    q ="select a.FDTNO_FAKTUR from TRANSAKSIPASIEND a where a.FDTNO_FAKTUR = %s  "
    result = Globals().getDataQuery(q , [bukti])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")	

def proses_excel_paket(request):
    kode_deposito = request.GET['kode_deposito']
    KD_CABANG= request.session['kdCabang']
    q = "select * from  "
    q += "(select    "
    q += "A.FDPNO_DEPOSIT, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,FDPNOMINAL,isnull(FDPNOMINAL_SISA,0) as FDPNOMINAL_SISA,(isnull(a.FDPNOMINAL,0)-isnull(FDPNOMINAL_SISA,0)) as SISASALDO  "
    q += ",dbo.fungsideposit(b.FDPDTARIF,b.FDPDQTY,b.FDPD_DISCKONSUMEN,b.FDPD_DISC1,b.FDPD_DISC2,b.FDPD_DISC3,b.FDPD_DISC4) as NILAI_PAKET "
    q += ",b.FDPDQTY ,A.FDPKD_PAKET,d.FMPKPAKETN "
    q += ",isnull((SELECT sum(z.FDTQTY) as QTY FROM TRANSAKSIPASIEN x inner join TRANSAKSIPASIEND z on x.FTNO_TRANSAKSI=z.FDTNO_TRANSAKSI where z.FDTNO_FAKTUR = a.FDPNO_DEPOSIT AND z.FDTKD_PRODUK = b.FDPDKD_PRODUK),0) as QTYPAKAI  "
    q += ",FDP_JENIS_DEPOSITO "
    q += ",b.FDPDKD_PRODUK,p.FMPPRODUKN "
    q += "from DEPOSIT_PAKET a inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN  "
    q += "inner join DEPOSIT_PAKETD b on a.FDPNO_DEPOSIT=b.FDPDNO_DEPOSIT "
    q += "inner join PRODUK p on b.FDPDKD_PRODUK=p.FMPPRODUK_ID "
    q += "left join PRODUK_PAKET d on a.FDPKD_PAKET=d.FMPKKD_PAKET  " 
    q += "WHERE FDPSTATUS = 1 and FDP_JENIS_DEPOSITO=%s "
    q += "AND a.FDPKD_CABANG= %s "
    q += ") as dd where dd.FDPDQTY <> QTYPAKAI "
    result = Globals().getDataQuery(q, [kode_deposito, KD_CABANG])
    # print (result[0])
    # Create a new workbook and add a worksheet
    wb = Workbook()
    ws = wb.active

    # Add headers to the worksheet
    headers = ["FDPNO_DEPOSIT", "TANGGAL", "FDPKD_PASIEN", "NAMAPASIEN", "NILAI_PAKET", "FDPNOMINAL", "FDPNOMINAL_SISA",
               "SISASALDO", "FDPDQTY", "FDPKD_PAKET", "FMPKPAKETN", "QTYPAKAI", "FDP_JENIS_DEPOSITO", "FDPDKD_PRODUK", "FMPPRODUKN"]

    ws.append(headers)

    # Add data to the worksheet
    for row_data in result:
        row = [row_data.get(column_name.upper(), '') for column_name in headers]
        ws.append(row)

    # Save the workbook to a response object
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=exported_data_paket.xlsx'
    wb.save(response)

    return response

def proses_excel_pakettunai(request):
    kode_deposito = request.GET['kode_deposito']
    KD_CABANG= request.session['kdCabang']
    q = "select * from  "
    q += "(select    "
    q += "A.FDPNO_DEPOSIT, convert(varchar, a.FDPTGL_DEPOSIT, 23) as TANGGAL,a.FDPKD_PASIEN,c.NAMAPASIEN,FDPNOMINAL,isnull(FDPNOMINAL_SISA,0) as FDPNOMINAL_SISA,(isnull(a.FDPNOMINAL,0)-isnull(FDPNOMINAL_SISA,0)) as SISASALDO  "
    q += ",dbo.fungsideposit(b.FDPDTARIF,b.FDPDQTY,b.FDPD_DISCKONSUMEN,b.FDPD_DISC1,b.FDPD_DISC2,b.FDPD_DISC3,b.FDPD_DISC4) as NILAI_PAKET "
    q += ",b.FDPDQTY ,A.FDPKD_PAKET,d.FMPKPAKETN "
    q += ",isnull((SELECT sum(z.FDTQTY) as QTY FROM TRANSAKSIPASIEN x inner join TRANSAKSIPASIEND z on x.FTNO_TRANSAKSI=z.FDTNO_TRANSAKSI where z.FDTNO_FAKTUR = a.FDPNO_DEPOSIT AND z.FDTKD_PRODUK = b.FDPDKD_PRODUK),0) as QTYPAKAI  "
    q += ",FDP_JENIS_DEPOSITO "
    q += ",b.FDPDKD_PRODUK,p.FMPPRODUKN "
    q += "from DEPOSIT_PAKET a inner join PASIEN c on a.FDPKD_PASIEN=c.KD_PASIEN  "
    q += "inner join DEPOSIT_PAKETD b on a.FDPNO_DEPOSIT=b.FDPDNO_DEPOSIT "
    q += "inner join PRODUK p on b.FDPDKD_PRODUK=p.FMPPRODUK_ID "
    q += "left join PRODUK_PAKET d on a.FDPKD_PAKET=d.FMPKKD_PAKET  " 
    q += "WHERE FDPSTATUS = 1 and FDP_JENIS_DEPOSITO=%s "
    q += "AND a.FDPKD_CABANG= %s "
    q += ") as dd where dd.FDPNOMINAL_SISA*-1 <> dd.SISASALDO order by dd.TANGGAL desc "
    result = Globals().getDataQuery(q, [kode_deposito, KD_CABANG])
    # print (result[0])
    # Create a new workbook and add a worksheet
    wb = Workbook()
    ws = wb.active

    # Add headers to the worksheet
    headers = ["FDPNO_DEPOSIT", "TANGGAL", "FDPKD_PASIEN", "NAMAPASIEN", "NILAI_PAKET", "FDPNOMINAL", "FDPNOMINAL_SISA",
               "SISASALDO", "FDPDQTY", "FDPKD_PAKET", "FMPKPAKETN", "QTYPAKAI", "FDP_JENIS_DEPOSITO", "FDPDKD_PRODUK", "FMPPRODUKN"]

    ws.append(headers)

    # Add data to the worksheet
    for row_data in result:
        row = [row_data.get(column_name.upper(), '') for column_name in headers]
        ws.append(row)

    # Save the workbook to a response object
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=exported_data_paket.xlsx'
    wb.save(response)

    return response