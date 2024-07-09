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
import bcrypt

def exit(request):
    return redirect('/')

def master_userpriv(request):
    if(Globals().isLogin(request)):
        user_priv = request.session['user_priv']
        user_privelege = request.session['user_priv']
        navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "master_userpriv")
        menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "master_userpriv", '0')
        menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "master_userpriv", '1')
        menubarCount = len(menubars)

        response = render(request, 'setupdata/userpriv/base.html', {
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

def aud_userpriv(request):
    kode_userpriv = request.POST['kode_userpriv']
    nama_userpriv = request.POST['nama_userpriv']
    password_userpriv= request.POST['password_userpriv']
    password_userpriv =createHashPass(password_userpriv)
    privelege_userpriv= request.POST['privelege_userpriv']
    kode_nip = request.POST['kode_nip']
    no_telepon = request.POST['no_telepon']
    aktif = request.POST['aktif']
    cabang_id = request.session['kdCabang']
    status_aud = request.POST['status_aud']

    try:
        q = "EXEC MST_AUD_USERPRIV %s, %s, %s, %s, %s, %s, %s, %s, %s"
        result = Globals().getDataSP(q, [kode_userpriv, nama_userpriv,password_userpriv,privelege_userpriv,kode_nip,no_telepon,aktif,cabang_id,status_aud])
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type="application/json")

    except ValueError:
        print('coba')


def open_userpriv(request):
    cabang_id = request.session['kdCabang']
    q = "select USER_ID,USER_NAME,USER_PRIV,BRANCH,nip,phone,AKTIF from USERSPRIV  WHERE BRANCH= %s order by USER_ID"
    result = Globals().getDataQuery(q,[cabang_id])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getprivelige(request):
    q = "select USER_PRIV,SHIFT_AKTIF,AKTIF from PRIVILEGE order by USER_PRIV"
    result = Globals().getDataQuery(q)
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def createHashPass(password):
    return bcrypt.hashpw(password.encode("utf-8") , bcrypt.gensalt()).decode("utf-8") 
  