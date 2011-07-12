from django.conf.urls.defaults import *


urlpatterns = patterns('example.site_app.views',
    url(r'^photo/$', 'create_photo', name='create_photo'),
    url(r'^post/$', 'create_post', name='create_post'),
)
