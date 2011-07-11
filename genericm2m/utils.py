from genericm2m.models import RelatedObjectsDescriptor


def monkey_patch(model_class, name='related', descriptor=None):
    rel_obj = descriptor or RelatedObjectsDescriptor()
    rel_obj.contribute_to_class(model_class, name)
    setattr(model_class, name, rel_obj)
    return True
