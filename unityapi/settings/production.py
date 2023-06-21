from .base import *

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'production': {
            'format': '%(asctime)s [%(levelname)s] %(process)d %(thread)d '
                      '%(pathname)s:%(lineno)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/production.log',
            'formatter': 'production',
            'level': 'INFO',
        },
    },
    'loggers': {
        # 自作したログ出力
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Djangoの警告・エラー
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/production.log',
            'formatter': 'production',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 5,
        },
    },
}

