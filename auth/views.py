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

def login(request):

    # print("==========================")
    # print(createHashPass("BUDI"))
    # print("==========================")
    # print(createHashPass("BUDI"))
    # print("==========================")
    q = "select * from CABANG"
    cabang = Globals().getDataQuery(q)
    kdCabang = cabang[0]['CABANG_ID']
    response = render(request, 'login.html', {'invalid': False })

    # Check Session
    if request.session.get('userauth') == True:
        return redirect('/')

    if request.POST:
        user = checkLogin(str(request.POST['username']), str(request.POST['password']))
        if user != None:
            # cek gudang
            q = "select a.USER_ID, a.USER_PRIV, b.GUDANG, c.NAME_WH, c.BRANCH from USERSPRIV as a left join PRIVILEGE as b on a.USER_PRIV = b.USER_PRIV left join WAREHOUSE as c on b.GUDANG = c.WH_ID where a.USER_ID = %s"
            rows = Globals().getDataQuery(q, [user['USER_ID']])

            request.session.set_expiry(0)
            request.session['userauth'] = True
            request.session['user_priv'] = user['USER_PRIV']
            request.session['user_name'] = user['USER_NAME']
            request.session['user_id'] = user['USER_ID']
            # print (request.session['user_id'])

            # DELETE STATIC FILES
            Globals().deleteFiles()
            Globals().deleteFiles("/DEBUG/")

            if rows[0]['USER_PRIV'] == None or rows[0]['GUDANG'] == None:
                qgudang = "select top 1 * from WAREHOUSE"
                data = Globals().getDataQuery(qgudang)

                request.session['kode_gudang_asli'] = 0
                request.session['kode_gudang'] = data[0]['WH_ID'].strip()
                request.session['nama_gudang'] = data[0]['NAME_WH'].strip()
                request.session['branch'] = kdCabang
            
            else:
                request.session['kode_gudang_asli'] = rows[0]['GUDANG'].strip()
                request.session['kode_gudang'] = rows[0]['GUDANG'].strip()
                request.session['nama_gudang'] = rows[0]['NAME_WH'].strip()
                request.session['branch'] = kdCabang

            request.session['kota_cabang'] = cabang[0]['KOTA']
            request.session['nama_cabang'] = cabang[0]['PERUSAHAAN']
            request.session['alamat_cabang'] = cabang[0]['ALAMAT1']

            qprivilege = 'SELECT TOP 1 * FROM PRIVILEGE WHERE USER_PRIV = %s'
            dataprivilege = Globals().getDataQuery(qprivilege, [request.session['user_priv']])
            request.session['shift_cek'] = dataprivilege[0]['AKTIF']
            request.session['shift_isset'] = '0'
            
            if dataprivilege[0]['SHIFT_AKTIF'] == None:
                request.session['shift_aktif'] = '1'
            else:
                request.session['shift_aktif'] = dataprivilege[0]['SHIFT_AKTIF'].strip()

            qshift = 'SELECT * FROM SHIFT WHERE SHFUSER_PRIV = %s'
            datashift = Globals().getDataQuery(qshift, [request.session['user_priv']])
            request.session['shift_jumlah'] = len(datashift)

            for x in datashift:
                if x['KD_SHIFT'].strip() == request.session['shift_aktif']:
                    request.session['shift_kode'] = x['KD_SHIFT'].strip()
                    request.session['shift_nama'] = x['NAMA_SHIFT'].strip()
                    shift_tanggal = str(x['TGL_SHIFT'])
                    request.session['shift_tanggal'] = shift_tanggal[0:10].strip()
                    request.session['shift_counter'] = x['COUNTER']
                    request.session['shift_next'] = x['SHIFT_NEW'].strip()

            request.session.modified = True
            return redirect('/')

        else:
            response = render(request, 'login.html', {'invalid': True, 'message': 'Username atau password Anda salah'})

    response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
    return response

def logout(request):
	request.session['userauth'] = False
	request.session.clear()
	response = redirect('/login')
	for cookie in request.COOKIES:
		response.delete_cookie(cookie)
	return response

def checkLogin(username, password):
    q = "select top 1 * from USERSPRIV where USER_ID=%s"
    result = Globals().getDataQuery(q, [username])

    if len(result) != 0:
        hashed = result[0]['USER_PASSWORD_HASH'].encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), hashed):
            return result[0]

        else:
            return None

    else:
        return None

def createHashPass(password):
    return bcrypt.hashpw(password.encode("utf-8") , bcrypt.gensalt()).decode("utf-8") 