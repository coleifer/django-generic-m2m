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
