"""
Django settings for RedBoxAppBackend project.
"""

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-xhivb31q8qvf-i7q+wo&j@bc72kwq9ql5_8dvcasw9dzipf2^x')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ✅ ALLOWED_HOSTS simplificado
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '192.168.1.100',
    '192.168.1.108',
    'redboxapp.duckdns.org',
    '192.168.1.110',
    '.duckdns.org',
    '*',
]

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
    'anymail',
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

# ✅ Base de datos simplificada con dj_database_url
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # ✅ Usar dj_database_url para parsear la URL (más simple y robusto)
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
    print(f"🟢 Conectado a la base de datos: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'Neon'}")
else:
    # Fallback para desarrollo local sin Docker
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "bd_redboxapp",
            "USER": "postgres",
            "PASSWORD": "Copito123*",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }
    print("🟡 Conectado a la base de datos LOCAL")

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

# CORS
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo

# ==================== CONFIGURACIÓN DE RESEND ====================

EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
ANYMAIL = {
    "RESEND_API_KEY": os.environ.get("RESEND_API_KEY"),
}
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"