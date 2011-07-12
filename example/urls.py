from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('completion.urls')),
    url(r'^blog/', include('basic.blog.urls')),
    url(r'^create/', include('example.site_app.urls')), # our custom content creation views
    url(r'^media/', include('basic.media.urls.photos')),
    url(r'^people/', include('basic.people.urls')),
    url(r'^places/', include('basic.places.urls')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
    url(r'^$', 'django.views.generic.simple.direct_to_template', kwargs={'template': 'homepage.html'}),
)
