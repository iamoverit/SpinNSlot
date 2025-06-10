import os
from pathlib import Path
from decouple import config

from huey import SqliteHuey

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')

DEBUG = config('DEBUG', cast=bool)
WEEK_START_FROM_MONDAY = config('WEEK_START_FROM_MONDAY', cast=bool)
BASE_HOST = config('BASE_HOST')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', BASE_HOST]
CSRF_TRUSTED_ORIGINS = ['https://*.127.0.0.1', f'https://{BASE_HOST}']

INSTALLED_APPS = [
    'huey.contrib.djhuey',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'django_ratelimit',
    'markdownify.apps.MarkdownifyConfig',
    'web',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
]
RATELIMIT_VIEW = 'web.views.ratelimit_view'
ROOT_URLCONF = 'config.urls'

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
                'web.context_processors.customer_context',
                'web.context_processors.theme',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
HUEY = SqliteHuey(filename=str(BASE_DIR / 'db' / 'huey_db.sqlite3'), immediate=False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'web.cache.CustomFileBasedCache',
        'LOCATION':  BASE_DIR / 'db' / 'django_cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Maximum number of cache entries
        }
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
LANGUAGE_CODE = 'ru-ru'

LANGUAGES = [
    ('ru', 'Russian'),
    ('en', 'English'),
]

import locale
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')  # Для Windows
        except locale.Error:
            pass

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')     

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BOOTSTRAP5 = {
    "css_url": {
        "url": f"{STATIC_URL}bootstrap/css/bootstrap.min.css",
    },

    "javascript_url": {
        "url": f"{STATIC_URL}bootstrap/js/bootstrap.bundle.min.js",
    },
    "color_mode": None,
}

TELEGRAM_BOT_NAME = config('TELEGRAM_BOT_NAME')
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='unsafe-secret-key')
TELEGRAM_LOGIN_REDIRECT_URL = config('TELEGRAM_LOGIN_REDIRECT_URL', default='http://127.0.0.1/')

AUTH_USER_MODEL = 'web.CustomUser'

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_queries.log',  # Choose a file name and path
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

MARKDOWNIFY = {
    "default": {
        "BLEACH": False,
    },
    "preview": {
        "WHITELIST_TAGS": ["a", "br", "p"],
        "BLEACH": True,
    }
}

if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += [
            'debug_toolbar',
        ]

        MIDDLEWARE += [
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        ]

        INTERNAL_IPS = [
            '127.0.0.1',
        ]

    except ImportError:
        pass