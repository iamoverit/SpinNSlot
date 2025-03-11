import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')

DEBUG = config('DEBUG')
BASE_HOST = config('BASE_HOST')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', BASE_HOST]
CSRF_TRUSTED_ORIGINS = ['https://*.127.0.0.1', f'https://{BASE_HOST}']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'markdownify.apps.MarkdownifyConfig',
    'web',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
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

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')     

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BOOTSTRAP5 = {
    "css_url": {
        "url": "/static/css/bootstrap.min.css",
    },
    "javascript_url": {
        "url": "/static/js/bootstrap.bundle.min.js",
    },
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