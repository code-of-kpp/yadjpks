
import os.path
try:
    import configparser
except ImportError:
    import ConfigParser as configparser  # lint:ok

from .settings_base import *

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..'))

CONF = configparser.SafeConfigParser()
CONF.read((os.path.join(PACKAGE_ROOT, 'etc', 'runtime.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'private-runtime.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'private-mq.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'private-db.cfg'),
          ))

# i18n and timezone:
TIME_ZONE = CONF.get('i18n', 'time zone')
LANGUAGE_CODE = CONF.get('i18n', 'language code')

# debug settings:
DEBUG = os.path.exists(os.path.join(PROJECT_ROOT, 'settings_debug.py'))
TEMPLATE_DEBUG = DEBUG
CRISPY_FAIL_SILENTLY = not DEBUG

# paths settigns:
DATA_ROOT = os.path.join(PACKAGE_ROOT, CONF.get('paths', 'data root'))
STATIC_ROOT = os.path.join(PACKAGE_ROOT, CONF.get('paths', 'static root'))
TEMPLATE_DIRS = (os.path.join(PACKAGE_ROOT, 'templates'),)

STATICFILES_DIRS = []
for key in ('js', 'css', 'font', 'img'):
    path = os.path.join(PACKAGE_ROOT, 'data', key)
    if os.path.exists(path):
        STATICFILES_DIRS.append(path)

# caches:
CACHES = {}
if CONF.has_section('memcached-nodes'):
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': tuple((v[1] for v in CONF.items('memcached-nodes'))),
    }
else:
    del CACHES

# DBs:
DATABASES = {}

engines = {
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'postgre': 'django.db.backends.postgresql_psycopg2',
    'pg': 'django.db.backends.postgresql_psycopg2',
    'mysql': 'django.db.backends.mysql',
    'sqlite': 'django.db.backends.sqlite3',
    'sqlite3': 'django.db.backends.sqlite3',
    'oracle': 'django.db.backends.oracle',
}

for s in (s
          for s in CONF.sections()
          if s.startswith('database-')):
    dbsection = s.replace('database-', '')
    DATABASES[dbsection] = {}
    engine = CONF.get(s, 'engine')
    DATABASES[dbsection]['ENGINE'] = engines.get(engine, engine)
    for param in ('HOST', 'PORT', 'NAME',
                  'USER', 'PASSWORD',
                 ):
        lparam = param.lower()
        if CONF.has_option(s, lparam):
            DATABASES[dbsection][param] = CONF.get(s, lparam)

# emails:
if CONF.has_section('email'):
    if CONF.has_option('email', 'use tls'):
        EMAIL_USE_TLS = CONF.getboolean('email', 'use tls')
    EMAIL_HOST = CONF.get('email', 'host')
    EMAIL_HOST_USER = CONF.get('email', 'user')
    EMAIL_HOST_PASSWORD = CONF.get('email', 'password')
    if CONF.has_option('email', 'port'):
        EMAIL_PORT = CONF.getint('email', 'port')
    if CONF.has_option('email', 'subject prefix'):
        EMAIL_SUBJECT_PREFIX = CONF.get('email', 'subject prefix') + ' '

# admins:
if CONF.has_section('admins'):
    ADMINS = tuple(((a[1], a[0]) for a in CONF.items('admins')))

# libraries:
if CONF.has_option('lib', 'nodejs'):
    NODEJS_BINARY = os.path.abspath(
            os.path.join(*CONF.get('lib', 'nodejs').split('/')))
else:
    NODEJS_BINARY = 'node'

if CONF.has_option('lib', 'lessc'):
    PIPELINE_LESS_BINARY = ' '.join((NODEJS_BINARY, os.path.abspath(
            os.path.join(*CONF.get('lib', 'lessc').split('/')))))

# communication with workers:
if CONF.has_section('celery'):
    try:
        import djcelery
        djcelery.setup_loader()
        INSTALLED_APPS = ('djcelery', ) + INSTALLED_APPS
    except ImportError:
        pass
    BROKER_URL = CONF.get('celery', 'broker')

if CONF.has_section('pyro'):
    PYRO_HOST = CONF.get('pyro', 'host')
    PYRO_PORT = CONF.getint('pyro', 'port')

# security:
ALLOWED_HOSTS = ('127.0.0.1', 'localhost', ) if \
    not CONF.has_option('security', 'allowed hosts') else \
    tuple((CONF.get('security', 'allowed hosts').split()))

SECRET_KEY = CONF.get('security', 'secret key')

# other:
MIDDLEWARE_CLASSES += (
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'yadjpks.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'yadjpks.wsgi.application'

#INSTALLED_APPS = ('yourapp', ) + INSTALLED_APPS

if DEBUG:
    from .settings_debug import *
    try:
        import django_extensions
        INSTALLED_APPS = INSTALLED_APPS + ('django_extensions', )
    except ImportError:
        pass
