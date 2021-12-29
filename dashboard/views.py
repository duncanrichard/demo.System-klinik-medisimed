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
	# Check Session
	if 'userauth' in request.session:
		is_login = request.session['userauth']
		user_priv = request.session['user_priv']

	else:
		is_login = False

	# Code
	if(is_login):
		navbars = Globals().getNavbars(user_priv, 'IMMODERMA', None)
		menubars = Globals().getMenubars(user_priv, 'IMMODERMA', None, '0')
		menubarsChild = Globals().getMenubars(user_priv, 'IMMODERMA', None, '1')
		menubarCount = len(menubars)

		response = render(request, 'dashboard/home.html', {
			'url': 'rawat_inap', 
			'navbars': navbars, 
			'menubars': menubars,
			'menubarsChild': menubarsChild,
			'menubarsType': 2,
			'count_': menubarCount,
			'list_': Globals().getSeparator(menubarCount),
		})
		
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')