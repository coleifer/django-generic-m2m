import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

ADMIN_MEDIA_PREFIX = '/static/admin/'

MEDIA_ROOT = '%s/media/' % (SITE_ROOT)
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    '%s/static/' % (SITE_ROOT),
)

CACHE_BACKEND = 'dummy:///'
CACHE_KEY_PREFIX = 'semtags'
CACHE_MIDDLEWARE_KEY_PREFIX = CACHE_KEY_PREFIX
CACHE_MIDDLEWARE_SECONDS = 60

LOGIN_REDIRECT_URL = '/'

SITE_NAME = 'semtags.com'

DATABASES = {
    'default': {
        'ENGINE'     : 'django.db.backends.sqlite3',
        'HOST'       : '',
        'PORT'       : '',
        'NAME'       : '%s/semtags.db' % SITE_ROOT,
        'USER'       : '',
        'PASSWORD'   : ''
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
SITE_ID = 1
SECRET_KEY = 'gv^gjq&amp;kwrs3uqmd*s-is7%8z7@bc9^#4$txthzx$ta3nrn6(&amp;'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    '%s/templates/' % (SITE_ROOT),
)

AUTOCOMPLETE_BACKEND = 'completion.backends.db_backend.DatabaseAutocomplete'
AUTOCOMPLETE_MIN_WORDS = 1

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'basic.blog',
    'basic.inlines',
    'basic.media',
    'basic.people',
    'basic.places',
    'tagging', # needed by basic
    'completion',
    'genericm2m',
    
    # lastly, just a single app for this site
    'example.site_app',
)
