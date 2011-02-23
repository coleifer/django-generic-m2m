#!/usr/bin/env python
import sys
from os.path import dirname, abspath

from django.conf import settings


if len(sys.argv) > 1 and 'postgres' in sys.argv:
    sys.argv.remove('postgres')
    db_engine = 'postgresql_psycopg2'
    db_name = 'test_main'
else:
    db_engine = 'sqlite3'
    db_name = ''

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE = db_engine,
        DATABASE_NAME = db_name,
        INSTALLED_APPS = [
            'django.contrib.contenttypes',
            'genericm2m',
            'genericm2m.genericm2m_tests',
        ],
    )

from django.test.simple import run_tests


def runtests(*test_args):
    if not test_args:
        test_args = ['genericm2m_tests']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
