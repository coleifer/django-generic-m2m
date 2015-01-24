# -*- coding: utf-8 -*-
import django
try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from sys import version_info
from genericm2m import PY3, unicode, str

class GFKOptimizedQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        # pop the gfk_field from the kwargs if its passed in explicitly
        self._gfk_field = kwargs.pop('gfk_field', None)

        # call the parent class' initializer
        super(GFKOptimizedQuerySet, self).__init__(*args, **kwargs)

    def _clone(self, *args, **kwargs):
        clone = super(GFKOptimizedQuerySet, self)._clone(*args, **kwargs)
        clone._gfk_field = self._gfk_field
        return clone

    def get_gfk(self):
        if not self._gfk_field:
            for field in self.model._meta.virtual_fields:
                if isinstance(field, GenericForeignKey):
                    self._gfk_field = field
                    break

        return self._gfk_field

    def generic_objects(self, model=None):
        clone = self._clone()

        ctypes_and_fks = {}

        gfk_field = self.get_gfk()
        ctype_field = '%s_id' % gfk_field.ct_field
        fk_field = gfk_field.fk_field

        for obj in clone:
            ctype = ContentType.objects.get_for_id(getattr(obj, ctype_field))
            obj_id = getattr(obj, fk_field)

            ctypes_and_fks.setdefault(ctype, [])
            ctypes_and_fks[ctype].append(obj_id)

        gfk_objects = {}
        for ctype, obj_ids in ctypes_and_fks.items():
            gfk_objects[ctype.pk] = ctype.model_class()._default_manager.in_bulk(obj_ids)

        obj_list = []
        for obj in clone:
            obj = gfk_objects[getattr(obj, ctype_field)][getattr(obj, fk_field)]
            if not model or (model and isinstance(obj, model)):
                obj_list.append(obj)

        return obj_list


class RelatedObjectsDescriptor(object):
    def __init__(self, model=None, from_field='parent', to_field='object'):
        self.related_model = model or RelatedObject
        self.from_field = self.get_related_model_field(from_field)
        self.to_field = self.get_related_model_field(to_field)

    def get_related_model_field(self, field_name):
        opts = self.related_model._meta
        for virtual_field in opts.virtual_fields:
            if virtual_field.name == field_name:
                return virtual_field
        return opts.get_field(field_name)

    def is_gfk(self, field):
        return isinstance(field, GenericForeignKey)

    def get_query_for_field(self, instance, field):
        if self.is_gfk(field):
            ctype = ContentType.objects.get_for_model(instance)
            return {
                field.ct_field: ctype,
                field.fk_field: instance.pk
            }
        elif isinstance(instance, field.rel.to):
            return {field.name: instance}

        raise TypeError(u'Unable to query %s with %s' % (field, instance))

    def get_query_from(self, instance):
        return self.get_query_for_field(instance, self.from_field)

    def get_query_to(self, instance):
        return self.get_query_for_field(instance, self.to_field)

    def contribute_to_class(self, cls, name):
        self.name = name
        self.model_class = cls
        setattr(cls, self.name, self)

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        ManagerClass = type(self.related_model._default_manager)
        return self.create_manager(instance, ManagerClass)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("Manager must be accessed via instance")

        manager = self.__get__(instance)
        manager.add(*value)

    def delete_manager(self, instance):
        return self.create_manager(instance,
                self.related_model._base_manager.__class__)

    def create_manager(self, instance, superclass, cf_from=True):
        rel_obj = self
        if cf_from:
            core_filters = self.get_query_from(instance)
            rel_field = self.to_field
        else:
            core_filters = self.get_query_to(instance)
            rel_field = self.from_field
        uses_gfk = self.is_gfk(rel_field)

        class RelatedManager(superclass):
            def get_queryset(self):
                if uses_gfk:
                    qs = GFKOptimizedQuerySet(self.model, gfk_field=rel_field)
                    return qs.filter(**(core_filters))
                else:
                    if django.VERSION < (1, 6):
                        method = superclass.get_query_set
                    else:
                        method = superclass.get_queryset

                    return method(self).filter(**(core_filters))

            if django.VERSION < (1, 6):
                get_query_set = get_queryset

            def add(self, *objs):
                for obj in objs:
                    if not isinstance(obj, self.model):
                        raise TypeError(u"'%s' instance expected" % self.model._meta.object_name)
                    if not PY3:
                        for (k, v) in core_filters.iteritems():
                            setattr(obj, k, v)
                    else:
                        for (k, v) in core_filters.items():
                            setattr(obj, k, v)
                    obj.save()
            add.alters_data = True

            def create(self, **kwargs):
                kwargs.update(core_filters)
                return super(RelatedManager, self).create(**kwargs)
            create.alters_data = True

            def get_or_create(self, **kwargs):
                kwargs.update(core_filters)
                return super(RelatedManager, self).get_or_create(**kwargs)
            get_or_create.alters_data = True

            def remove(self, *objs):
                for obj in objs:
                    # Is obj actually part of this descriptor set?
                    if obj in self.all():
                        obj.delete()
                    else:
                        raise rel_obj.related_model.DoesNotExist(
                            u"%r is not related to %r." % (obj, instance))
            remove.alters_data = True

            def clear(self):
                self.all().delete()
            clear.alters_data = True

            def connect(self, obj, **kwargs):
                kwargs.update(rel_obj.get_query_to(obj))
                connection, created = self.get_or_create(**kwargs)
                return connection

            def related_to(self):
                mgr = rel_obj.create_manager(instance, superclass, False)
                return mgr.filter(
                    **rel_obj.get_query_to(instance)
                )

            def symmetrical(self):
                if django.VERSION < (1, 6):
                    method = superclass.get_query_set
                else:
                    method = superclass.get_queryset
                return method(self).filter(
                    Q(**rel_obj.get_query_from(instance)) |
                    Q(**rel_obj.get_query_to(instance))
                ).distinct()

        manager = RelatedManager()
        manager.core_filters = core_filters
        manager.model = self.related_model

        return manager

    def all(self):
        if self.is_gfk(self.from_field):
            ctype = ContentType.objects.get_for_model(self.model_class)
            query = {self.from_field.ct_field: ctype}
        else:
            query = {}
        return self.related_model._default_manager.filter(**query)


class BaseGFKRelatedObject(models.Model):
    """
    A generic many-to-many implementation where diverse objects are related
    across a single model to other diverse objects -> using a dual GFK
    """
    # SOURCE OBJECT:
    parent_type = models.ForeignKey(ContentType, related_name="child_%(class)s")
    parent_id = models.IntegerField(db_index=True)
    parent = GenericForeignKey(ct_field="parent_type", fk_field="parent_id")

    # ACTUAL RELATED OBJECT:
    object_type = models.ForeignKey(ContentType, related_name="related_%(class)s")
    object_id = models.IntegerField(db_index=True)
    object = GenericForeignKey(ct_field="object_type", fk_field="object_id")

    class Meta:
        abstract = True


class RelatedObject(BaseGFKRelatedObject):
    """
    A subclass of BaseGFKRelatedObject which adds two fields used for tracking
    some metadata about the relationship, an alias and the date the relationship
    was created
    """
    alias = models.CharField(max_length=255, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-creation_date',)

    def __unicode__(self):
        return unicode(u'%s related to %s ("%s")' % (self.parent, self.object, self.alias))
