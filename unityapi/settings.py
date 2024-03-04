from pathlib import Path
import environ
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
root = environ.Path(os.path.join(BASE_DIR, 'secrets'))

# env.read_env(root('.env.prod'))
# env.read_env(root('.env.dev'))
env.read_env(root('.env'))

SECRET_KEY = env.str('SECRET_KEY')
KAONAVI_API_KEY = env.str('KAONAVI_API_KEY')
KAONAVI_API_SECRET = env.str('KAONAVI_API_SECRET')

DEBUG = env.bool('DEBUG', default=False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'unity_prod_db',
    }
}

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'rest_framework',
    'basicapi.apps.BasicapiConfig',
    'corsheaders',
    'djoser',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ORIGIN_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', default=[])

ROOT_URLCONF = 'unityapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

AUTH_USER_MODEL = 'basicapi.User'
ACTIVATION_EXPIRED_DAYS = 3
