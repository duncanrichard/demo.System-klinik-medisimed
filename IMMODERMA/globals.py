import os
import json
import locale
import datetime
import simplejson
from .environment import env
from .settings import DATABASES
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection, connections, ProgrammingError, DatabaseError
from pyreportjasper import JasperPy

class Globals:
	def generateReportDB(self, input_filename, output_filename, user,param={}, db='', list_format=["pdf"]):
		ts = datetime.datetime.now()
		date = ts.strftime("%d_%m_%Y_%I_%M_%S_%f")
		user = "_" + user + "_"

		reportNameFile = output_filename + user + date
		in_file = os.path.abspath(os.path.dirname(__name__)) + '/jrxml/'+input_filename
		out_file = os.path.abspath(os.path.dirname(__name__)) + '/static/report/'+reportNameFile
		
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
			jdbc_dir = getattr(env, 'JDBC_DIR', os.path.abspath(os.path.dirname(__name__)) + '/jdbc')

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
			jdbc_dir = getattr(env, 'JDBC_DIR', os.path.abspath(os.path.dirname(__name__)) + '/jdbc')

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

	def getDataQuery(self, query, params = [], db = 'main'):
		if db == 'main':
			cursor = connection.cursor()
		elif db == 'antrian':
			cursor = connections['antrian'].cursor()
		else:
			cursor = connections['epublic'].cursor()

		cursor.execute(query, params)
		result = self.dictfetchall(cursor)
		cursor.close()

		return result

	def getDataSP(self, query, params = [], db = 'main', setIndex = 1):
		if db == 'main':
			cursor = connection.cursor()
		elif db == 'antrian':
			cursor = connections['antrian'].cursor()
		else:
			cursor = connections['epublic'].cursor()

		cursor.execute(query, params)

		result = self.fetchResult(cursor,setIndex)
		
		cursor.close()
		return result

	def executeQuery(self, query, params = [], db = 'main'):
		if db == 'main':
			cursor = connection.cursor()
		elif db == 'antrian':
			cursor = connections['antrian'].cursor()
		else:
			cursor = connections['epublic'].cursor()

		cursor.execute(query, params)
		cursor.close()

	def getNavbars(self, user_priv, modul, submodul = None):
		cursor = connection.cursor()

		if submodul == None:	
			qnavbar = "SELECT * FROM PROPERTIES_NAVBAR WHERE modul = '"+modul+"' AND submodul IS NULL AND id IN "
			qnavbar += "(SELECT NAVBAR_PRIV FROM PRIVILEGE_NAVBAR WHERE USER_PRIV = '"+user_priv+"' AND modul = '"+modul+"' AND submodul IS NULL) "
		else:
			qnavbar = "SELECT * FROM PROPERTIES_NAVBAR WHERE modul = '"+modul+"' AND submodul = '"+submodul+"' AND id IN "
			qnavbar += "(SELECT NAVBAR_PRIV FROM PRIVILEGE_NAVBAR WHERE USER_PRIV = '"+user_priv+"' AND modul = '"+modul+"' AND submodul = '"+submodul+"') "

		qnavbar += "ORDER BY nav_order"
		cursor.execute(qnavbar)
		return self.dictfetchall(cursor)

	def getMenubars(self, user_priv, modul, submodul = None, level = 'default'):
		cursor = connection.cursor()

		if submodul == None:	
			qmenubar = "SELECT * FROM PROPERTIES_MENUBAR WHERE modul = '"+modul+"' AND submodul IS NULL "

			if level != 'default':
				qmenubar += "AND level = " + level

			qmenubar += "AND id IN (SELECT MENUBAR_PRIV FROM PRIVILEGE_MENUBAR WHERE USER_PRIV = '"+user_priv+"' AND modul = '"+modul+"' AND submodul IS NULL) "
		else:
			qmenubar = "SELECT * FROM PROPERTIES_MENUBAR WHERE modul = '"+modul+"' AND submodul = '"+submodul+"' "

			if level != 'default':
				qmenubar += "AND level = " + level

			qmenubar += "AND id IN (SELECT MENUBAR_PRIV FROM PRIVILEGE_MENUBAR WHERE USER_PRIV = '"+user_priv+"' AND modul = '"+modul+"' AND submodul = '"+submodul+"') "

		qmenubar += "ORDER BY menu_order"
		cursor.execute(qmenubar)
		return self.dictfetchall(cursor)

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
		if not os.path.exists(os.path.abspath(os.path.dirname(__name__)) + '/LOG/'+folder):
			os.makedirs(os.path.abspath(os.path.dirname(__name__)) + '/LOG/'+folder)

		files = os.path.abspath(os.path.dirname(__name__)) + '/LOG/'+folder+'/'+file_name
		
		if os.path.exists(files) == False:
			f = open(files, "w+")
		else:
			f = open(files, "a+")

		tanggal = self.tanggalIndo(datetime.datetime.now().strftime('%Y-%m-%d'))
		jam = str(datetime.datetime.now().strftime('%H:%M:%S'))

		jsonData = json.dumps(self.generateData(data), cls=DjangoJSONEncoder)

		f.write('==============================================' + "\n")
		f.write("USER ID : " + user['user_id'] + ", NAMA : " + user['user_name'] + ", USER PRIV : " + user['user_priv'] + "\n")
		f.write("TANGGAL : " + tanggal +", JAM : " + jam + "\n")
		f.write('==============================================' + "\n")
		f.write(simplejson.dumps(simplejson.loads(jsonData), indent=2))
		f.write('\n==============================================' + "\r")
		f.write('==============================================' + "\r\n")

		f.close()

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
		# Privilege = getData("select distinct USER_PRIV from USERSPRIV;")
		Privilege = self.getDataQuery("select distinct USER_PRIV from USERSPRIV;")

		if 'userauth' in request.session:
			is_login = request.session['userauth']
			# if(request.session['user_priv'] not in PRIV['USER_PRIV']):
			if(not any(user['USER_PRIV'] == request.session['user_priv'] for user in Privilege)):
				is_login = False
		else:
			is_login = False
		return is_login

	def check_access(self, user_priv, id_navbar, modul, submodul = None):
		if submodul is None:
			qnavbar = "SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+user_priv+"' AND B.modul = '"+ modul +"' AND B.submodul IS NULL AND B.id = '"+ id_navbar +"'"
		else:
			qnavbar = "SELECT * FROM PRIVILEGE_NAVBAR AS A RIGHT JOIN PROPERTIES_NAVBAR AS B ON A.NAVBAR_PRIV = B.id WHERE A.USER_PRIV = '"+user_priv+"' AND B.modul = '"+ modul +"' AND B.submodul = '"+ submodul +"' AND B.id = '"+ id_navbar +"'"
		result = self.getData(qnavbar)

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
