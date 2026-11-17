from decimal import Decimal
from datetime import date
from urllib.parse import urlencode

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from IMMODERMA.globals import Globals

from .models import ApotekerPreparation, TreatmentBMHP


def _page_context(request):
    selected_date = request.GET.get("tanggal", "").strip()
    try:
        filter_date = date.fromisoformat(selected_date) if selected_date else date.today()
    except ValueError:
        filter_date = date.today()

    action_filter = request.GET.get("aksi", "belum").strip().lower()
    if action_filter not in {"semua", "belum", "sudah"}:
        action_filter = "belum"

    user_priv = request.session["user_priv"]
    menubars = Globals().getMenubars(user_priv, "IMMODERMA", None, "0")
    status_clause = ""
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

    mappings = {}
    treatment_ids = {item["TREATMENT_ID"] for item in queue}
    if treatment_ids:
        for usage in TreatmentBMHP.objects.select_related("bmhp").filter(
            treatment_id__in=treatment_ids
        ):
            mappings.setdefault(usage.treatment_id, []).append(usage)

    for item in queue:
        treatment_quantity = Decimal(str(item["JUMLAH_TREATMENT"] or 0))
        item["bmhp_items"] = [
            {
                "nama": usage.bmhp.nama_bmhp,
                "jumlah": format(usage.jumlah * treatment_quantity, ".2f"),
                "satuan": usage.satuan,
            }
            for usage in mappings.get(item["TREATMENT_ID"], [])
        ]

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

    if action_filter == "belum":
        transactions = {
            transaction_id: transaction
            for transaction_id, transaction in transactions.items()
            if any(not treatment["PREPARATION_ID"] for treatment in transaction["treatments"])
        }
    elif action_filter == "sudah":
        transactions = {
            transaction_id: transaction
            for transaction_id, transaction in transactions.items()
            if any(treatment["PREPARATION_ID"] for treatment in transaction["treatments"])
        }

    paginator = Paginator(list(transactions.values()), 10)
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
        "action_filter": action_filter,
    }


def apoteker(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    response = render(request, "dashboard/apoteker/base.html", _page_context(request))
    response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    return response


@require_POST
def mark_prepared(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    transaction_id = request.POST.get("transaction_id", "").strip()
    detail_number = request.POST.get("detail_number", "").strip()
    return_params = {
        "tanggal": request.POST.get("tanggal", ""),
        "aksi": request.POST.get("aksi", "belum"),
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
