from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from genericm2m.models import RelatedObject, RelatedObjectsDescriptor, GFKOptimizedQuerySet
from genericm2m.genericm2m_tests.models import (
    Food, Beverage, Person, RelatedBeverage, Boring, AnotherRelatedObject, Note
)


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
        
        self.table = Boring.objects.create(name='table')
        self.chair = Boring.objects.create(name='chair')
    
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
        
        self.sandwich.related.connect(self.table)
        
        related = self.sandwich.related.all()
        self.assertRelatedEqual(related, (
            (self.sandwich, self.table),
            (self.sandwich, self.milk),
            (self.sandwich, self.soda),
        ))
    
    def test_related_to(self):
        self.pizza.related.connect(self.soda)
        self.pizza.related.connect(self.beer)
        self.pizza.related.connect(self.table)
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
    
    def test_generic_traversal(self):
        self.pizza.related.connect(self.beer)
        self.pizza.related.connect(self.soda)
        self.pizza.related.connect(self.mario)
        
        related = self.pizza.related.all()
        self.assertEqual(type(related), GFKOptimizedQuerySet)
        
        objects = related.generic_objects()
        self.assertEqual(objects, [self.mario, self.soda, self.beer])
    
    def test_filtering(self):
        self.pizza.related.connect(self.beer, alias='bud lite')
        self.pizza.related.connect(self.soda, alias='pepsi')
        self.pizza.related.connect(self.mario)
        
        rel_qs = self.pizza.related.filter(alias='bud lite')
        self.assertRelatedEqual(rel_qs, (
            (self.pizza, self.beer),
        ))
        
        rel_qs = self.pizza.related.filter(object_type=ContentType.objects.get_for_model(Beverage))
        self.assertRelatedEqual(rel_qs, (
            (self.pizza, self.soda),
            (self.pizza, self.beer),
        ))
        
        rel_qs = self.beer.related.related_to().filter(alias='bud lite')
        self.assertRelatedEqual(rel_qs, (
            (self.pizza, self.beer),
        ))
        
    def test_custom_model_using_gfks(self):
        self.note_a = Note.objects.create(content='a')
        self.note_b = Note.objects.create(content='b')
        self.note_c = Note.objects.create(content='c')
        
        self.note_a.related.connect(self.pizza)
        self.note_a.related.connect(self.note_b)
        
        self.note_b.related.connect(self.cereal, alias='cereal note', description='lucky charms!')
        self.note_b.related.connect(self.milk, alias='milk note', description='goes good with cereal')
        
        queryset = self.note_a.related.all()
        self.assertEqual(queryset.model, AnotherRelatedObject)
        self.assertTrue(isinstance(queryset, GFKOptimizedQuerySet))
        
        related_a = self.note_a.related.all()
        self.assertRelatedEqual(related_a, (
            (self.note_a, self.pizza),
            (self.note_a, self.note_b),
        ))
        
        related_b = self.note_b.related.all()
        self.assertRelatedEqual(related_b, (
            (self.note_b, self.cereal),
            (self.note_b, self.milk),
        ))
        
        cereal_rel, milk_rel = related_b
        
        self.assertEqual(cereal_rel.alias, 'cereal note')
        self.assertEqual(cereal_rel.description, 'lucky charms!')
        
        self.assertEqual(milk_rel.alias, 'milk note')
        self.assertEqual(milk_rel.description, 'goes good with cereal')
        
        self.assertRelatedEqual(self.note_b.related.filter(alias='cereal note'), (
            (self.note_b, self.cereal),
        ))
        
        related_c = self.note_c.related.all()
        self.assertRelatedEqual(related_c, ())
        
        self.assertEqual(related_a.generic_objects(), [
            self.pizza, self.note_b
        ])
        
        self.assertEqual(related_b.generic_objects(), [
            self.cereal, self.milk
        ])
        
        self.assertEqual(related_c.generic_objects(), [])
