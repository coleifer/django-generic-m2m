from providers import *

from basic.blog.models import Post
from basic.media.models import Photo
from completion.listeners import start_listening
from genericm2m.utils import monkey_patch


# monkey patch the Post model with a related objects descriptor
monkey_patch(Post)
monkey_patch(Photo)

# configure our signal handlers so we can update the autocomplete index on
# model save & delete
start_listening()
