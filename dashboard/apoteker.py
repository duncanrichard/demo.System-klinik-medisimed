from decimal import Decimal
from datetime import date
from base64 import b64decode
from binascii import Error as BinasciiError
from urllib.parse import urlencode

from django.contrib import messages
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET, require_POST

from IMMODERMA.globals import Globals

from .models import ApotekerPreparation, ApotekerSignature, TreatmentBMHP


def _signature_data(value):
    value = value.strip()
    if not value:
        return ""

    prefix = "data:image/png;base64,"
    if not value.startswith(prefix) or len(value) > 500000:
        raise ValueError

    try:
        b64decode(value[len(prefix):], validate=True)
    except (BinasciiError, ValueError):
        raise ValueError from None
    return value


def _attach_bmhp_items(treatments):
    mappings = {}
    treatment_ids = {item["TREATMENT_ID"] for item in treatments}
    if treatment_ids:
        for usage in TreatmentBMHP.objects.select_related("bmhp").filter(
            treatment_id__in=treatment_ids
        ):
            mappings.setdefault(usage.treatment_id, []).append(usage)

    for item in treatments:
        treatment_quantity = Decimal(str(item["JUMLAH_TREATMENT"] or 0))
        item["bmhp_items"] = [
            {
                "nama": usage.bmhp.nama_bmhp,
                "jumlah": format(usage.jumlah * treatment_quantity, ".2f"),
                "satuan": usage.satuan,
            }
            for usage in mappings.get(item["TREATMENT_ID"], [])
        ]


def _transaction_is_prepared(treatments):
    mapped_treatments = [treatment for treatment in treatments if treatment["bmhp_items"]]
    return bool(mapped_treatments) and all(
        treatment.get("PREPARATION_ID") for treatment in mapped_treatments
    )


def _staff_names(
    transaction_id, branch_id, relation_table, transaction_column, staff_column
):
    query = (
        "SELECT staff.NAMA FROM ("
        "SELECT dokter.FMDDOKTERN AS NAMA "
        f"FROM {relation_table} AS relasi "
        f"INNER JOIN DOKTER AS dokter ON relasi.{staff_column} = dokter.FMDDOKTER_ID "
        f"WHERE relasi.{transaction_column} = %s AND dokter.KD_CABANG = %s "
        "UNION "
        "SELECT perawat.FMPPERAWATN AS NAMA "
        f"FROM {relation_table} AS relasi "
        f"INNER JOIN PERAWAT AS perawat ON relasi.{staff_column} = perawat.FMPPERAWAT_ID "
        f"WHERE relasi.{transaction_column} = %s AND perawat.KD_CABANG = %s"
        ") AS staff ORDER BY staff.NAMA"
    )
    return [
        item["NAMA"]
        for item in Globals().getDataQuery(
            query, [transaction_id, branch_id, transaction_id, branch_id]
        )
    ]


def _page_context(request):
    selected_date = request.GET.get("tanggal", "").strip()
    try:
        filter_date = date.fromisoformat(selected_date) if selected_date else date.today()
    except ValueError:
        filter_date = date.today()

    user_priv = request.session["user_priv"]
    menubars = Globals().getMenubars(user_priv, "IMMODERMA", None, "0")
    queue_query = (
        "SELECT transaksi.FTNO_TRANSAKSI, detail.FDTNOMER, "
        "CONVERT(varchar, transaksi.FTTGL_TRANSAKSI, 23) AS TANGGAL, "
        "CONVERT(varchar, transaksi.FTTGL_TRANSAKSI, 108) AS WAKTU_PERMINTAAN, "
        "pasien.KD_PASIEN, pasien.NAMAPASIEN, detail.FDTKD_PRODUK AS TREATMENT_ID, "
        "detail.FDTKDPRODUKN AS NAMA_TREATMENT, detail.FDTQTY AS JUMLAH_TREATMENT, "
        "persiapan.id AS PREPARATION_ID "
        "FROM TRANSAKSIPASIEN AS transaksi "
        "INNER JOIN KUNJUNGANPASIEN AS kunjungan ON transaksi.FTNO_KUNJUNGAN = kunjungan.KPNO_TRANSAKSI "
        "INNER JOIN PASIEN AS pasien ON kunjungan.KPKD_PASIEN = pasien.KD_PASIEN "
        "INNER JOIN TRANSAKSIPASIEND AS detail ON transaksi.FTNO_TRANSAKSI = detail.FDTNO_TRANSAKSI "
        "LEFT JOIN APOTEKER_PERSIAPAN_BMHP AS persiapan "
        "ON persiapan.transaction_id = transaksi.FTNO_TRANSAKSI "
        "AND persiapan.transaction_detail_number = detail.FDTNOMER "
        "WHERE transaksi.KD_CABANG = %s AND CAST(transaksi.FTTGL_TRANSAKSI AS date) = %s "
        "ORDER BY transaksi.FTTGL_TRANSAKSI, transaksi.FTNO_TRANSAKSI, detail.FDTNOMER"
    )
    queue = Globals().getDataQuery(
        queue_query,
        [request.session["kdCabang"], filter_date],
    )

    _attach_bmhp_items(queue)

    transactions = {}
    for item in queue:
        transaction = transactions.setdefault(
            item["FTNO_TRANSAKSI"],
            {
                "FTNO_TRANSAKSI": item["FTNO_TRANSAKSI"],
                "TANGGAL": item["TANGGAL"],
                "WAKTU_PERMINTAAN": item["WAKTU_PERMINTAAN"],
                "KD_PASIEN": item["KD_PASIEN"],
                "NAMAPASIEN": item["NAMAPASIEN"],
                "treatments": [],
            },
        )
        transaction["treatments"].append(item)

    for transaction in transactions.values():
        # One row represents a transaction. It becomes yellow only after all
        # treatments that have BMHP mapping have been prepared.
        transaction["is_prepared"] = _transaction_is_prepared(
            transaction["treatments"]
        )

    ordered_transactions = sorted(
        transactions.values(),
        key=lambda transaction: (
            transaction["is_prepared"],
            transaction["WAKTU_PERMINTAAN"],
            transaction["FTNO_TRANSAKSI"],
        ),
    )
    paginator = Paginator(ordered_transactions, 10)
    queue_page = paginator.get_page(request.GET.get("page", 1))

    return {
        "navbars": Globals().getNavbars(user_priv, "IMMODERMA", None),
        "menubars": menubars,
        "menubarsChild": Globals().getMenubars(user_priv, "IMMODERMA", None, "1"),
        "menubarsType": 1,
        "count_": len(menubars),
        "list_": Globals().getSeparator(len(menubars)),
        "queue": queue_page,
        "filter_date": filter_date.isoformat(),
    }


def apoteker(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    response = render(request, "dashboard/apoteker/base.html", _page_context(request))
    response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    return response


@require_GET
def receipt(request, transaction_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    branch_id = request.session["kdCabang"]
    treatments = Globals().getDataQuery(
        "SELECT transaksi.FTNO_TRANSAKSI, detail.FDTNOMER, "
        "CONVERT(varchar, transaksi.FTTGL_TRANSAKSI, 23) AS TANGGAL, "
        "CONVERT(varchar, transaksi.FTTGL_TRANSAKSI, 108) AS WAKTU, "
        "pasien.KD_PASIEN, pasien.NAMAPASIEN, "
        "detail.FDTKD_PRODUK AS TREATMENT_ID, detail.FDTKDPRODUKN AS NAMA_TREATMENT, "
        "detail.FDTQTY AS JUMLAH_TREATMENT, persiapan.id AS PREPARATION_ID "
        "FROM TRANSAKSIPASIEN AS transaksi "
        "INNER JOIN KUNJUNGANPASIEN AS kunjungan "
        "ON transaksi.FTNO_KUNJUNGAN = kunjungan.KPNO_TRANSAKSI "
        "INNER JOIN PASIEN AS pasien ON kunjungan.KPKD_PASIEN = pasien.KD_PASIEN "
        "INNER JOIN TRANSAKSIPASIEND AS detail "
        "ON transaksi.FTNO_TRANSAKSI = detail.FDTNO_TRANSAKSI "
        "LEFT JOIN APOTEKER_PERSIAPAN_BMHP AS persiapan "
        "ON persiapan.transaction_id = transaksi.FTNO_TRANSAKSI "
        "AND persiapan.transaction_detail_number = detail.FDTNOMER "
        "WHERE transaksi.FTNO_TRANSAKSI = %s AND transaksi.KD_CABANG = %s "
        "ORDER BY detail.FDTNOMER",
        [transaction_id, branch_id],
    )
    if not treatments:
        raise Http404("Transaksi tidak ditemukan.")

    _attach_bmhp_items(treatments)
    if not _transaction_is_prepared(treatments):
        messages.warning(
            request,
            "Receipt belum dapat dicetak karena BMHP belum seluruhnya disiapkan.",
        )
        return redirect("apoteker")
    doctors = _staff_names(
        transaction_id,
        branch_id,
        "TRANSAKSIDOKTERD",
        "FDDNO_TRANSAKSI",
        "FDDKD_DOKTER",
    )
    nurses = _staff_names(
        transaction_id,
        branch_id,
        "TRANSAKSIPERAWATD",
        "FDPNO_TRANSAKSI",
        "FDPKD_PERAWAT",
    )
    bc = [
        item["NAMA"]
        for item in Globals().getDataQuery(
            "SELECT DISTINCT perawat.FMPPERAWATN AS NAMA "
            "FROM TRANSAKSIBCD AS relasi "
            "INNER JOIN PERAWAT AS perawat ON relasi.FDBC_ID = perawat.FMPPERAWAT_ID "
            "WHERE relasi.FDBCNO_TRANSAKSI = %s AND perawat.KD_CABANG = %s "
            "ORDER BY perawat.FMPPERAWATN",
            [transaction_id, branch_id],
        )
    ]
    signature = ApotekerSignature.objects.filter(transaction_id=transaction_id).first()
    if signature is None:
        signature = {
            "penerima_nama": "",
            "penerima_tanda_tangan": "",
            "penyerah_nama": "",
            "penyerah_tanda_tangan": "",
        }

    response = render(
        request,
        "dashboard/apoteker/receipt.html",
        {
            "transaction": treatments[0],
            "treatments": treatments,
            "doctors": doctors,
            "bc": bc,
            "nurses": nurses,
            "clinic_name": request.session.get("nama_cabang", ""),
            "clinic_city": request.session.get("kota_cabang", ""),
            "clinic_address": request.session.get("alamat_cabang", ""),
            "signature": signature,
        },
    )
    response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    return response


@require_POST
def save_signature(request, transaction_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    valid_transaction = Globals().getDataQuery(
        "SELECT 1 FROM TRANSAKSIPASIEN "
        "WHERE FTNO_TRANSAKSI = %s AND KD_CABANG = %s",
        [transaction_id, request.session["kdCabang"]],
    )
    if not valid_transaction:
        raise Http404("Transaksi tidak ditemukan.")

    penerima_nama = request.POST.get("penerima_nama", "").strip()[:100]
    penyerah_nama = request.POST.get("penyerah_nama", "").strip()[:100]
    try:
        penerima_tanda_tangan = _signature_data(
            request.POST.get("penerima_tanda_tangan", "")
        )
        penyerah_tanda_tangan = _signature_data(
            request.POST.get("penyerah_tanda_tangan", "")
        )
    except ValueError:
        messages.error(request, "Format tanda tangan tidak valid.")
        return redirect("apoteker_receipt", transaction_id=transaction_id)

    if bool(penerima_nama) != bool(penerima_tanda_tangan) or bool(penyerah_nama) != bool(penyerah_tanda_tangan):
        messages.error(request, "Setiap tanda tangan harus disertai nama jelas.")
        return redirect("apoteker_receipt", transaction_id=transaction_id)
    if not penerima_tanda_tangan and not penyerah_tanda_tangan:
        messages.error(request, "Buat minimal satu tanda tangan sebelum menyimpan.")
        return redirect("apoteker_receipt", transaction_id=transaction_id)

    signature, _ = ApotekerSignature.objects.get_or_create(
        transaction_id=transaction_id
    )
    if (
        penerima_tanda_tangan and signature.penerima_tanda_tangan
    ) or (
        penyerah_tanda_tangan and signature.penyerah_tanda_tangan
    ):
        messages.error(request, "Tanda tangan yang sudah tersimpan tidak dapat diubah.")
        return redirect("apoteker_receipt", transaction_id=transaction_id)
    if penerima_tanda_tangan:
        signature.penerima_nama = penerima_nama
        signature.penerima_tanda_tangan = penerima_tanda_tangan
    if penyerah_tanda_tangan:
        signature.penyerah_nama = penyerah_nama
        signature.penyerah_tanda_tangan = penyerah_tanda_tangan
    signature.save()
    messages.success(request, "Tanda tangan digital berhasil disimpan.")
    return redirect("apoteker_receipt", transaction_id=transaction_id)


@require_POST
def mark_prepared(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    transaction_id = request.POST.get("transaction_id", "").strip()
    detail_number = request.POST.get("detail_number", "").strip()
    return_params = {
        "tanggal": request.POST.get("tanggal", ""),
        "page": request.POST.get("page", "1"),
    }
    return_url = "/apoteker/?" + urlencode(return_params)

    if not transaction_id or not detail_number.isdigit():
        messages.error(request, "Data treatment tidak valid.")
        return redirect(return_url)

    valid_detail = Globals().getDataQuery(
        "SELECT 1 FROM TRANSAKSIPASIEN AS transaksi "
        "INNER JOIN TRANSAKSIPASIEND AS detail ON transaksi.FTNO_TRANSAKSI = detail.FDTNO_TRANSAKSI "
        "WHERE transaksi.FTNO_TRANSAKSI = %s AND detail.FDTNOMER = %s AND transaksi.KD_CABANG = %s "
        "AND EXISTS (SELECT 1 FROM TREATMENT_BMHP AS mapping WHERE mapping.treatment_id = detail.FDTKD_PRODUK)",
        [transaction_id, int(detail_number), request.session["kdCabang"]],
    )
    if not valid_detail:
        messages.error(request, "Data treatment tidak ditemukan.")
        return redirect(return_url)

    try:
        ApotekerPreparation.objects.create(
            transaction_id=transaction_id,
            transaction_detail_number=int(detail_number),
            prepared_by=request.session.get("user_id", ""),
        )
    except IntegrityError:
        messages.info(request, "Treatment ini sudah ditandai disiapkan.")
    else:
        messages.success(request, "BMHP treatment sudah ditandai disiapkan.")
    return redirect(return_url)
