import os
from setuptools import setup, find_packages

from genericm2m import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='django-generic-m2m',
    version=".".join(map(str, VERSION)),
    description='relate anything to anything',
    long_description=readme,
    author='Charles Leifer',
    author_email='coleifer@gmail.com',
    url='https://github.com/coleifer/django-generic-m2m',
    packages=find_packages(),
    package_data = {
        'genericm2m': [
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    test_suite='runtests.runtests',
)
