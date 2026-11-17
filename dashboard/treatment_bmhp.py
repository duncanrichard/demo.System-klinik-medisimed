from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from IMMODERMA.globals import Globals

from .forms import TreatmentBMHPForm
from .models import TreatmentBMHP


def _treatments():
    return Globals().getDataQuery(
        "SELECT FMPPRODUK_ID, FMPPRODUKN FROM PRODUK "
        "WHERE FMPPRODUK_ID IS NOT NULL ORDER BY FMPPRODUKN, FMPPRODUK_ID"
    )


def _mapped_treatments():
    return Globals().getDataQuery(
        "SELECT mapping.treatment_id, ISNULL(produk.FMPPRODUKN, mapping.treatment_id) AS treatment_name, "
        "COUNT(mapping.id) AS total_bmhp "
        "FROM TREATMENT_BMHP AS mapping "
        "LEFT JOIN PRODUK AS produk ON produk.FMPPRODUK_ID = mapping.treatment_id "
        "GROUP BY mapping.treatment_id, produk.FMPPRODUKN "
        "ORDER BY produk.FMPPRODUKN, mapping.treatment_id"
    )


def _unmapped_treatments():
    return Globals().getDataQuery(
        "SELECT produk.FMPPRODUK_ID, produk.FMPPRODUKN FROM PRODUK AS produk "
        "WHERE produk.FMPPRODUK_ID IS NOT NULL "
        "AND NOT EXISTS (SELECT 1 FROM TREATMENT_BMHP AS mapping "
        "WHERE mapping.treatment_id = produk.FMPPRODUK_ID) "
        "ORDER BY produk.FMPPRODUKN, produk.FMPPRODUK_ID"
    )


def _page_context(
    request,
    treatment_id=None,
    form=None,
    editing=None,
    open_edit_modal=False,
    edit_rows=None,
    bulk_error="",
    open_create_modal=False,
    create_rows=None,
    create_error="",
    selected_create_treatment_id="",
):
    user_priv = request.session["user_priv"]
    menubars = Globals().getMenubars(user_priv, "IMMODERMA", None, "0")
    selected_treatment_id = treatment_id or request.GET.get("treatment_id", "")
    usages = TreatmentBMHP.objects.none()
    if selected_treatment_id:
        usages = TreatmentBMHP.objects.filter(treatment_id=selected_treatment_id).select_related("bmhp")

    mapped_usage_data = [
        {
            "id": usage.id,
            "treatment_id": usage.treatment_id,
            "bmhp_id": usage.bmhp_id,
            "bmhp_name": usage.bmhp.nama_bmhp,
            "jumlah": format(usage.jumlah, ".2f"),
            "satuan": usage.satuan,
            "update_url": reverse("treatment_bmhp_update", args=[usage.id]),
        }
        for usage in TreatmentBMHP.objects.select_related("bmhp").all()
    ]

    return {
        "navbars": Globals().getNavbars(user_priv, "IMMODERMA", None),
        "menubars": menubars,
        "menubarsChild": Globals().getMenubars(user_priv, "IMMODERMA", None, "1"),
        "menubarsType": 1,
        "count_": len(menubars),
        "list_": Globals().getSeparator(len(menubars)),
        "treatments": _treatments(),
        "unmapped_treatments": _unmapped_treatments(),
        "mapped_treatments": _mapped_treatments(),
        "selected_treatment_id": selected_treatment_id,
        "form": form or TreatmentBMHPForm(),
        "editing": editing,
        "open_edit_modal": open_edit_modal,
        "mapped_usage_data": mapped_usage_data,
        "edit_rows": edit_rows or [],
        "bulk_error": bulk_error,
        "open_create_modal": open_create_modal,
        "create_rows": create_rows or [],
        "create_error": create_error,
        "selected_create_treatment_id": selected_create_treatment_id,
        "usages": usages,
    }


def treatment_bmhp(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    response = render(request, "dashboard/treatment_bmhp/base.html", _page_context(request))
    response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    return response


def _require_treatment(request):
    treatment_id = request.POST.get("treatment_id", "").strip()
    if not treatment_id:
        return None
    return treatment_id


@require_POST
def create_treatment_bmhp(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    treatment_id = _require_treatment(request)
    if treatment_id is None:
        return HttpResponseBadRequest("Pilih treatment terlebih dahulu.")

    rows, error = _submitted_bmhp_rows(request)
    if error or not rows:
        return render(
            request,
            "dashboard/treatment_bmhp/base.html",
            _page_context(
                request,
                open_create_modal=True,
                create_rows=_posted_bmhp_rows(request),
                create_error=error or "Tambahkan minimal satu data BMHP.",
                selected_create_treatment_id=treatment_id,
            ),
            status=400,
        )

    if TreatmentBMHP.objects.filter(treatment_id=treatment_id).exists():
        return HttpResponseBadRequest("Treatment ini sudah memiliki data BMHP.")

    try:
        with transaction.atomic():
            for row in rows:
                TreatmentBMHP.objects.create(
                    treatment_id=treatment_id,
                    bmhp_id=row["bmhp_id"],
                    jumlah=row["jumlah"],
                    satuan=row["satuan"],
                )
    except IntegrityError:
        return render(
            request,
            "dashboard/treatment_bmhp/base.html",
            _page_context(
                request,
                open_create_modal=True,
                create_rows=_posted_bmhp_rows(request),
                create_error="BMHP dengan satuan yang sama tidak boleh diinput lebih dari sekali.",
                selected_create_treatment_id=treatment_id,
            ),
            status=400,
        )

    messages.success(request, "Data BMHP treatment berhasil ditambahkan.")
    return redirect("/treatment_bmhp/")


def edit_treatment_bmhp(request, usage_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    usage = get_object_or_404(TreatmentBMHP, pk=usage_id)
    return render(
        request,
        "dashboard/treatment_bmhp/base.html",
        _page_context(
            request,
            treatment_id=usage.treatment_id,
            form=TreatmentBMHPForm(instance=usage),
            editing=usage,
        ),
    )


@require_POST
def update_treatment_bmhp(request, usage_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    usage = get_object_or_404(TreatmentBMHP, pk=usage_id)
    form = TreatmentBMHPForm(request.POST, instance=usage)
    if form.is_valid():
        try:
            form.save()
        except IntegrityError:
            form.add_error("bmhp", "BMHP dengan satuan yang sama sudah terdaftar pada treatment ini.")
        else:
            messages.success(request, "Pemakaian BMHP berhasil diperbarui.")
            return redirect(f"/treatment_bmhp/?treatment_id={usage.treatment_id}")

    return render(
        request,
        "dashboard/treatment_bmhp/base.html",
        _page_context(
            request,
            treatment_id=usage.treatment_id,
            form=form,
            editing=usage,
            open_edit_modal=True,
        ),
        status=400,
    )


def _submitted_bmhp_rows(request):
    usage_ids = request.POST.getlist("usage_id")
    bmhp_ids = request.POST.getlist("bmhp_id")
    jumlahs = request.POST.getlist("jumlah")
    satuans = request.POST.getlist("satuan")
    if not (len(usage_ids) == len(bmhp_ids) == len(jumlahs) == len(satuans)):
        return [], "Data BMHP tidak lengkap. Silakan ulangi perubahan Anda."

    rows = []
    duplicate_keys = set()
    for index, bmhp_id in enumerate(bmhp_ids):
        form = TreatmentBMHPForm(
            {"bmhp": bmhp_id, "jumlah": jumlahs[index], "satuan": satuans[index]}
        )
        if not form.is_valid():
            return [], f"Data BMHP pada baris {index + 1} belum valid."

        cleaned = form.cleaned_data
        duplicate_key = (cleaned["bmhp"].pk, cleaned["satuan"])
        if duplicate_key in duplicate_keys:
            return [], "BMHP dengan satuan yang sama tidak boleh diinput lebih dari sekali."
        duplicate_keys.add(duplicate_key)
        rows.append(
            {
                "usage_id": usage_ids[index],
                "bmhp_id": cleaned["bmhp"].pk,
                "jumlah": str(cleaned["jumlah"]),
                "satuan": cleaned["satuan"],
            }
        )
    return rows, ""


def _posted_bmhp_rows(request):
    usage_ids = request.POST.getlist("usage_id")
    bmhp_ids = request.POST.getlist("bmhp_id")
    jumlahs = request.POST.getlist("jumlah")
    satuans = request.POST.getlist("satuan")
    return [
        {
            "usage_id": usage_ids[index] if index < len(usage_ids) else "",
            "bmhp_id": bmhp_ids[index] if index < len(bmhp_ids) else "",
            "jumlah": jumlahs[index] if index < len(jumlahs) else "",
            "satuan": satuans[index] if index < len(satuans) else "",
        }
        for index in range(max(len(usage_ids), len(bmhp_ids), len(jumlahs), len(satuans)))
    ]


@require_POST
def bulk_update_treatment_bmhp(request, treatment_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    rows, error = _submitted_bmhp_rows(request)
    if error:
        return render(
            request,
            "dashboard/treatment_bmhp/base.html",
            _page_context(
                request,
                treatment_id=treatment_id,
                open_edit_modal=True,
                edit_rows=_posted_bmhp_rows(request),
                bulk_error=error,
            ),
            status=400,
        )

    existing_usages = {
        str(usage.id): usage
        for usage in TreatmentBMHP.objects.filter(treatment_id=treatment_id).select_related("bmhp")
    }
    if any(row["usage_id"] and row["usage_id"] not in existing_usages for row in rows):
        return HttpResponseBadRequest("Data BMHP treatment tidak valid.")

    try:
        with transaction.atomic():
            submitted_usage_ids = {row["usage_id"] for row in rows if row["usage_id"]}
            for usage_id, usage in existing_usages.items():
                if usage_id not in submitted_usage_ids:
                    usage.delete()
            for row in rows:
                if row["usage_id"]:
                    usage = existing_usages[row["usage_id"]]
                    usage.bmhp_id = row["bmhp_id"]
                    usage.jumlah = row["jumlah"]
                    usage.satuan = row["satuan"]
                    usage.save()
                else:
                    TreatmentBMHP.objects.create(
                        treatment_id=treatment_id,
                        bmhp_id=row["bmhp_id"],
                        jumlah=row["jumlah"],
                        satuan=row["satuan"],
                    )
    except IntegrityError:
        return render(
            request,
            "dashboard/treatment_bmhp/base.html",
            _page_context(
                request,
                treatment_id=treatment_id,
                open_edit_modal=True,
                edit_rows=_posted_bmhp_rows(request),
                bulk_error="BMHP dengan satuan yang sama sudah terdaftar pada treatment ini.",
            ),
            status=400,
        )

    messages.success(request, "Data BMHP treatment berhasil diperbarui.")
    return redirect("/treatment_bmhp/")


@require_POST
def delete_treatment_bmhp(request, usage_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    usage = get_object_or_404(TreatmentBMHP, pk=usage_id)
    treatment_id = usage.treatment_id
    usage.delete()
    messages.success(request, "BMHP berhasil dihapus dari treatment.")
    return redirect(f"/treatment_bmhp/?treatment_id={treatment_id}")


@require_POST
def delete_treatment_bmhp_mapping(request, treatment_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    deleted_count, _ = TreatmentBMHP.objects.filter(treatment_id=treatment_id).delete()
    if deleted_count:
        messages.success(request, "Seluruh BMHP untuk treatment berhasil dihapus.")
    else:
        messages.warning(request, "Data BMHP treatment tidak ditemukan.")
    return redirect("/treatment_bmhp/")
