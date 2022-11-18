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
    bidan = request.POST['bidan']
    user = request.session['user_id']
    cabang_id = request.session['kdCabang']
    status_aud = request.POST['status_aud']

    try:
        q = "EXEC MST_AUD_PERAWAT %s, %s, %s, %s, %s, %s, %s, %s, %s"
        result = Globals().getDataSP(q, [far_kode_perawat, far_nama_perawat,far_jabatan_perawat,far_kode_nip,aktif,bidan,user,cabang_id,status_aud])
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print('coba')


def open_perawat(request):
    cabang_id = request.session['kdCabang']
    q = "SELECT FMPPERAWAT_ID,FMPPERAWATN,FMPJABATAN,FMPNIP,FMPSTATUS,FMPBIDAN,KD_CABANG,USERRS,UPDATERS FROM perawat  WHERE KD_CABANG= %s order by FMPPERAWATN"
    result = Globals().getDataQuery(q,[cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
  