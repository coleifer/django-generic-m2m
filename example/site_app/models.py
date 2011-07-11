from listeners import start_listening
from providers import *

from basic.blog.models import Post
from genericm2m.utils import monkey_patch


# monkey patch the Post model with a related objects descriptor
monkey_patch(Post, 'related')

# configure our signal handlers so we can update the autocomplete index on
# model save & delete
start_listening()
