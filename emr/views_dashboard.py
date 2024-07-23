from IMMODERMA.globals import Globals
from IMMODERMA.environment import env

import os
import json
import bcrypt
from pprint import pprint
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder

def isLogin(request):
    if 'userauth_emr' in request.session:
        is_login = request.session['userauth_emr']
    else:
        is_login = False
    return is_login

def dashboard(request):
    # Code
    if(isLogin(request)):
        user_priv = request.session['user_priv']
        kdCabang = request.session['kdCabang']
        q = "select * from CABANG  WHERE CABANG_ID=%s "
        cabang = Globals().getDataQuery(q, [kdCabang])
        request.session['kota_cabang'] = cabang[0]['KOTA']
        request.session['nama_cabang'] = cabang[0]['PERUSAHAAN']
        request.session['alamat_cabang'] = cabang[0]['ALAMAT1']


        response = render(request, 'emr/dashboard/home.html', {
        })

        response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
        return response


    else:
        return redirect('/emr/login')

def login(request):

    response = render(request, 'emr/login.html', {'invalid': False })

    # Check Session
    if request.session.get('userauth_emr') == True:
        return redirect('/')

    if request.POST:
        # user = checkLogin(str(request.POST['cabang']),str(request.POST['username']), str(request.POST['password']))
        user = checkLogin(str(request.POST['username']), str(request.POST['password']))
        if user != None:
            # print(user)
            request.session.set_expiry(0)
            request.session['userauth_emr'] = True
            request.session['user_priv'] = user['USER_PRIV']
            request.session['user_name'] = user['USER_NAME']
            request.session['user_emr'] = user['USER_EMR']
            request.session['user_id'] = user['USER_ID']
            request.session['kdCabang'] = user['KD_CABANG']
            # print (request.session['user_id'])

            # DELETE STATIC FILES
            # Globals().deleteFiles()
            # Globals().deleteFiles("/DEBUG/")
            request.session.modified = True
            return redirect('/emr')

        else:
            response = render(request, 'emr/login.html', {'invalid': True, 'message': 'Username atau password Anda salah'})

    response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
    return response

def logout(request):
	request.session['userauth_emr'] = False
	request.session.clear()
	response = redirect('/emr/login')
	for cookie in request.COOKIES:
		response.delete_cookie(cookie)
	return response

# def checkLogin(cabang,username, password):
def checkLogin(username, password):
    q = " SELECT DOKTER.FMDDOKTER_ID as id,(DOKTER.FMDDOKTER_ID+'_'+DOKTER.FMDDOKTERN) as text,DOKTER.PW as PW "
    q +=" ,'DOKTER' as USER_PRIV,DOKTER.FMDDOKTERN as USER_NAME,'DOKTER' as USER_EMR,DOKTER.FMDDOKTER_ID as USER_ID,DOKTER.KD_CABANG as KD_CABANG "
    q +=" FROM DOKTER "
    # q +=" WHERE DOKTER.KD_CABANG=%s AND DOKTER.FMDDOKTER_ID=%s "
    q +=" WHERE  DOKTER.FMDDOKTER_ID=%s "
    q +=" UNION "
    q +=" SELECT PERAWAT.FMPPERAWAT_ID as id,(PERAWAT.FMPPERAWAT_ID+'_'+PERAWAT.FMPPERAWATN) as text,PERAWAT.FMPPW as PW "
    q +=" ,'PERAWAT' as USER_PRIV,PERAWAT.FMPPERAWATN as USER_NAME,'PERAWAT' as USER_EMR,PERAWAT.FMPPERAWAT_ID as USER_ID,PERAWAT.KD_CABANG as KD_CABANG"
    q +=" FROM PERAWAT"
    q +=" WHERE PERAWAT.FMPPERAWAT_ID=%s"
    # print(q)
    result = Globals().getDataQuery(q, [username,username])
    if len(result) != 0:
        hashed = result[0]['PW'].encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), hashed):
            return result[0]

        else:
            return None

    else:
        return None

def createHashPass(password):
    return bcrypt.hashpw(password.encode("utf-8") , bcrypt.gensalt()).decode("utf-8") 


def getCabang(request):
    cari='%'+request.GET['q']+'%'
    q = " Select CABANG_ID as id,(CABANG_ID+'_'+PERUSAHAAN) as text from CABANG where PERUSAHAAN LIKE %s "
    # pprint(proc_param)
    result = Globals().getDataQuery(q, [cari])
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")

def getUser(request):
    user_id = request.GET['cabang']
    if 'cabang' in request.GET:
        cari='%'+request.GET['q']+'%'
        q = " SELECT DOKTER.FMDDOKTER_ID as id,(DOKTER.FMDDOKTER_ID+'_'+DOKTER.FMDDOKTERN) as text FROM DOKTER "
        q +=" WHERE DOKTER.KD_CABANG=%s AND DOKTER.FMDDOKTERN LIKE %s"
        q +=" UNION "
        q +=" SELECT PERAWAT.FMPPERAWAT_ID as id,(PERAWAT.FMPPERAWAT_ID+'_'+PERAWAT.FMPPERAWATN) as text FROM PERAWAT"
        q +=" WHERE PERAWAT.KD_CABANG=%s AND PERAWAT.FMPPERAWATN LIKE %s"
        # pprint(proc_param)
        result = Globals().getDataQuery(q, [user_id,cari,user_id,cari])
    else:
        result=[]
    json_data = json.dumps(result, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type="application/json")