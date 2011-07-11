from django.db.models.signals import post_save, post_delete

from completion import site, UnknownObjectException


def update_obj(sender, instance, created, **kwargs):
    try:
        site.get_provider(instance)
        site.remove_object(instance)
        site.store_object(instance)
    except UnknownObjectException:
        pass

def remove_obj(sender, instance, **kwargs):
    try:
        site.get_provider(instance)
        site.remove_object(instance)
    except UnknownObjectException:
        pass


def start_listening():
    post_save.connect(update_obj)
    post_delete.connect(remove_obj)
