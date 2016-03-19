import os
import sys
from aristotle_mdr.required_settings import *

BASE = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(1, BASE)
sys.path.insert(1, os.path.join(BASE, "tests"))
sys.path.insert(1, os.path.join(BASE, "tests/apps"))
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'tests/apps/bulk_actions_test/templates')
]

SECRET_KEY = 'inara+vtkprm7@0(fsc$+grbz9-s+tmo9d)e#k(9uf8m281&$7xhdkjr'
SOUTH_TESTS_MIGRATE = True

MEDIA_ROOT = os.path.join(BASE, "media")
MEDIA_URL = '/media/'
CKEDITOR_UPLOAD_PATH = 'uploads/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test_database',
    }
}

if 'TRAVIS' in os.environ:
    if os.environ.get('DB') == 'sqlitefile':
        print("Running TRAVIS-CI test-suite with file-based SQLite")
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test_database',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    elif os.environ.get('DB') == 'postgres':
        print("Running TRAVIS-CI test-suite with POSTGRESQL")
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'aristotle_test_db',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    # elif os.eviron.get('DB') == 'mysql':
    elif os.environ.get('DB') == 'sqlitememory':
        print("Running TRAVIS-CI test-suite with memory-based SQLite")
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }

class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

MIGRATION_MODULES = DisableMigrations()

INSTALLED_APPS = (
    # The good stuff
    'templatetags',
    'extension_test',
    'text_download_test',
) + INSTALLED_APPS

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'aristotle_mdr.contrib.whoosh_backend.FixedWhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'aristotle_mdr/tests/whoosh_index'),
        'INCLUDE_SPELLING': True,
    },
}

# https://docs.djangoproject.com/en/1.6/topics/testing/overview/#speeding-up-the-tests
# We do a lot of user log in testing, this should speed stuff up.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

ARISTOTLE_SETTINGS['SEPARATORS']['DataElementConcept'] = '--'
ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] = ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] + ['extension_test']
ARISTOTLE_DOWNLOADS = ARISTOTLE_DOWNLOADS + [
    ('txt', 'Text', 'fa-file-pdf-o', 'text_download_test'),
]
ARISTOTLE_SETTINGS['BULK_ACTIONS'].update({
    'delete': 'bulk_actions_test.actions.StaffDeleteActionForm',
    'incomplete': 'bulk_actions_test.actions.IncompleteActionForm',
})
ROOT_URLCONF = 'extension_test.urls'

# disable
__LOGGING__ = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console-simple': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
            },
        },
    'loggers': {
        'aristotle_mdr': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
            },
        'django': {
            'handlers': ['console-simple'],
            'level': 'INFO',
            'propagate': True,
            },
        }
    }

"""
if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
"""