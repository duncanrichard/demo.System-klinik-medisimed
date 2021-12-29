import os
from .environment import env
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'e(hj*&lv%pce(8t234l6dv#!@7%k644_97v-bo^7b7r1y%2unv'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'IMMODERMA.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(os.path.join(BASE_DIR, 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'IMMODERMA.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': getattr(env, 'DB_ENGINE', 'sql_server.pyodbc'),
        'NAME': getattr(env, 'DB_NAME', ''),
        'HOST': getattr(env, 'DB_HOST', ''),
        'PORT': getattr( env,'PORT', '1433'),
        'USER': getattr(env, 'USER', ''),
        'PASSWORD': getattr(env, 'PASSWORD', ''),
        'OPTIONS': getattr(env, 'OPTIONS' , {'driver': 'ODBC Driver 17 for SQL Server'}),
    },

    'antrian': {
        'ENGINE': getattr(env, 'DB_ENGINE', 'sql_server.pyodbc'),
        'NAME': getattr(env, 'DB_NAME_2', ''),
        'HOST': getattr(env, 'DB_HOST', ''),
        'PORT': getattr( env,'PORT', '1433'),
        'USER': getattr(env, 'USER', ''),
        'PASSWORD': getattr(env, 'PASSWORD', ''),
        'OPTIONS': getattr(env, 'OPTIONS' , {'driver': 'ODBC Driver 17 for SQL Server'}),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'DEBUG/'+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+'.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}