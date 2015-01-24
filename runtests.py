#!/usr/bin/env python
import sys
from os.path import dirname, abspath

import django
from django.conf import settings


if len(sys.argv) > 1 and 'postgres' in sys.argv:
    sys.argv.remove('postgres')
    db_engine = 'django.db.backends.postgresql_psycopg2'
    db_name = 'test_main'
else:
    db_engine = 'django.db.backends.sqlite3'
    db_name = ''

if not settings.configured:
    settings.configure(
        DATABASES=dict(default=dict(ENGINE=db_engine, NAME=db_name)),
        INSTALLED_APPS = [
            'django.contrib.contenttypes',
            'genericm2m',
            'genericm2m.genericm2m_tests',
        ],
        MIDDLEWARE_CLASSES = (),
    )

from django.test.utils import get_runner

try:
    django.setup()
except AttributeError:
    pass

def runtests(*test_args):
    if not test_args:
        if sys.version_info[0] > 2:
            test_args = ['genericm2m.genericm2m_tests']
        else:
            test_args = ["genericm2m_tests"]
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    runtests(*sys.argv[1:])
