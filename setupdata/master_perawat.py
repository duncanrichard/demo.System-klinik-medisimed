from django.shortcuts import render,redirect
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from urllib.parse import unquote
from inspect import getmembers
from pprint import pprint
from IMMODERMA.globals import Globals
from IMMODERMA.config import env
from datetime import datetime
from django.urls import include, re_path as url
from django.db import transaction

def exit(request):
    return redirect('/')

def master_perawat(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "master_perawat")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "master_perawat", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "master_perawat", '1')
        menubarCount = len(menubars)

        response = render(request, 'setupdata/perawat/base.html', {
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

def aud_perawat(request):
    far_kode_perawat = request.POST['far_kode_perawat']
    far_nama_perawat = request.POST['far_nama_perawat']
    far_jabatan_perawat= request.POST['far_jabatan_perawat']
    far_kode_nip = request.POST['far_kode_nip']
    aktif = request.POST['aktif']
    hidden = request.POST.get('hidden', '0')
    bidan = request.POST['bidan']
    user = request.session['user_id']
    cabang_id = request.session['kdCabang']
    status_aud = request.POST['status_aud']

    try:
        q = "EXEC MST_AUD_PERAWAT %s, %s, %s, %s, %s, %s, %s, %s, %s"
        result = Globals().getDataSP(q, [far_kode_perawat, far_nama_perawat,far_jabatan_perawat,far_kode_nip,aktif,bidan,user,cabang_id,status_aud])
        perawat_id = far_kode_perawat
        if result and status_aud != 'D':
            perawat_id = result[0].get('perawat_ID', perawat_id)
        if perawat_id and status_aud != 'D':
            hidden = 1 if str(hidden) == '1' else 0
            # Keep the visibility key aligned with the branch stored on the
            # nurse record, not only with the session representation.
            branch_row = Globals().getDataQuery(
                "SELECT TOP (1) KD_CABANG FROM PERAWAT WHERE FMPPERAWAT_ID = %s "
                "ORDER BY CASE WHEN KD_CABANG = %s THEN 0 ELSE 1 END",
                [perawat_id, cabang_id],
            )
            visibility_branch = branch_row[0]['KD_CABANG'] if branch_row else cabang_id
            with transaction.atomic():
                Globals().executeQuery(
                    "IF EXISTS (SELECT 1 FROM NAKES_PEMBELIAN_VISIBILITY "
                    "WHERE nakes_type = %s AND nakes_id = %s AND kd_cabang = %s) "
                    "UPDATE NAKES_PEMBELIAN_VISIBILITY SET is_hidden = %s, updated_by = %s, "
                    "updated_at = SYSUTCDATETIME() WHERE nakes_type = %s AND nakes_id = %s AND kd_cabang = %s "
                    "ELSE INSERT INTO NAKES_PEMBELIAN_VISIBILITY "
                    "(nakes_type, nakes_id, kd_cabang, is_hidden, updated_by) VALUES (%s, %s, %s, %s, %s)",
                    [
                        'PERAWAT', perawat_id, visibility_branch, hidden, user,
                        'PERAWAT', perawat_id, visibility_branch,
                        'PERAWAT', perawat_id, visibility_branch, hidden, user,
                    ],
                )
                saved_visibility = Globals().getDataQuery(
                    "SELECT is_hidden FROM NAKES_PEMBELIAN_VISIBILITY "
                    "WHERE nakes_type = %s AND nakes_id = %s AND kd_cabang = %s",
                    ['PERAWAT', perawat_id, visibility_branch],
                )
                if not saved_visibility or int(saved_visibility[0]['is_hidden']) != hidden:
                    raise RuntimeError('Status tampil Pembelian Perawat gagal disimpan.')
            if result:
                result[0]['IS_HIDDEN'] = hidden
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print('coba')


def open_perawat(request):
    cabang_id = request.session['kdCabang']
    q = "SELECT perawat.FMPPERAWAT_ID,perawat.FMPPERAWATN,perawat.FMPJABATAN,perawat.FMPNIP,perawat.FMPSTATUS,perawat.FMPBIDAN,perawat.KD_CABANG,perawat.USERRS,perawat.UPDATERS,ISNULL(visibility.is_hidden, 0) AS IS_HIDDEN FROM perawat AS perawat LEFT JOIN NAKES_PEMBELIAN_VISIBILITY AS visibility ON visibility.nakes_type = 'PERAWAT' AND visibility.nakes_id = perawat.FMPPERAWAT_ID AND visibility.kd_cabang = perawat.KD_CABANG WHERE perawat.KD_CABANG = %s ORDER BY perawat.FMPPERAWATN"
    result = Globals().getDataQuery(q,[cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
