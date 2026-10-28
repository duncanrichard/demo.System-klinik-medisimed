"""Runtime configuration loaded from environment variables.

The legacy ``IMMODERMA.environment`` module is still accepted as a fallback so
existing installations keep working while production is migrated to explicit
environment variables.
"""

import json
import os


try:
    from .environment import env as _legacy_env
except ImportError:
    _legacy_env = None


def _value(name, default=""):
    environment_name = "IMMODERMA_{}".format(name)
    if environment_name in os.environ:
        return os.environ[environment_name]
    if _legacy_env is not None:
        return getattr(_legacy_env, name, default)
    return default


def _boolean(name, default=False):
    value = _value(name, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _json_object(name, default):
    value = _value(name, default)
    if isinstance(value, dict):
        return value
    if not value:
        return default
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return default
    return parsed if isinstance(parsed, dict) else default


class env:
    DEBUG = _boolean("DEBUG", False)
    SECRET_KEY = _value("SECRET_KEY", "")
    ALLOWED_HOSTS = _value("ALLOWED_HOSTS", "")
    CSRF_TRUSTED_ORIGINS = _value("CSRF_TRUSTED_ORIGINS", "")
    TIME_ZONE = _value("TIME_ZONE", "Asia/Jakarta")

    # ``sql_server.pyodbc`` is the backend identifier used by the retired
    # django-pyodbc-azure package.  Keep old environment.py files usable with
    # the supported mssql-django package.
    DB_ENGINE = (
        "mssql"
        if _value("DB_ENGINE", "mssql") == "sql_server.pyodbc"
        else _value("DB_ENGINE", "mssql")
    )
    DB_NAME = _value("DB_NAME", "")
    DB_NAME_2 = _value("DB_NAME_2", "")
    DB_HOST = _value("DB_HOST", "")
    DB_PORT = _value("DB_PORT", _value("PORT", "1433"))
    DB_USER = _value("DB_USER", _value("USER", ""))
    DB_PASSWORD = _value("DB_PASSWORD", _value("PASSWORD", ""))
    DB_OPTIONS = _json_object(
        "DB_OPTIONS",
        _value("OPTIONS", {"driver": "ODBC Driver 18 for SQL Server"}),
    )

    JDBC_MODE = _value("JDBC_MODE", "LINUX")
    JDBC_DRIVER = _value("JDBC_DRIVER", "net.sourceforge.jtds.jdbc.Driver")
    JDBC_URL = _value("JDBC_URL", "")
    JDBC_DIR = _value("JDBC_DIR", "")
    HAPUS_FILE_HARI = _value("HAPUS_FILE_HARI", 30)

    SATU_SEHAT_URL = _value(
        "SATU_SEHAT_URL", "https://api-satusehat.kemkes.go.id/oauth2/v1"
    )
    SATU_SEHAT_URL_DATA = _value(
        "SATU_SEHAT_URL_DATA", "https://api-satusehat.kemkes.go.id/fhir-r4/v1"
    )

