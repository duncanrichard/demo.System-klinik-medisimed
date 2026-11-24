from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from IMMODERMA.globals import Globals

from .forms import BMHPForm
from .models import BMHP


def _page_context(request, form=None, editing=None):
    user_priv = request.session["user_priv"]
    menubars = Globals().getMenubars(user_priv, "IMMODERMA", None, "0")
    page_obj = Paginator(BMHP.objects.all(), 20).get_page(request.GET.get("page"))
    return {
        "navbars": Globals().getNavbars(user_priv, "IMMODERMA", None),
        "menubars": menubars,
        "menubarsChild": Globals().getMenubars(user_priv, "IMMODERMA", None, "1"),
        "menubarsType": 1,
        "count_": len(menubars),
        "list_": Globals().getSeparator(len(menubars)),
        "form": form or BMHPForm(),
        "editing": editing,
        "bmhps": page_obj,
        "page_obj": page_obj,
    }


def master_bmhp(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    response = render(request, "dashboard/master_bmhp/base.html", _page_context(request))
    response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    return response


@require_POST
def create_bmhp(request):
    if not Globals().isLogin(request):
        return redirect("/login")

    form = BMHPForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "BMHP berhasil ditambahkan.")
        return redirect("master_bmhp")

    return render(request, "dashboard/master_bmhp/base.html", _page_context(request, form=form), status=400)


def edit_bmhp(request, bmhp_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    bmhp = get_object_or_404(BMHP, pk=bmhp_id)
    response = render(
        request,
        "dashboard/master_bmhp/base.html",
        _page_context(request, form=BMHPForm(instance=bmhp), editing=bmhp),
    )
    response["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    return response


@require_POST
def update_bmhp(request, bmhp_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    bmhp = get_object_or_404(BMHP, pk=bmhp_id)
    form = BMHPForm(request.POST, instance=bmhp)
    if form.is_valid():
        form.save()
        messages.success(request, "Nama BMHP berhasil diperbarui.")
        return redirect("master_bmhp")

    return render(
        request,
        "dashboard/master_bmhp/base.html",
        _page_context(request, form=form, editing=bmhp),
        status=400,
    )


@require_POST
def delete_bmhp(request, bmhp_id):
    if not Globals().isLogin(request):
        return redirect("/login")

    get_object_or_404(BMHP, pk=bmhp_id).delete()
    messages.success(request, "BMHP berhasil dihapus.")
    return redirect("master_bmhp")
