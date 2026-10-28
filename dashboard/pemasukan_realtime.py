from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font

from IMMODERMA.globals import Globals


PAYMENT_COLUMNS = (
    "CONVERT(varchar(19), pembayaran.FTBTGL_TRANSAKSI, 120) AS WAKTU, "
    "pembayaran.FTBNO_TRANSAKSI AS NO_TRANSAKSI, "
    "ISNULL(pembayaran.FTBNAMAPEMBAYAR, '') AS NAMA_PEMBAYAR, "
    "ISNULL(pembayaran.FTBTUNAI, 0) AS TUNAI, "
    "(ISNULL(pembayaran.FTBNILAIBANK01, 0) + ISNULL(pembayaran.FTBNILAIBANK02, 0) "
    "+ ISNULL(pembayaran.FTBNILAIBANK03, 0) + ISNULL(pembayaran.FTBNILAIBANK04, 0)) AS BANK, "
    "ISNULL(pembayaran.FTBPIUTANG, 0) AS PIUTANG, "
    "ISNULL(pembayaran.FTBJAMINPERUSAHAAN, 0) AS JAMINAN, "
    "(ISNULL(pembayaran.NILAI_VOUCHER01, 0) + ISNULL(pembayaran.NILAI_VOUCHER02, 0) "
    "+ ISNULL(pembayaran.NILAI_VOUCHER03, 0) + ISNULL(pembayaran.NILAI_VOUCHER04, 0)) AS VOUCHER, "
    "ISNULL(pembayaran.USERRS, '') AS KASIR "
)

PAYMENT_QUERY = (
    "SELECT " + PAYMENT_COLUMNS +
    "FROM TRANSAKSIBAYARD pembayaran "
    "INNER JOIN TRANSAKSIPASIEN transaksi "
    "ON pembayaran.FTBNO_TRANSAKSI = transaksi.FTNO_TRANSAKSI "
    "WHERE transaksi.KD_CABANG = %s "
    "AND pembayaran.FTBTGL_TRANSAKSI >= %s "
    "AND pembayaran.FTBTGL_TRANSAKSI < %s "
    "ORDER BY pembayaran.FTBTGL_TRANSAKSI DESC, pembayaran.FTBNO_TRANSAKSI DESC"
)

MONEY_FIELDS = ("TUNAI", "BANK", "PIUTANG", "JAMINAN", "VOUCHER")


def _selected_date(request):
    value = request.GET.get("tanggal", date.today().isoformat())
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _payment_rows(request):
    selected_date = _selected_date(request)
    if selected_date is None:
        return None, None, JsonResponse(
            {"detail": "Parameter tanggal harus memakai format YYYY-MM-DD."}, status=400
        )

    branch = request.session.get("kdCabang")
    if not branch:
        return None, None, JsonResponse(
            {"detail": "Cabang belum dipilih. Pilih cabang terlebih dahulu."}, status=400
        )

    rows = Globals().getDataQuery(
        PAYMENT_QUERY,
        [branch, selected_date, selected_date + timedelta(days=1)],
    )
    return selected_date, rows, None


def _summary(rows):
    result = {field: Decimal("0") for field in MONEY_FIELDS}
    for row in rows:
        for field in MONEY_FIELDS:
            result[field] += Decimal(str(row.get(field) or 0))
    result["TOTAL"] = sum(result.values(), Decimal("0"))
    return result


def _page_context(request):
    user_priv = request.session["user_priv"]
    navbars = Globals().getNavbars(user_priv, "IMMODERMA", "pemasukan_realtime")
    menubars = Globals().getMenubars(user_priv, "IMMODERMA", "pemasukan_realtime", "0")
    menubars_child = Globals().getMenubars(user_priv, "IMMODERMA", "pemasukan_realtime", "1")
    count = len(menubars)
    return {
        "navbars": navbars,
        "menubars": menubars,
        "menubarsChild": menubars_child,
        "menubarsType": 1,
        "count_": count,
        "list_": Globals().getSeparator(count),
        "today": date.today().isoformat(),
    }


@require_GET
def pemasukan_realtime(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    response = render(request, "dashboard/pemasukan_realtime/base.html", _page_context(request))
    response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    return response


@require_GET
def data(request):
    if not Globals().isLogin(request):
        return JsonResponse({"detail": "Sesi login telah berakhir."}, status=401)

    selected_date, rows, error = _payment_rows(request)
    if error:
        return error

    return JsonResponse(
        {"tanggal": selected_date.isoformat(), "data": rows, "ringkasan": _summary(rows)},
        encoder=DjangoJSONEncoder,
    )


@require_GET
def export(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    selected_date, rows, error = _payment_rows(request)
    if error:
        return error

    workbook = Workbook(write_only=True)
    worksheet = workbook.create_sheet("Pemasukan")
    headers = ["Waktu", "No. Transaksi", "Nama Pembayar", "Tunai", "Bank", "Piutang", "Jaminan", "Voucher", "Total", "Kasir"]
    header_cells = []
    for value in headers:
        cell = WriteOnlyCell(worksheet, value=value)
        cell.font = Font(bold=True)
        header_cells.append(cell)
    worksheet.append(header_cells)

    for row in rows:
        values = [row.get("WAKTU"), row.get("NO_TRANSAKSI"), row.get("NAMA_PEMBAYAR")]
        amounts = [Decimal(str(row.get(field) or 0)) for field in MONEY_FIELDS]
        amount_cells = []
        for value in amounts + [sum(amounts)]:
            cell = WriteOnlyCell(worksheet, value=value)
            cell.number_format = '#,##0.00'
            amount_cells.append(cell)
        worksheet.append(values + amount_cells + [row.get("KASIR")])

    totals = _summary(rows)
    worksheet.append([])
    total_cells = []
    for value in [totals[field] for field in MONEY_FIELDS] + [totals["TOTAL"]]:
        cell = WriteOnlyCell(worksheet, value=value)
        cell.number_format = '#,##0.00'
        cell.font = Font(bold=True)
        total_cells.append(cell)
    worksheet.append(["TOTAL"] + [""] * 2 + total_cells)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="pemasukan-realtime-{}.xlsx"'.format(selected_date.isoformat())
    )
    workbook.save(response)
    return response
