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


Up and running stupid fast
--------------------------

You need to add a ``RelatedObjectsDescriptor`` to any model you intend to relate
objects from.  For example, a news site may want to relate its news stories to
various other models::

    from django.db import models
    
    from genericm2m.models import RelatedObjectsDescriptor
    
    
    class Story(models.Model):
        # ... story fields ...
        
        related = RelatedObjectsDescriptor()
        
        # rest of model definition follows


Now you can relate your stories to other objects::

    >>> story.related.connect(some_city) # create a relationship between story and some_city
    >>> story.related.connect(some_public_figure) # ... between story and some_public_figure

These relationships can be queried::

    >>> story.related.all() # find out what "story" has been related to
    [<RelatedObject: story related to some_city ("")>,
     <RelatedObject: story related to some_public_figure ("")>]

And you can use a custom method on the ``QuerySet`` to get at those related
objects using an optimized query::

    >>> story.related.all().generic_objects() # traverse the GFK to get the actual objects
    [<City: some_city>, <Person: some_public_figure>]


Monkeypatching
^^^^^^^^^^^^^^

If the model definition isn't accessible, whether because it is in a 3rd party
app or because it is in a contrib app, you can monkeypatch::

    from django.contrib.auth.models import User
    
    from genericm2m.utils import monkey_patch
    
    monkey_patch(User, 'related')


Now you can create relationships from ``User`` objects::

    >>> some_guy = User.objects.get(username='some_guy') # get a user object
    >>> pizza = Food.objects.get(name='pizza') # get a food object
    >>> some_guy.related.connect(pizza) # connect the user to the food
