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

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CORS_ORIGIN_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', default=[])

# 本番環境用
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {"simple": {"format": "%(asctime)s [%(levelname)s] %(message)s"}},
#     "handlers": {
#         "file": {
#             "level": "INFO",
#             "class": "logging.FileHandler",
#             "filename": "/var/log/django/app.log",
#             "formatter": "simple",
#         },
#     },
#     "loggers": {
#         "django": {"handlers": ["file"], "level": "INFO", "propagate": False,},
#         "": {"handlers": ["file"], "level": "INFO", "propagate": False,},
#     },
# }

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
