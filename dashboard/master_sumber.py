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


def master_sumber(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']

        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "master_sumber")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "master_sumber", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "master_sumber", '1')
        menubarCount = len(menubars)

        response = render(request, 'dashboard/sumber/sumberfrm.html', {
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


def aud_Sumber(request):
    Sumber_id = request.POST['Sumber_id']
    nama = request.POST['nama']
    user = request.session['user_id']
    status_aud = request.POST['status_aud']

    try:
        q = "EXEC AUD_SUMBER %s, %s, %s, %s"
        result = Globals().getDataSP(q, [Sumber_id, nama,user,status_aud])
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print('coba')


def open_sumber(request):
    q = "SELECT SUMBER_ID,NAMA_SUMBER,USERRS,UPDATERS FROM SUMBER order by NAMA_SUMBER"
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")
