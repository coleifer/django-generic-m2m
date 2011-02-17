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


class Beverage(models.Model):
    name = models.CharField(max_length=255)
    
    related = RelatedObjectsDescriptor()


class Person(models.Model):
    name = models.CharField(max_length=255)
    
    related = RelatedObjectsDescriptor()
