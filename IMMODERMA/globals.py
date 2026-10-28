import os
import json
import locale
import datetime
from pathlib import Path

import simplejson
from .config import env
from .settings import BASE_DIR, DATABASES
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection, connections, ProgrammingError, DatabaseError
# from datetime import datetime as DTime
# # bpjs
# import requests
# import hashlib
# import base64
# import urllib
# import hmac

# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# import lzstring

class Globals:
	def generateReportDB(self, input_filename, output_filename, user, param=None, db='', list_format=None):
		from pyreportjasper import JasperPy

		param = param or {}
		list_format = list_format or ["pdf"]
		ts = datetime.datetime.now()
		date = ts.strftime("%d_%m_%Y_%I_%M_%S_%f")
		user = "_" + user + "_"

		reportNameFile = output_filename + user + date
		in_file = str(Path(BASE_DIR) / 'jrxml' / input_filename)
		out_file = str(Path(BASE_DIR) / 'static' / 'report' / reportNameFile)
		
		if db == '' :
			db_profile = 'default'
		else :
			db_profile = db

		username = DATABASES[db_profile]['USER']
		password = DATABASES[db_profile]['PASSWORD']
		host = DATABASES[db_profile]['HOST']
		database = DATABASES[db_profile]['NAME']
		port = DATABASES[db_profile]['PORT']	

		if getattr(env, 'JDBC_MODE', 'WINDOWS') == 'WINDOWS':
			jdbc_driver = getattr(env, 'JDBC_DRIVER', 'com.microsoft.sqlserver.jdbc.SQLServerDriver')
			jdbc_url = getattr(env, 'JDBC_URL', 'jdbc:sqlserver://'+host+':'+port+';databaseName='+database)
			jdbc_dir = getattr(env, 'JDBC_DIR', '') or str(Path(BASE_DIR) / 'jdbc')

			con = {
				'driver': 'generic',
				'jdbc_driver' : jdbc_driver,
				'jdbc_url' : jdbc_url,
				'jdbc_dir' : jdbc_dir,
				'username': username,
				'password': password,
				'host': host,
				'database': database,
				'port': port
			}
		else:
			jdbc_driver = getattr(env, 'JDBC_DRIVER', 'net.sourceforge.jtds.jdbc.Driver')
			jdbc_url = getattr(env, 'JDBC_URL', 'jdbc:jtds:sqlserver://'+host+':'+port+'/'+database+';user='+username+';password='+password)
			jdbc_dir = getattr(env, 'JDBC_DIR', '') or str(Path(BASE_DIR) / 'jdbc')

			con = {
				'driver': 'generic',
				'jdbc_driver' : jdbc_driver,
				'jdbc_url' : jdbc_url,
				'jdbc_dir' : jdbc_dir,
				'username': username,
				'password': password,
				'host': host,
				'database': database,
				'port': port
			}

		jasper = JasperPy()
		if(not os.path.exists(in_file[0:-5]+'jasper')):
			jasper.compile(in_file)

		jasper.process(
			in_file[0:-5]+'jasper',
	    	output_file = out_file,
	    	format_list = list_format,
	        parameters = param,
	        db_connection = con,
	        locale = 'en_US'
		)

		response = {}
		for file_format in list_format:
			response[file_format] = '/static/report/' + reportNameFile + "." + file_format

		return response

	def dictfetchall(self,cursor):
		# "Return all rows from a cursor as a dict"
		fetchdata = cursor.fetchall()
		if(cursor.description):
			columns = [col[0] for col in cursor.description]
			return [
				dict(zip(columns, row))
				for row in fetchdata
			]
		else:
			return fetchdata

	def _connection(self, db):
		if db == 'main':
			return connection
		return connections[db]

	def getDataQuery(self, query, params=None, db='main'):
		with self._connection(db).cursor() as cursor:
			cursor.execute(query, params or [])
			return self.dictfetchall(cursor)

	def getData(self,query, param = None,setIndex = 1):
		cursor = connection.cursor()
		if( param is not None):
			cursor.execute(query, param)
		else:
			cursor.execute(query)
		results = None
		i = 0
		while results is None :
			try:
				results = self.dictfetchall(cursor)
				
				i+= 1
				if(i == setIndex):
					break
				else :
					results = None
					cursor.nextset()
				
			except ProgrammingError as e:
				cursor.nextset()
		# pprint(results)
		cursor.close()
		return results

	def getDataSP(self, query, params=None, db='main', setIndex=1):
		with self._connection(db).cursor() as cursor:
			cursor.execute(query, params or [])
			return self.fetchResult(cursor, setIndex)

	def executeQuery(self, query, params=None, db='main'):
		with self._connection(db).cursor() as cursor:
			cursor.execute(query, params or [])

	def getNavbars(self, user_priv, modul, submodul = None):
		if submodul == None:	
			qnavbar = "SELECT * FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul IS NULL AND id IN "
			qnavbar += "(SELECT NAVBAR_PRIV FROM PRIVILEGE_NAVBAR WHERE USER_PRIV = %s AND modul = %s AND submodul IS NULL) "
			params = [modul, user_priv, modul]
		else:
			qnavbar = "SELECT * FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul = %s AND id IN "
			qnavbar += "(SELECT NAVBAR_PRIV FROM PRIVILEGE_NAVBAR WHERE USER_PRIV = %s AND modul = %s AND submodul = %s) "
			params = [modul, submodul, user_priv, modul, submodul]

		qnavbar += "ORDER BY nav_order"
		return self.getDataQuery(qnavbar, params)

	def getMenubars(self, user_priv, modul, submodul = None, level = 'default'):
		if submodul == None:	
			qmenubar = "SELECT * FROM PROPERTIES_MENUBAR WHERE modul = %s AND submodul IS NULL "
			params = [modul]
			if level != 'default':
				qmenubar += "AND level = %s "
				params.append(level)
			qmenubar += "AND id IN (SELECT MENUBAR_PRIV FROM PRIVILEGE_MENUBAR WHERE USER_PRIV = %s AND modul = %s AND submodul IS NULL) "
			params.extend([user_priv, modul])
		else:
			qmenubar = "SELECT * FROM PROPERTIES_MENUBAR WHERE modul = %s AND submodul = %s "
			params = [modul, submodul]
			if level != 'default':
				qmenubar += "AND level = %s "
				params.append(level)
			qmenubar += "AND id IN (SELECT MENUBAR_PRIV FROM PRIVILEGE_MENUBAR WHERE USER_PRIV = %s AND modul = %s AND submodul = %s) "
			params.extend([user_priv, modul, submodul])

		qmenubar += "ORDER BY menu_order"
		return self.getDataQuery(qmenubar, params)

	def getSeparator(self, n):
		separator = []
		n += 1
		counter = 7
		
		for x in range(n):
			if x+1 == counter:
				separator.append(counter)
				counter += 6

		return separator

	def create_log(self, file_name, folder, data, user):
		log_dir = Path(BASE_DIR) / 'LOG' / folder
		log_dir.mkdir(parents=True, exist_ok=True)
		file_path = log_dir / file_name

		tanggal = self.tanggalIndo(datetime.datetime.now().strftime('%Y-%m-%d'))
		jam = str(datetime.datetime.now().strftime('%H:%M:%S'))

		jsonData = json.dumps(self.generateData(data), cls=DjangoJSONEncoder)

		with file_path.open("a", encoding="utf-8") as log_file:
			log_file.write('==============================================\n')
			log_file.write("USER ID : " + user['user_id'] + ", NAMA : " + user['user_name'] + ", USER PRIV : " + user['user_priv'] + "\n")
			log_file.write("TANGGAL : " + tanggal + ", JAM : " + jam + "\n")
			log_file.write('==============================================\n')
			log_file.write(simplejson.dumps(simplejson.loads(jsonData), indent=2))
			log_file.write('\n==============================================\r')
			log_file.write('==============================================\r\n')

	def generateData(self, data):
		result = []
		jsonData = []

		for x in data:
			cursor = connection.cursor()
			cursor.execute(x['query'])
			result.append(self.dictfetchall(cursor))

		i = 0
		for y in data:
			jsonData.append({
				"query": y['query'],
				"data": result[i]
			})

			i+=1

		return jsonData


	def tanggalIndo(self, date):
		tgl = date.split("-")
		tanggal = tgl[2]
		bulan = tgl[1]
		tahun = tgl[0]

		if (bulan == '01'):
			bulan = ' Januari '
		elif (bulan == '02'):
			bulan = ' Februari '
		elif (bulan == '03'):
			bulan = ' Maret '
		elif (bulan == '04'):
			bulan = ' April '
		elif (bulan == '05'):
			bulan = ' Mei '
		elif (bulan == '06'):
			bulan = ' Juni '
		elif (bulan == '07'):
			bulan = ' Juli '
		elif (bulan == '08'):
			bulan = ' Agustus '
		elif (bulan == '09'):
			bulan = ' September '
		elif (bulan == '10'):
			bulan = ' Oktober '
		elif (bulan == '11'):
			bulan = ' November '
		else:
			bulan = ' Desember '

		return tanggal + bulan + tahun

	
	def isLogin(self,request):
		if not request.session.get('userauth'):
			return False
		user_priv = request.session.get('user_priv')
		if not user_priv:
			return False
		privileges = self.getDataQuery(
			"select distinct USER_PRIV from USERSPRIV;"
		)
		return any(user['USER_PRIV'] == user_priv for user in privileges)

	def check_access(self, user_priv, id_navbar, modul, submodul = None):
		if submodul is None:
			qnavbar = "SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = %s AND B.modul = %s AND B.submodul IS NULL AND B.id = %s"
			params = [user_priv, modul, id_navbar]
		else:
			qnavbar = "SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = %s AND B.modul = %s AND B.submodul = %s AND B.id = %s"
			params = [user_priv, modul, submodul, id_navbar]
		result = self.getData(qnavbar, params)

		if len(result) > 0:
			return True
		else:
			return False

	def deleteFiles(self, folder = "/static/report/"):
		root_path = os.path.abspath(os.path.dirname(__name__))
		path = root_path + folder
		today = datetime.datetime.today()

		hari = (int(getattr(env, 'HAPUS_FILE_HARI', 30)) + 1)

		if(hari == 0):
			hari = -1

		elif(hari > 0):
			hari = hari * -1

		os.chdir(path)

		for root, directories, files in os.walk(path,topdown=False): 

			for name in files:
				t = os.stat(os.path.join(root, name))[8] 
				filetime = datetime.datetime.fromtimestamp(t) - today

				if filetime.days <= hari:
					split_tup = os.path.splitext(os.path.join(root, name))

					data_extension = ['.pdf', '.xls', '.xlsx', '.html', '.txt', '.log']
					if split_tup[1] in data_extension:
						os.remove(os.path.join(root, name))

			for directory in directories:
				t = os.stat(os.path.join(root, directory))[8] 
				foldertime = datetime.datetime.fromtimestamp(t) - today

				if foldertime.days <= hari:
					os.rmdir(os.path.join(root, directory))
		
		os.chdir(root_path)

	
	def fetchResult(self,cursor,setIndex = 1):
		i = 0
		results = self.dictfetchall(cursor)
		# pprint(results)
		if results is None:
			return None
		else :
			i+= 1
			# print(i)
			# print(setIndex)
			if (i >= setIndex):
				return results
			else:

				while i < setIndex :
					try:
						cursor.nextset()	
						results = self.dictfetchall(cursor)
						i+= 1
					except ProgrammingError as e:
						i+= 1
					except DatabaseError as e:
						i+= 1
					
				return results

	def input(self, method, key, default=None):
		if key not in method:
			return default
		else: 
			return method[key]
		
	
