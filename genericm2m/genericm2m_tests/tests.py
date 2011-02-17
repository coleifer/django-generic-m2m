from django.test import TestCase

from genericm2m.models import RelatedObject, RelatedObjectsDescriptor
from genericm2m.genericm2m_tests.models import Food, Beverage, Person, RelatedBeverage


class RelationsTestCase(TestCase):
    def setUp(self):
        self.pizza = Food.objects.create(name='pizza')
        self.sandwich = Food.objects.create(name='sandwich')
        self.cereal = Food.objects.create(name='cereal')
        
        self.soda = Beverage.objects.create(name='soda')
        self.beer = Beverage.objects.create(name='beer')
        self.milk = Beverage.objects.create(name='milk')
        
        self.mario = Person.objects.create(name='mario')
        self.sam = Person.objects.create(name='sam')
        self.chocula = Person.objects.create(name='chocula')
    
    def assertRelatedEqual(self, rel_qs, tups, from_field='parent',
                           to_field='object'):
        rel_tup = [
            (getattr(rel_obj, from_field), getattr(rel_obj, to_field)) \
            for rel_obj in rel_qs
        ]
        self.assertEqual(rel_tup, list(tups))
    
    def test_connect(self):
        self.pizza.related.connect(self.soda)
        self.pizza.related.connect(self.beer)
        self.pizza.related.connect(self.mario)
        
        self.soda.related.connect(self.pizza)
        self.soda.related.connect(self.beer)
        
        related = self.pizza.related.all()
        self.assertRelatedEqual(related, (
            (self.pizza, self.mario),
            (self.pizza, self.beer),
            (self.pizza, self.soda),
        ))
        
        self.sandwich.related.connect(self.soda)
        self.sandwich.related.connect(self.milk)
        
        related = self.sandwich.related.all()
        self.assertRelatedEqual(related, (
            (self.sandwich, self.milk),
            (self.sandwich, self.soda),
        ))
        
        related = self.cereal.related.all()
        self.assertRelatedEqual(related, ())
        
        related = self.soda.related.all()
        self.assertRelatedEqual(related, (
            (self.soda, self.beer),
            (self.soda, self.pizza),
        ))
    
    def test_related_to(self):
        self.pizza.related.connect(self.soda)
        self.pizza.related.connect(self.beer)
        self.sandwich.related.connect(self.soda)
        self.sandwich.related.connect(self.milk)
        self.mario.related.connect(self.soda)
        self.soda.related.connect(self.pizza)
        
        related = self.soda.related.related_to()
        self.assertRelatedEqual(related, (
            (self.mario, self.soda),
            (self.sandwich, self.soda),
            (self.pizza, self.soda),
        ))
        
        related = self.beer.related.related_to()
        self.assertRelatedEqual(related, (
            (self.pizza, self.beer),
        ))
        
        related = self.milk.related.related_to()
        self.assertRelatedEqual(related, (
            (self.sandwich, self.milk),
        ))
        
        related = self.pizza.related.related_to()
        self.assertRelatedEqual(related, (
            (self.soda, self.pizza),
        ))

    def test_manager_methods(self):
        self.pizza.related.connect(self.soda)
        rel_obj = RelatedObject.objects.all()[0] # grab the new related obj
        
        self.cereal.related.connect(self.milk)
        
        new_rel_obj = RelatedObject(object=self.beer)
        
        self.pizza.related.add(new_rel_obj)
        self.assertRelatedEqual(self.pizza.related.all(), (
            (self.pizza, self.beer),
            (self.pizza, self.soda),
        ))
        
        self.pizza.related.remove(rel_obj)
        self.assertRelatedEqual(self.pizza.related.all(), (
            (self.pizza, self.beer),
        ))
        
        self.pizza.related.clear()
        self.assertRelatedEqual(self.pizza.related.all(), ())
        
        # make sure clearing the pizza objects didn't affect cereal
        self.assertRelatedEqual(self.cereal.related.all(), (
            (self.cereal, self.milk),
        ))
        
        self.assertEqual(RelatedObject.objects.count(), 1)
    
    def test_model_level(self):
        self.pizza.related.connect(self.beer)
        self.cereal.related.connect(self.milk)
        
        self.mario.related.connect(self.pizza)
        self.sam.related.connect(self.beer)
        self.soda.related.connect(self.pizza)
        
        self.assertRelatedEqual(Food.related.all(), (
            (self.cereal, self.milk),
            (self.pizza, self.beer),
        ))
        
        self.assertRelatedEqual(Beverage.related.all(), (
            (self.soda, self.pizza),
        ))
        
        self.assertRelatedEqual(Person.related.all(), (
            (self.sam, self.beer),
            (self.mario, self.pizza),
        ))
    
    def test_custom_connect(self):
        self.pizza.related_beverages.connect(self.soda)
        self.pizza.related_beverages.connect(self.beer)
        
        related = self.pizza.related_beverages.all()
        self.assertRelatedEqual(related, (
            (self.pizza, self.beer),
            (self.pizza, self.soda),
        ), 'food', 'beverage')
        
        self.sandwich.related_beverages.connect(self.soda)
        self.sandwich.related_beverages.connect(self.milk)
        
        related = self.sandwich.related_beverages.all()
        self.assertRelatedEqual(related, (
            (self.sandwich, self.milk),
            (self.sandwich, self.soda),
        ), 'food', 'beverage')
        
        related = self.cereal.related_beverages.all()
        self.assertRelatedEqual(related, ())

    def test_custom_model_manager(self):
        self.pizza.related_beverages.connect(self.soda)
        rel_obj = RelatedBeverage.objects.all()[0] # grab the new related obj
        
        self.cereal.related_beverages.connect(self.milk)
        
        new_rel_obj = RelatedBeverage(beverage=self.beer)
        
        self.pizza.related_beverages.add(new_rel_obj)
        self.assertRelatedEqual(self.pizza.related_beverages.all(), (
            (self.pizza, self.beer),
            (self.pizza, self.soda),
        ), 'food', 'beverage')
        
        self.pizza.related_beverages.remove(rel_obj)
        self.assertRelatedEqual(self.pizza.related_beverages.all(), (
            (self.pizza, self.beer),
        ), 'food', 'beverage')
        
        self.pizza.related_beverages.clear()
        self.assertRelatedEqual(self.pizza.related_beverages.all(), ())
        
        # make sure clearing the pizza objects didn't affect cereal
        self.assertRelatedEqual(self.cereal.related_beverages.all(), (
            (self.cereal, self.milk),
        ), 'food', 'beverage')
        
        self.assertEqual(RelatedBeverage.objects.count(), 1)
    
    def test_custom_model_level(self):
        self.pizza.related_beverages.connect(self.soda)
        self.pizza.related_beverages.connect(self.beer)
        self.sandwich.related_beverages.connect(self.soda)
        self.cereal.related_beverages.connect(self.milk)
        
        self.assertRelatedEqual(Food.related_beverages.all(), (
            (self.cereal, self.milk),
            (self.sandwich, self.soda),
            (self.pizza, self.beer),
            (self.pizza, self.soda),
        ), 'food', 'beverage')
