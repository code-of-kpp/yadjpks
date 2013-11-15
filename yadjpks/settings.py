import os.path

import six

from .settings_base import *

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..'))

conf = six.moves.configparser.SafeConfigParser()
conf.read((os.path.join(PACKAGE_ROOT, 'etc', 'runtime.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'private-runtime.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'mq.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'private-mq.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'private-db.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'urls.cfg'),
          os.path.join(PACKAGE_ROOT, 'etc', 'private-urls.cfg'),
          ))

get_default = lambda conf, sect, opt, val: conf.get(sect, opt) \
    if conf.has_option(sect, opt) else val
get_float_default = lambda conf, sect, opt, val: conf.getfloat(sect, opt) \
    if conf.has_option(sect, opt) else val
get_int_default = lambda conf, sect, opt, val: conf.getint(sect, opt) \
    if conf.has_option(sect, opt) else val
get_bool_default = lambda conf, sect, opt, val: conf.getboolean(sect, opt) \
    if conf.has_option(sect, opt) else val

# i18n and timezone:
TIME_ZONE = conf.get('i18n', 'time zone')
LANGUAGE_CODE = conf.get('i18n', 'language code')

# debug settings:
DEBUG = os.path.exists(os.path.join(PROJECT_ROOT, 'settings_debug.py'))
TEMPLATE_DEBUG = DEBUG
CRISPY_FAIL_SILENTLY = not DEBUG

# paths settigns:
DATA_ROOT = os.path.join(PACKAGE_ROOT, conf.get('paths', 'data root'))
STATIC_ROOT = os.path.join(PACKAGE_ROOT, conf.get('paths', 'static root'))
TEMPLATE_DIRS = (os.path.join(PACKAGE_ROOT, 'templates'),)

STATICFILES_DIRS = []
for key in ('js', 'css', 'font', 'img'):
    path = os.path.join(PACKAGE_ROOT, 'data', key)
    if os.path.exists(path):
        STATICFILES_DIRS.append(path)
STATICFILES_DIRS = tuple(STATICFILES_DIRS)

# caches:
CACHES = {}
if conf.has_section('memcached-nodes'):
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': tuple((v[1] for v in conf.items('memcached-nodes'))),
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
          for s in conf.sections()
          if s.startswith('database-')):
    dbsection = s.replace('database-', '')
    DATABASES[dbsection] = {}
    engine = conf.get(s, 'engine')
    DATABASES[dbsection]['ENGINE'] = engines.get(engine.lower(), engine)
    for param in ('HOST', 'PORT', 'NAME',
                  'USER', 'PASSWORD',
                 ):
        lparam = param.lower()
        if conf.has_option(s, lparam):
            DATABASES[dbsection][param] = conf.get(s, lparam)

# emails:
if conf.has_section('email'):
    if conf.has_option('email', 'use tls'):
        EMAIL_USE_TLS = conf.getboolean('email', 'use tls')
    EMAIL_HOST = conf.get('email', 'host')
    EMAIL_HOST_USER = conf.get('email', 'user')
    EMAIL_HOST_PASSWORD = conf.get('email', 'password')
    if conf.has_option('email', 'port'):
        EMAIL_PORT = conf.getint('email', 'port')
    if conf.has_option('email', 'subject prefix'):
        EMAIL_SUBJECT_PREFIX = conf.get('email', 'subject prefix') + ' '

# admins:
if conf.has_section('admins'):
    ADMINS = tuple(((a[1], a[0]) for a in conf.items('admins')))

# libraries:
if conf.has_option('lib', 'nodejs'):
    NODEJS_BINARY = os.path.abspath(
            os.path.join(*conf.get('lib', 'nodejs').split('/')))

if conf.has_option('lib', 'lessc'):
    PIPELINE_LESS_BINARY = ' '.join((NODEJS_BINARY, os.path.abspath(
            os.path.join(*conf.get('lib', 'lessc').split('/')))))

# communication with workers:
if conf.has_section('celery'):
    try:
        import djcelery
        djcelery.setup_loader()
        INSTALLED_APPS = ('djcelery', ) + INSTALLED_APPS
    except ImportError as exc:
        msg = exc.args[0]
        modname = 'djcelery'
        if not msg.startswith('No module named') or modname not in msg:
            raise
    BROKER_URL = conf.get('celery', 'broker')

    if BROKER_URL == 'django://':
        INSTALLED_APPS += ('kombu.transport.django', )

    CELERY_IGNORE_RESULT = get_bool_default(conf,
        'celery', 'ignore result', True)

    CELERY_STORE_ERRORS_EVEN_IF_IGNORED = get_bool_default(conf,
        'celery', 'store errors even if ignored', True)


if conf.has_section('celery-queues'):
    CELERY_ROUTES = {}
    for queue, tasks in conf.items('celery-queues'):
        for task in tasks.split():
            CELERY_ROUTES[task] = {'queue': queue}

if conf.has_section('pyro'):
    PYRO_HOST = conf.get('pyro', 'host')
    PYRO_PORT = conf.getint('pyro', 'port')

# security:
ALLOWED_HOSTS = ('127.0.0.1', 'localhost', ) if \
    not conf.has_option('security', 'allowed hosts') else \
    tuple((conf.get('security', 'allowed hosts').split()))

SECRET_KEY = conf.get('security', 'secret key')

# apps:
for name in ('private-apps.txt', 'apps.txt'):
    apps_file = os.path.join(PACKAGE_ROOT, 'etc', name)
    if os.path.exists(apps_file):
        with open(apps_file) as f:
            INSTALLED_APPS = tuple((
                line for line in
                        six.moves.map(lambda s: s.strip(), f)
                    if line and not line.startswith('#')
            )) + INSTALLED_APPS


# top-level urls (assume urls module in every app here):
if conf.has_section('top level urls'):
    TOP_LEVEL_URLS = tuple(((a[0], a[1])
        for a in conf.items('top level urls')))


# other:

if 'django.contrib.sessions' in INSTALLED_APPS:
    MIDDLEWARE_CLASSES.append(
        'django.contrib.sessions.middleware.SessionMiddleware')

if 'django.contrib.auth' in INSTALLED_APPS:
    MIDDLEWARE_CLASSES.append(
        'django.contrib.auth.middleware.AuthenticationMiddleware')

if 'django.contrib.messages' in INSTALLED_APPS:
    MIDDLEWARE_CLASSES.append(
        'django.contrib.messages.middleware.MessageMiddleware')

# Uncomment the next line for simple clickjacking protection:
# MIDDLEWARE_CLASSES.append(
#     'django.middleware.clickjacking.XFrameOptionsMiddleware')

MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES)

ROOT_URLCONF = 'yadjpks.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'yadjpks.wsgi.application'

if DEBUG:
    from .settings_debug import *
    try:
        import django_extensions  # lint:ok
        INSTALLED_APPS = INSTALLED_APPS + ('django_extensions', )
    except ImportError as exc:
        msg = exc.args[0]
        modname = 'django_extensions'
        if not msg.startswith('No module named') or modname not in msg:
            raise
