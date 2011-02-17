==================
django-generic-m2m
==================

relate anything to anything


what it does
------------

the purpose of this project is to allow you to create database-level
relationships between various objects using a consistent api.

for a full tour of the api, the best place to look is the tests


quick overview
--------------

say you have a couple models::

    class Food(models.Model):
        name = models.CharField(max_length=255)

        related = RelatedObjectsDescriptor()

        def __unicode__(self):
            return self.name


    class Beverage(models.Model):
        name = models.CharField(max_length=255)

        related = RelatedObjectsDescriptor()

        def __unicode__(self):
            return self.name

Here's a sample interactive interpreter session::

    >>> pizza = Food.objects.create(name='pizza')
    >>> pepperoni = Food.objects.create(name='pepperoni')
    >>> beer = Beverage.objects.create(name='beer')
    >>> soda = Beverage.objects.create(name='soda')

    >>> pizza.related.connect(pepperoni)
    <RelatedObject: pizza related to pepperoni ("")>

    >>> pizza.related.connect(beer)
    <RelatedObject: pizza related to beer ("")>

    >>> pepperoni.related.related_to()  
    [<RelatedObject: pizza related to pepperoni ("")>]

    >>> pizza.related.all()
    [<RelatedObject: pizza related to beer ("")>, <RelatedObject: pizza related to pepperoni ("")>]

    >>> pizza.related.all().generic_objects()
    [<Beverage: beer>, <Food: pepperoni>]

    >>> Food.related.all()
    [<RelatedObject: pizza related to beer ("")>, <RelatedObject: pizza related to pepperoni ("")>]
