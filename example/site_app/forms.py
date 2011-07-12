from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from basic.blog.models import Post
from basic.media.models import Photo


class BaseRelationshipsForm(forms.ModelForm):
    relationships = forms.CharField(required=False)
    hidden_relationships = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def clean_hidden_relationships(self):
        hidden = self.cleaned_data.get('hidden_relationships') or ''
        
        cts_and_ids = [ct_id for ct_id in hidden.split(',') if ct_id.strip()]
        objects = []
        
        for ct_id in cts_and_ids:
            content_type_id, object_id = ct_id.split(':')
            
            ctype = ContentType.objects.get_for_id(int(content_type_id))
            obj = ctype.model_class()._default_manager.get(pk=object_id)
            
            objects.append(obj)
        
        return objects


class SlugifyMixin(object):
    def clean_title(self):
        title = self.cleaned_data.get('title')
        self.instance.slug = slugify(title)
        return title


class PostForm(BaseRelationshipsForm, SlugifyMixin):
    class Meta:
        model = Post
        fields = ('title', 'body',)


class PhotoForm(BaseRelationshipsForm, SlugifyMixin):
    class Meta:
        model = Photo
        fields = ('title', 'photo',)
