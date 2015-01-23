try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from genericm2m.models import RelatedObjectsDescriptor


class RelatedBeverage(models.Model):
    food = models.ForeignKey('Food')
    beverage = models.ForeignKey('Beverage')

    class Meta:
        ordering = ('-id',)


class Food(models.Model):
    name = models.CharField(max_length=255)

    related = RelatedObjectsDescriptor()
    related_beverages = RelatedObjectsDescriptor(RelatedBeverage, 'food', 'beverage')

    def __unicode__(self):
        return self.name


class Beverage(models.Model):
    name = models.CharField(max_length=255)

    related = RelatedObjectsDescriptor()

    def __unicode__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=255)

    related = RelatedObjectsDescriptor()

    def __unicode__(self):
        return self.name


class Boring(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class AnotherRelatedObject(models.Model):
    parent_type = models.ForeignKey(ContentType, related_name="child_%(class)s")
    parent_id = models.IntegerField(db_index=True)
    parent = GenericForeignKey(ct_field="parent_type", fk_field="parent_id")

    object_type = models.ForeignKey(ContentType, related_name="related_%(class)s")
    object_id = models.IntegerField(db_index=True)
    object = GenericForeignKey(ct_field="object_type", fk_field="object_id")

    alias = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id',)


class Note(models.Model):
    content = models.TextField()

    related = RelatedObjectsDescriptor(AnotherRelatedObject)
