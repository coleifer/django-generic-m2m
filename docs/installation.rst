Getting started
===============

Installation
------------

You can pip install django-generic-m2m::

    pip install django-generic-m2m

Alternatively, you can use the version hosted on GitHub, which may contain new
or undocumented features::

    git clone git://github.com/coleifer/django-generic-m2m.git
    cd django-generic-m2m
    python setup.py install


Adding to your Django Project
--------------------------------

After installing, adding genericm2m to your projects is a snap.  First,
add it to your projects' `INSTALLED_APPS` and run `django-admin.py syncdb`::
    
    # settings.py
    INSTALLED_APPS = [
        ...
        'genericm2m'
    ]
