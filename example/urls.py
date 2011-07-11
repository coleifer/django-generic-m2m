from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('completion.urls')),
    url(r'^blog/', include('basic.blog.urls')),
    url(r'^media/', include('basic.media.urls.photos')),
    url(r'^people/', include('basic.people.urls')),
    url(r'^places/', include('basic.places.urls')),
    url(r'^$', 'site_app.views.create_post'),
)
