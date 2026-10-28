"""Legacy example only.

Use ``.env.example`` and ``IMMODERMA_*`` environment variables for new
installations. This file intentionally contains no credentials.
"""


class env:
    DB_ENGINE = "mssql"
    DB_NAME = "IMMO"
    DB_NAME_2 = ""
    DB_HOST = "127.0.0.1"
    PORT = "1433"
    USER = ""
    PASSWORD = ""
    OPTIONS = {"driver": "ODBC Driver 18 for SQL Server"}
