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
        """
        Connect model instances to various other model instances, then query
        the manager and check the queryset returned is correct
        """
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
        """
        Check the back-side of the double-GFK, note: this only works on objects
        that have a RelatedObjectsDescriptor() pointing to the same model
        class, in this case the default `RelatedObject`
        """
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

    def test_symmetrical(self):
        self.pizza.related.connect(self.soda)
        self.pizza.related.connect(self.beer)
        self.pizza.related.connect(self.table)
        self.sandwich.related.connect(self.soda)
        self.sandwich.related.connect(self.milk)
        self.mario.related.connect(self.soda)
        self.soda.related.connect(self.pizza)

        related = self.soda.related.symmetrical().order_by('id')
        self.assertRelatedEqual(related, (
            (self.pizza, self.soda),
            (self.sandwich, self.soda),
            (self.mario, self.soda),
            (self.soda, self.pizza),
        ))

        related = self.beer.related.symmetrical()
        self.assertRelatedEqual(related, (
            (self.pizza, self.beer),
        ))

    def test_manager_methods(self):
        """
        Since the RelatedObjectsDescriptor behaves like a dynamic manager (much
        the same as Django's ForeignRelatedObjectsDescriptor) test to ensure
        that the manager behaves as expected and correctly implements all the
        basic FK methods
        """
        # connect pizza to soda and grab the newly-created RelatedObject
        self.pizza.related.connect(self.soda)
        rel_obj = RelatedObject.objects.all()[0]

        # connect cereal to milk (this is just to make sure that anything
        # modified on one Food object doesn't affect another Food object
        self.cereal.related.connect(self.milk)

        # create a new RelatedObject but do not save it yet -- note that it does
        # not have `parent_object` set
        new_rel_obj = RelatedObject(object=self.beer)

        # add this related object to pizza, parent_object gets set and it will
        # show up in the queryset as expected
        self.pizza.related.add(new_rel_obj)
        self.assertRelatedEqual(self.pizza.related.all(), (
            (self.pizza, self.beer),
            (self.pizza, self.soda),
        ))

        # remove the original RelatedObject `rel_obj`, which was the connection
        # from pizza -> soda
        self.pizza.related.remove(rel_obj)
        self.assertRelatedEqual(self.pizza.related.all(), (
            (self.pizza, self.beer),
        ))

        # make sure clearing pizza's related queryset works
        self.pizza.related.clear()
        self.assertRelatedEqual(self.pizza.related.all(), ())

        # make sure clearing the pizza objects didn't affect cereal
        self.assertRelatedEqual(self.cereal.related.all(), (
            (self.cereal, self.milk),
        ))

        # there should be just one row in the table
        self.assertEqual(RelatedObject.objects.count(), 1)

    def test_model_level(self):
        """
        The RelatedObjectsDescriptor can work at the class-level as well and
        applies to all instances of the model - check that when connections are
        made between individual instances and then are queried via the class,
        that all connections are returned from that model type
        """
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
        """
        Mimic the test_connect() method, but instead use the custom descriptor,
        `related_beverages` which goes through the RelatedBeverage model
        """
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
        """
        Mimic the test_model_manager() method, but instead use the custom
        descriptor and through model
        """
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
        """
        And lastly, test that the custom descriptor/through-model work as
        expected at the model-level (previous tests were instance-level)
        """
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
        """
        Ensure that the RelatedObjectsDescriptor returns a GFKOptimizedQuerySet
        when the through model contains a GFK -- also check that the queryset's
        optimized lookup works as expected
        """
        self.pizza.related.connect(self.beer)
        self.pizza.related.connect(self.soda)
        self.pizza.related.connect(self.mario)

        # the manager returns instances of GFKOptimizedQuerySet
        related = self.pizza.related.all()
        self.assertEqual(type(related), GFKOptimizedQuerySet)

        # check the queryset is using the right field
        self.assertEqual(related.get_gfk().name, 'object')

        # the custom queryset's optimized lookup works correctly
        objects = related.generic_objects()
        self.assertEqual(objects, [self.mario, self.soda, self.beer])

        # check the reverse does not hold, documenting existing behavior since
        # it looks at only the "default" manager on the back-side
        related = self.soda.related.related_to()
        self.assertEqual(type(related), GFKOptimizedQuerySet)

        # check the queryset is using the right field
        self.assertEqual(related.get_gfk().name, 'parent')

        # the custom queryset's optimized lookup works correctly
        objects = related.generic_objects()
        self.assertEqual(objects, [self.pizza])

    def test_filtering(self):
        """
        Check that filtering on RelatedObject fields (or through model fields)
        works as expected
        """
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
        """
        Check that using a custom through model with GFKs works as expected
        (looking at models.py, Note uses `AnotherRelatedObject` as its through)
        """
        self.note_a = Note.objects.create(content='a')
        self.note_b = Note.objects.create(content='b')
        self.note_c = Note.objects.create(content='c')

        self.note_a.related.connect(self.pizza)
        self.note_a.related.connect(self.note_b)

        self.pizza.related.connect(self.note_b)

        # create some notes with custom attributes
        self.note_b.related.connect(self.cereal, alias='cereal note', description='lucky charms!')
        self.note_b.related.connect(self.milk, alias='milk note', description='goes good with cereal')

        # ensure that the queryset is using the correct model and automatically
        # determines that a GFKOptimizedQuerySet can be used
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

        related_to = self.note_b.related.related_to()
        # note that pizza does not show up here even though it is related to note b
        # this is because that relationship was stored in a different table (RelatedObject)
        # as opposed to AnotherRelatedObject
        self.assertEqual(related_to.generic_objects(), [self.note_a])

        cereal_rel, milk_rel = related_b

        # check that the custom attributes were saved correctly
        self.assertEqual(cereal_rel.alias, 'cereal note')
        self.assertEqual(cereal_rel.description, 'lucky charms!')

        self.assertEqual(milk_rel.alias, 'milk note')
        self.assertEqual(milk_rel.description, 'goes good with cereal')

        # check that we can filter on fields as expected
        self.assertRelatedEqual(self.note_b.related.filter(alias='cereal note'), (
            (self.note_b, self.cereal),
        ))

        related_c = self.note_c.related.all()
        self.assertRelatedEqual(related_c, ())

        # lastly, check that the GFKOptimizedQuerySet returns the expected
        # results when doing the optimized lookup
        self.assertEqual(related_a.generic_objects(), [
            self.pizza, self.note_b
        ])

        self.assertEqual(related_b.generic_objects(), [
            self.cereal, self.milk
        ])

        self.assertEqual(related_c.generic_objects(), [])

    def test_generic_objects_filtered(self):
        """
        Get generic objects filtered by Model.
        """
        self.pizza.related.connect(self.beer)
        self.pizza.related.connect(self.soda)
        self.pizza.related.connect(self.mario)

        # Get all generic related content
        related = self.pizza.related.all()
        objects = related.generic_objects()
        self.assertEqual(objects, [self.mario, self.soda, self.beer])

        # Get Person generic related content only.
        related = self.pizza.related.all()
        objects = related.generic_objects(Person)
        self.assertEqual(objects, [self.mario])
