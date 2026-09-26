class env:
    DB_ENGINE = 'sql_server.pyodbc'

    DB_NAME = 'IMMO'
    DB_NAME_2 = ''

    DB_HOST = 'localhost'
    PORT = '1433'

    USER = 'sa'
    PASSWORD = 'richard_98'

    OPTIONS = {
        'driver': 'ODBC Driver 17 for SQL Server',
        'trusted_connection': 'yes'
    }