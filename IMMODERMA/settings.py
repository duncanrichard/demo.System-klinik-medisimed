import os

from django.core.exceptions import ImproperlyConfigured

from .config import env


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _csv(value):
    return [item.strip() for item in str(value).split(",") if item.strip()]


DEBUG = env.DEBUG
SECRET_KEY = env.SECRET_KEY
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "unsafe-development-only-key"
    else:
        raise ImproperlyConfigured(
            "IMMODERMA_SECRET_KEY wajib diisi ketika IMMODERMA_DEBUG=False."
        )

ALLOWED_HOSTS = _csv(env.ALLOWED_HOSTS)
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

CSRF_TRUSTED_ORIGINS = _csv(env.CSRF_TRUSTED_ORIGINS)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "IMMODERMA.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "IMMODERMA.wsgi.application"

_database_common = {
    "ENGINE": env.DB_ENGINE,
    "HOST": env.DB_HOST,
    "PORT": env.DB_PORT,
    "USER": env.DB_USER,
    "PASSWORD": env.DB_PASSWORD,
    "OPTIONS": env.DB_OPTIONS,
}

DATABASES = {
    "default": dict(_database_common, NAME=env.DB_NAME),
    "antrian": dict(_database_common, NAME=env.DB_NAME_2),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "id-id"
TIME_ZONE = env.TIME_ZONE
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

SESSION_ENGINE = "django.contrib.sessions.backends.file"
SESSION_COOKIE_NAME = "Immoderma_Session_ID"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

LOG_DIR = os.path.join(BASE_DIR, "DEBUG")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "immoderma.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "IMMODERMA": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

UPLOAD_PATH = os.path.join("static", "excel", "uploads") + os.sep
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
