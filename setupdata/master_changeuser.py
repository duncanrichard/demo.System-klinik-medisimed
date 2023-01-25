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

def master_changeuser(request):
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', "master_changeuser")
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', "master_changeuser", '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', "master_changeuser", '1')
		menubarCount = len(menubars)
		response = render(request, 'setupdata/changepassword/changepassword.html', {
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

def changepassword(request):
	user_id = request.session['user_id']
	password = request.GET['password']
	newpassword = request.GET['newpassword']
	user = checkLogin(user_id, password)
	print ('user')
	print (user)
	if user != None:
		q = "select top 1 * from USERSPRIV where USER_ID=%s"
		result = Globals().getDataQuery(q, [user_id])
		if len(result) != 0:
			kode_userpriv = user_id
			nama_userpriv = result[0]['USER_NAME']
			password_userpriv= newpassword
			password_userpriv =createHashPass(password_userpriv)
			privelege_userpriv= result[0]['USER_PRIV']
			kode_nip = result[0]['nip']
			no_telepon = result[0]['phone']
			aktif = result[0]['AKTIF']
			cabang_id = request.session['kdCabang']
			status_aud = 'A'

			try:
				q = "EXEC MST_AUD_USERPRIV %s, %s, %s, %s, %s, %s, %s, %s, %s"
				result = Globals().getDataSP(q, [kode_userpriv, nama_userpriv,password_userpriv,privelege_userpriv,kode_nip,no_telepon,aktif,cabang_id,status_aud])
				json_data = json.dumps(result, cls=DjangoJSONEncoder)
				return HttpResponse(json_data, content_type="application/json")

			except ValueError:
				print('coba')
	else :
		result = [{'STATUS': 'GAGAL','STATE':'UPDATE','USERSPRIV_ID':user_id, 'ERROR_MESSAGE': 'Username atau password Anda salah'}]
		json_data = json.dumps(result, cls=DjangoJSONEncoder)
		return HttpResponse(json_data, content_type="application/json")

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
  
