from pathlib import Path
import environ
from datetime import timedelta
import os
import boto3

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
secrets = environ.Path(os.path.join(BASE_DIR, 'secrets'))
env.read_env(secrets('.env'))

SECRET_KEY = env.str('SECRET_KEY')

KAONAVI_API_KEY = env.str('KAONAVI_API_KEY')
KAONAVI_API_SECRET = env.str('KAONAVI_API_SECRET')

AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = env.str('AWS_S3_BUCKET_NAME')
AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME')
AWS_S3_EXPIRES_IN = env.int('AWS_S3_EXPIRES_IN')

STORAGE_CLIENT = boto3.client('s3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION_NAME)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])
CORS_ORIGIN_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', default=[])

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'access-control-allow-origin',
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

WSGI_APPLICATION = 'unityapi.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1440)
}

AUTH_USER_MODEL = 'basicapi.User'

ACTIVATION_EXPIRED_DAYS = 3

# SendGrid
#本番環境用
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'xxx@gmail.com'
# EMAIL_HOST_PASSWORD = 'xxx'
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'xxx@gmail.com'
# SENDGRID_SANDBOX_MODE_IN_DEBUG = False
# SENDGRID_TRACK_CLICKS_PLAIN = False

#ローカル確認用
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
SENDGRID_API_KEY = env('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE_IN_DEBUG = True
SENDGRID_TRACK_CLICKS_PLAIN = False
SENDGRID_ECHO_TO_STDOUT = True
MY_URL = env.str('MY_URL', default='http://localhost:8000')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': env.str('DB_NAME'),
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

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

# 開発環境
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
