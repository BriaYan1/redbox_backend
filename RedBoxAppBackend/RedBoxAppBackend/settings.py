"""
Django settings for RedBoxAppBackend project.
"""

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import os
from urllib.parse import urlparse, parse_qsl

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-xhivb31q8qvf-i7q+wo&j@bc72kwq9ql5_8dvcasw9dzipf2^x'
DEBUG = True
ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'backend',
    'corsheaders',
    'rest_framework.authtoken',
    'anymail',  # ✅ Agregar esta línea
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'RedBoxAppBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RedBoxAppBackend.wsgi.application'


# Database
database_url = os.getenv("DATABASE_URL") or ""

if isinstance(database_url, bytes):

    database_url = database_url.decode("utf-8")


tmpPostgres = urlparse(database_url)

DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.postgresql',

        'NAME': tmpPostgres.path.replace('/', '') if isinstance(tmpPostgres.path, str) else tmpPostgres.path.decode('utf-8').replace('/', ''),

        'USER': tmpPostgres.username if isinstance(tmpPostgres.username, str) else tmpPostgres.username.decode('utf-8') if tmpPostgres.username else '',

        'PASSWORD': tmpPostgres.password if isinstance(tmpPostgres.password, str) else tmpPostgres.password.decode('utf-8') if tmpPostgres.password else '',

        'HOST': tmpPostgres.hostname if isinstance(tmpPostgres.hostname, str) else tmpPostgres.hostname.decode('utf-8') if tmpPostgres.hostname else '',

        'PORT': 5432,

        'OPTIONS': dict(parse_qsl(tmpPostgres.query if isinstance(tmpPostgres.query, str) else tmpPostgres.query.decode('utf-8'))),

    }

}

# Password validation
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


# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

CORS_ALLOW_ALL_ORIGINS = True

# ==================== CONFIGURACIÓN DE RESEND ====================

# Backend de email usando Anymail con Resend
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

# Configuración de Resend
ANYMAIL = {
    "RESEND_API_KEY": os.environ.get("RESEND_API_KEY"),
}

# Correo por defecto (usa el dominio de prueba de Resend)
# Después puedes cambiarlo por DEFAULT_FROM_EMAIL = "no-reply@tudominio.com"
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"

############# Cloudflare ################

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.108', '190.75.32.29', 'redboxapp.duckdns.org']
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.100',      # ← Agrega tu IP local
    'redboxapp.duckdns.org',
    '.duckdns.org',      
]