from IMMODERMA.globals import Globals
from IMMODERMA.environment import env

import os
import json
from pprint import pprint
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder

def dashboard(request):
	# Code
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']
		if 'kdCabang' in request.GET:
			request.session['kdCabang'] = request.GET['kdCabang']
			kdCabang = request.session['kdCabang']
			q = "select * from CABANG  WHERE CABANG_ID=%s "
			cabang = Globals().getDataQuery(q, [kdCabang])
			request.session['kota_cabang'] = cabang[0]['KOTA']
			request.session['nama_cabang'] = cabang[0]['PERUSAHAAN']
			request.session['alamat_cabang'] = cabang[0]['ALAMAT1']

		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', None)
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', None, '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', None, '1')
		menubarCount = len(menubars)

		response = render(request, 'dashboard/home.html', {
			# 'url': 'rawat_inap', 
			'navbars': navbars, 
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			#'user_id' : request.session['user_id']
		})
		
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
		

	else:
		return redirect('/login')

def cabang(request):
	# Code
	if(Globals().isLogin(request)):
		user_priv = request.session['user_priv']
		user_privelege = request.session['user_priv']

		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', None)
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', None, '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', None, '1')
		menubarCount = len(menubars)

		response = render(request, 'dashboard/cabang.html', {
			# 'url': 'rawat_inap', 
			'navbars': navbars, 
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 1,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
			#'user_id' : request.session['user_id']
		})
		
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
		

	else:
		return redirect('/login')