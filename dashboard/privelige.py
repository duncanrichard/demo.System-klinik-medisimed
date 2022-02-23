from django.template.response import TemplateResponse
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db import connection
# from .form import PabrikanForm, SupplierForm
import datetime
# from datetime import datetime
import json
from django.core import serializers
from django.db import transaction
from django.db import IntegrityError
# from privilege.models import PrivilegeModul
from IMMODERMA.globals import Globals
from pprint import pprint

def dashboard(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):
		response = render(request, 'privilege/home/home.html', {})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def menu(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):
		q1 = "select id,name,icon,url from (select * from PRIVILEGE_MODUL where USER_PRIV = 'FISIOTERAPI') as x right join PROPERTIES_MENU on x.MENU_PRIV=id where x.MENU_PRIV is null;"
		q2 = "select id,name,icon,url from PRIVILEGE_MODUL inner join PROPERTIES_MENU on MENU_PRIV=id and USER_PRIV = 'FISIOTERAPI';"
		q3 = "select distinct USER_PRIV from USERSPRIV;"

		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)

		response = render(request, 'privilege/menus/base.html', {"selecteds": selected, "unselecteds":unselected, "user_privs":user_priv})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def menu_priv(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):
		q1 = "select id,name,icon,url from (select * from PRIVILEGE_MODUL where USER_PRIV = '"+request.GET['menu_user']+"') as x right join PROPERTIES_MENU on x.MENU_PRIV=id where x.MENU_PRIV is null;"
		q2 = "select id,name,icon,url from PRIVILEGE_MODUL inner join PROPERTIES_MENU on MENU_PRIV=id and USER_PRIV = '"+request.GET['menu_user']+"';"
		q3 = "select distinct USER_PRIV from USERSPRIV;"

		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)

		# datane.get('selecteds').append(selected)
		response = json.dumps({'selecteds':selected, 
							 'unselecteds':unselected,
							 'user_priv':user_priv
							})
		
		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def menu_post(request):
	if(Globals().isLogin(request)):
		PrivilegeModul.objects.filter(user_priv=request.POST['priv']).delete()

		for rule in request.POST.getlist('rules[]'):
			data = PrivilegeModul(user_priv=request.POST['priv'],menu_priv=rule)
			data.save()

		response = json.dumps({
			"success": True,
			"message": "success",
		})

		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def user(request):
	if(Globals().isLogin(request)):
		response = render(request, 'privilege/home/home.html', {})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def navbars(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):

		q3 = "select distinct USER_PRIV from USERSPRIV;"
		q4 = "select name, [table] from PROPERTIES_MENU;"
		q5 = "SELECT distinct submodul FROM PROPERTIES_NAVBAR where submodul is not null;"

		# unselected = getData(q1)
		# selected = getData(q2)

		unselected = []
		selected = []

		user_priv =Globals().getDataQuery(q3) 
		modul_priv=Globals().getDataQuery(q4)
		submodul_priv=Globals().getDataQuery(q5)

		response = render(request, 'privilege/navbars/base.html', {"selecteds": selected, "unselecteds":unselected, "user_privs":user_priv, "modul_privs":modul_priv, "submodul_privs":[]})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def navbars_priv(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):

		q1 = "SELECT B.id, B.name, B.parent, B.link, B.submodul FROM (SELECT B.id, B.name, B.parent, B.link, A.NAVBAR_PRIV FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"') AS A RIGHT JOIN (SELECT * FROM PROPERTIES_NAVBAR WHERE modul = '"+request.GET['modul_priv']+"') as B ON A.NAVBAR_PRIV = B.id WHERE A.NAVBAR_PRIV IS NULL AND B.submodul IS NULL"
		q2 = "SELECT B.id, B.name, B.parent, B.link, A.NAVBAR_PRIV, B.submodul FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"'  AND B.submodul is null;"
		q3 = "select distinct USER_PRIV from USERSPRIV;"
		q5 = "SELECT distinct submodul FROM PROPERTIES_NAVBAR where submodul is not null and modul = '"+request.GET['modul_priv']+"';"

		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)
		submodul_priv=Globals().getDataQuery(q5)


		response = json.dumps({'selecteds':selected, 
							 'unselecteds':unselected,
							 'user_priv':user_priv,
							 'submodul_privs':submodul_priv
							})
		
		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def navbars_post(request):

	if(Globals().isLogin(request)):
		delete_query = "DELETE FROM PRIVILEGE_NAVBAR WHERE USER_PRIV = '"+request.POST['user_priv']+"' AND modul = '"+request.POST['modul_priv']+"' AND submodul IS NULL"
		Globals().executeQuery(delete_query)

		for rule in request.POST.getlist('rules[]'):
			query = "insert into PRIVILEGE_NAVBAR (USER_PRIV, NAVBAR_PRIV, modul) values ('"+request.POST['user_priv']+"','"+rule+"','"+request.POST['modul_priv']+"');"
			Globals().executeQuery(query)

		response = json.dumps({
			"success": True,
			"message": "success",
		})

		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def subnavbars_priv(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):

		q1 = "SELECT B.id, B.name, B.parent, B.link FROM (SELECT B.id, B.name, B.parent, B.link, A.NAVBAR_PRIV FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"' AND B.submodul = '"+request.GET['submodul_priv']+"') AS A RIGHT JOIN (SELECT * FROM PROPERTIES_NAVBAR WHERE modul = '"+request.GET['modul_priv']+"' AND submodul = '"+request.GET['submodul_priv']+"') as B ON A.NAVBAR_PRIV = B.id WHERE A.NAVBAR_PRIV IS NULL"
		q2 = "SELECT B.id, B.name, B.parent, B.link, A.NAVBAR_PRIV FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"' AND B.submodul = '"+request.GET['submodul_priv']+"';"
		q3 = "select distinct USER_PRIV from USERSPRIV;"
		q5 = "SELECT distinct submodul FROM PROPERTIES_NAVBAR where submodul is not null and modul = '"+request.GET['modul_priv']+"';"

		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)
		submodul_priv=Globals().getDataQuery(q5)

		response = json.dumps({'selecteds':selected, 
							 'unselecteds':unselected,
							 'user_priv':user_priv,
							 'submodul_privs':submodul_priv
							})
		
		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def subnavbars_post(request):
	if(Globals().isLogin(request)):

		delete_query = "DELETE FROM PRIVILEGE_NAVBAR WHERE USER_PRIV = '"+request.POST['user_priv']+"' AND modul = '"+request.POST['modul_priv']+"' AND submodul = '"+request.POST['submodul_priv']+"'"
		Globals().executeQuery(delete_query)

		for rule in request.POST.getlist('rules[]'):
			query = "insert into PRIVILEGE_NAVBAR (USER_PRIV, NAVBAR_PRIV, modul, submodul) values ('"+request.POST['user_priv']+"','"+rule+"','"+request.POST['modul_priv']+"','"+request.POST['submodul_priv']+"');"
			Globals().executeQuery(query)

		response = json.dumps({
			"success": True,
			"message": "success",
		})

		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def actionbars(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):

		q1 = "SELECT B.name, B.parent, B.link FROM (SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = 'FISIOTERAPI' AND B.modul = 'IMMODERMA') AS A RIGHT JOIN (SELECT * FROM PROPERTIES_NAVBAR WHERE modul = 'IMMODERMA') as B ON A.NAVBAR_PRIV = B.id WHERE A.NAVBAR_PRIV IS NULL"
		q2 = "SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = 'FISIOTERAPI' AND B.modul = 'IMMODERMA';"
		q3 = "select distinct USER_PRIV from USERSPRIV;"
		q4 = "select name, [table] from PROPERTIES_MENU;"

		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)
		modul_priv=Globals().getDataQuery(q4)

		response = render(request, 'privilege/navbars/base.html', {"selecteds": selected, "unselecteds":unselected, "user_privs":user_priv, "modul_privs":modul_priv})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def actionbars_priv(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):

		q1 = "SELECT B.id, B.name, B.parent, B.link FROM (SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"') AS A RIGHT JOIN (SELECT * FROM PROPERTIES_NAVBAR WHERE modul = '"+request.GET['modul_priv']+"') as B ON A.NAVBAR_PRIV = B.id WHERE A.NAVBAR_PRIV IS NULL"
		q2 = "SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"';"
		q3 = "select distinct USER_PRIV from USERSPRIV;"


		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)

		response = json.dumps({'selecteds':selected, 
							 'unselecteds':unselected,
							 'user_priv':user_priv
							})
		
		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def actionbars_post(request):
	if(Globals().isLogin(request)):

		delete_query = "DELETE FROM PRIVILEGE_NAVBAR WHERE USER_PRIV = '"+request.POST['user_priv']+"'"
		Globals().executeQuery(delete_query)

		for rule in request.POST.getlist('rules[]'):
			query = "insert into PRIVILEGE_NAVBAR (USER_PRIV, NAVBAR_PRIV) values ('"+request.POST['user_priv']+"','"+rule+"');"
			Globals().executeQuery(query)

		response = json.dumps({
			"success": True,
			"message": "success",
		})

		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def menubars(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):
		user_privelege = request.session['user_priv']

		q1 = "SELECT B.name, B.parent, B.link FROM (SELECT B.id, B.name, B.parent, B.link, A.MENUBAR_PRIV FROM PRIVILEGE_MENUBAR AS A RIGHT JOIN PROPERTIES_MENUBAR AS B ON A.MENUBAR_PRIV = B.id WHERE A.USER_PRIV = 'FISIOTERAPI' AND B.modul = 'IMMODERMA' AND B.submodul is null) AS A RIGHT JOIN (SELECT * FROM PROPERTIES_MENUBAR WHERE modul = 'IMMODERMA' AND submodul is null) as B ON A.MENUBAR_PRIV = B.id WHERE A.MENUBAR_PRIV IS NULL"
		q2 = "SELECT B.id, B.name, B.parent, B.link, A.MENUBAR_PRIV FROM PRIVILEGE_MENUBAR AS A RIGHT JOIN PROPERTIES_MENUBAR AS B ON A.MENUBAR_PRIV = B.id WHERE A.USER_PRIV = 'FISIOTERAPI' AND B.modul = 'IMMODERMA' AND B.submodul is null;"
		q3 = "select distinct USER_PRIV from USERSPRIV;"
		q4 = "select name, [table] from PROPERTIES_MENU;"
		q5 = "SELECT distinct submodul FROM PROPERTIES_MENUBAR where submodul is not null;"

		unselected = []
		selected = []

		user_priv =Globals().getDataQuery(q3) 
		modul_priv=Globals().getDataQuery(q4)
		submodul_priv=Globals().getDataQuery(q5)

		response = render(request, 'privilege/menubars/base.html', {"selecteds": selected, "unselecteds":unselected, "user_privs":user_priv, "modul_privs":modul_priv, "submodul_privs":[],'user_id':user_privelege})
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		return response
	else:
		return redirect('/login')

def menubars_priv(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):

		q1 = "SELECT B.id, B.name, B.parent, B.link FROM (SELECT B.id, B.name, B.parent, B.link, A.MENUBAR_PRIV FROM PRIVILEGE_MENUBAR AS A RIGHT JOIN PROPERTIES_MENUBAR AS B ON A.MENUBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"' AND B.submodul is null) AS A RIGHT JOIN (SELECT * FROM PROPERTIES_MENUBAR WHERE modul = '"+request.GET['modul_priv']+"' AND submodul is null) as B ON A.MENUBAR_PRIV = B.id WHERE A.MENUBAR_PRIV IS NULL"
		q2 = "SELECT B.id, B.name, B.parent, B.link, A.MENUBAR_PRIV FROM PRIVILEGE_MENUBAR AS A RIGHT JOIN PROPERTIES_MENUBAR AS B ON A.MENUBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"' AND B.submodul is null;"
		q3 = "select distinct USER_PRIV from USERSPRIV;"

		q5 = "SELECT distinct submodul FROM PROPERTIES_MENUBAR where submodul is not null"

		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)
		submodul_priv=Globals().getDataQuery(q5)
		
		response = json.dumps({'selecteds':selected, 
							 'unselecteds':unselected,
							 'user_priv':user_priv,
							 'submodul_privs':submodul_priv
							})
		
		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def submenubars_priv(request):
	# Check Session
	# Code
	if(Globals().isLogin(request)):

		q1 = "SELECT B.id, B.name, B.parent, B.link FROM (SELECT B.id, B.name, B.parent, B.link, A.MENUBAR_PRIV FROM PRIVILEGE_MENUBAR AS A RIGHT JOIN PROPERTIES_MENUBAR AS B ON A.MENUBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"' AND B.submodul = '"+request.GET['submodul_priv']+"') AS A RIGHT JOIN (SELECT * FROM PROPERTIES_MENUBAR WHERE modul = '"+request.GET['modul_priv']+"' AND submodul = '"+request.GET['submodul_priv']+"') as B ON A.MENUBAR_PRIV = B.id WHERE A.MENUBAR_PRIV IS NULL"
		q2 = "SELECT B.id, B.name, B.parent, B.link, A.MENUBAR_PRIV FROM PRIVILEGE_MENUBAR AS A RIGHT JOIN PROPERTIES_MENUBAR AS B ON A.MENUBAR_PRIV = B.id WHERE A.USER_PRIV = '"+request.GET['user_priv']+"' AND B.modul = '"+request.GET['modul_priv']+"' AND B.submodul = '"+request.GET['submodul_priv']+"';"
		q3 = "select distinct USER_PRIV from USERSPRIV;"

		q5 = "SELECT distinct submodul FROM PROPERTIES_MENUBAR where submodul is not null and modul = '"+request.GET['modul_priv']+"';"

		
		unselected =Globals().getDataQuery(q1) 
		selected=Globals().getDataQuery(q2)
		user_priv=Globals().getDataQuery(q3)
		submodul_priv=Globals().getDataQuery(q5)

		response = json.dumps({'selecteds':selected, 
							 'unselecteds':unselected,
							 'user_priv':user_priv,
							 'submodul_privs':submodul_priv
							})
		
		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def menubars_post(request):
	if(Globals().isLogin(request)):

		delete_query = "DELETE FROM PRIVILEGE_MENUBAR WHERE USER_PRIV = '"+request.POST['user_priv']+"' AND modul = '"+request.POST['modul_priv']+"' AND submodul IS NULL"
		Globals().executeQuery(delete_query)

		for rule in request.POST.getlist('rules[]'):
			query = "insert into PRIVILEGE_MENUBAR (USER_PRIV, MENUBAR_PRIV, modul) values ('"+request.POST['user_priv']+"','"+rule+"','"+request.POST['modul_priv']+"');"
			Globals().executeQuery(query)

		response = json.dumps({
			"success": True,
			"message": "success",
		})

		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')

def submenubars_post(request):
	if(Globals().isLogin(request)):

		delete_query = "DELETE FROM PRIVILEGE_MENUBAR WHERE USER_PRIV = '"+request.POST['user_priv']+"' AND modul = '"+request.POST['modul_priv']+"' AND submodul = '"+request.POST['submodul_priv']+"'"
		Globals().executeQuery(delete_query)

		for rule in request.POST.getlist('rules[]'):
			# print("hasil "+rule)
			query = "insert into PRIVILEGE_MENUBAR (USER_PRIV, MENUBAR_PRIV, modul, submodul) values ('"+request.POST['user_priv']+"','"+rule+"','"+request.POST['modul_priv']+"','"+request.POST['submodul_priv']+"');"
			Globals().executeQuery(query)

		response = json.dumps({
			"success": True,
			"message": "success",
		})

		return HttpResponse(response, content_type="application/json")
	else:
		return redirect('/login')