from completion import site, DjangoModelProvider

from basic.blog.models import Post
from basic.media.models import Photo
from basic.people.models import Person
from basic.places.models import City, Place


class PostProvider(DjangoModelProvider):
    def get_title(self, obj):
        return obj.title
    
    def get_pub_date(self, obj):
        return obj.publish
    
    def get_data(self, obj):
        return {
            'title': obj.title,
            'url': obj.get_absolute_url(),
        }


class PhotoProvider(DjangoModelProvider):
    def get_title(self, obj):
        return obj.title
    
    def get_pub_date(self, obj):
        return obj.uploaded
    
    def get_data(self, obj):
        return {
            'title': obj.title,
            'url': obj.get_absolute_url(),
        }


class PersonProvider(DjangoModelProvider):
    def get_title(self, obj):
        return obj.full_name
    
    def get_pub_date(self, obj):
        return obj.birth_date
    
    def get_data(self, obj):
        return {
            'title': obj.full_name,
            'url': obj.get_absolute_url(),
        }


class PlaceProvider(DjangoModelProvider):
    def get_title(self, obj):
        return obj.title
    
    def get_pub_date(self, obj):
        return obj.modified
    
    def get_data(self, obj):
        return {
            'title': obj.title,
            'url': obj.get_absolute_url(),
        }


class CityProvider(DjangoModelProvider):
    def get_title(self, obj):
        return unicode(obj)
    
    def get_pub_date(self, obj):
        return None
    
    def get_data(self, obj):
        return {
            'title': unicode(obj),
            'url': obj.get_absolute_url(),
        }


site.register(Post, PostProvider)
site.register(Photo, PhotoProvider)
site.register(Person, PersonProvider)
site.register(Place, PlaceProvider)
site.register(City, CityProvider)
