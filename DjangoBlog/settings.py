"""
Django settings for DjangoBlog project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import sys
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n9ceqv38)#&mwuat@(mjb_p%em$e8$qyr#fw9ot!=ba6lijx-6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', False)

# 'rain' is supported right now
WEATHER = os.getenv('DJANGO_WEATHER', 'NORMAL')
# DEBUG = False
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['*', '127.0.0.1', 'mtuktarov.ru', '192.168.1.64']
# Application definition
# MY_SUPER_ERROR = 0
# MESSAGE_LEVEL = MY_SUPER_ERROR
LOGO_COLOR_BACKGROUND = '#2d2f44'
LOGO_COLOR_TEXT = '#e0bf4b'


SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.abspath(os.path.join(SITE_ROOT, '../'))
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'mdeditor',
    'haystack',
    'blog',
    'accounts',
    'comments',
    'oauth',
    'servermanager',
    'compressor'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',


    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'blog.middleware.OnlineMiddleware',

]

ROOT_URLCONF = 'DjangoBlog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'templates/share_layout')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.seo_processor',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'DjangoBlog.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
SITE_DOMAIN_NAME = os.getenv('DJANGO_SITE_DOMAIN_NAME', 'mtuktarov.ru')
DJANGO_SU_NAME = os.environ.get('DJANGO_SU_NAME', 'admin')
DJANGO_SU_EMAIL = os.environ.get('DJANGO_SU_EMAIL', 'admin@admin.admin')
DJANGO_SU_PASSWORD = os.environ.get('DJANGO_SU_PASSWORD', 'admin123')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGNAME', 'blogd'),
        'USER': os.getenv('PGUSER', 'blogd'),
        'PASSWORD': os.getenv('PGPASSWORD', 'blogd'),
        'HOST': os.getenv('PGHOST', '/opt/blogd/sockets'),
    }
}
# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

# LANGUAGE_CODE = 'zh-hans'
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'DjangoBlog.whoosh_cn_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
# Automatically update searching index
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# Allow user login with username and password
AUTHENTICATION_BACKENDS = ['accounts.user_login_backend.EmailOrUsernameModelBackend']

STATIC_ROOT = '/opt/blogd_static'

STATIC_URL = '/static/'
STATICFILES = os.path.join(BASE_DIR, 'static')

AUTH_USER_MODEL = 'accounts.BlogUser'
LOGIN_URL = '/login/'

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_TIME_FORMAT = '%Y-%m-%d'

# bootstrap color styles
BOOTSTRAP_COLOR_TYPES = [
    'default', 'primary', 'success', 'info', 'warning', 'danger'
]

# paginate
PAGINATE_BY = 10
# http cache timeout
CACHE_CONTROL_MAX_AGE = 2592000

DISABLE_CACHE = os.getenv('DJANGO_DISABLE_CACHE', False)
# cache setting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache' if DISABLE_CACHE else 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'mtuktarov_test' if TESTING else 'mtuktarov',
        'TIMEOUT': 60 * 60 * 10
    }
}

SITE_ID = 1

# Emial:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_FILES = os.path.join(BASE_DIR, 'templates/email')
# postfix app gmail password: tgmsfmcrzethlkoi
EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = os.getenv('DJANGO_EMAIL_PORT', 465)
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_USER', 'noreply@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_PASS', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
# Setting debug=false did NOT handle except email notifications
ADMINS = []
# WX ADMIN password(Two times md5)
WXADMIN = '995F03AC401D6CABABAEF756FC4D43C7'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'log_file'],
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d %(module)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'djangoblog.log',
            'maxBytes': 16777216,  # 16 MB
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'djangoblog': {
            'handlers': ['log_file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other
    'compressor.finders.CompressorFinder',
)
# COMPRESS_ENABLED = True
COMPRESS_ENABLED = False
# COMPRESS_OFFLINE = True

COMPRESS_CSS_FILTERS = [
    # creates absolute urls from relative ones
    # 'compressor.filters.css_default.CssAbsoluteFilter',
    # css minimizer
    # 'compressor.filters.cssmin.CSSMinFilter'
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter'
]

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/media/'

MDEDITOR_CONFIGS = {
    'default': {
        'width': '90%',
        'height': 500,
        'toolbar': ["undo", "redo", "|",
                    "bold", "del", "italic", "quote", "ucwords", "uppercase",
                    "lowercase", "|",
                    "h1", "h2", "h3", "h5", "h6", "|",
                    "list-ul", "list-ol", "hr", "|",
                    "link", "reference-link", "image", "code",
                    "preformatted-text", "code-block", "table", "datetime",
                    "emoji", "html-entities", "pagebreak", "goto-line", "|",
                    "help", "info",
                    "||", "preview", "watch", "fullscreen"],
        'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],  # image upload format type
        'image_folder': 'editor',  # image save the folder name
        'theme': 'default',  # edit box theme, dark / default
        'preview_theme': 'default',  # Preview area theme, dark / default
        'editor_theme': 'default',  # edit area theme, pastel-on-dark / default
        'toolbar_autofixed': True,  # Whether the toolbar capitals
        'search_replace': True,  # Whether to open the search for replacement
        'emoji': True,  # whether to open the expression function
        'tex': True,  # whether to open the tex chart function
        'flow_chart': True,  # whether to open the flow chart function
        'sequence': True,  # Whether to open the sequence diagram function
        'watch': True,  # Live preview
        'language': 'en',  # zh / en
        'lineWrapping': True,  # lineWrapping
        'lineNumbers': True,  # lineNumbers,
        'placeholder': 'Enjoy!'
    },
    'custom': {
        'width': '90%',
        'height': 200,
        'toolbar': ["undo", "redo"]
    }
}

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger', }


try:
    from local_settings import *
except ImportError:
    pass
