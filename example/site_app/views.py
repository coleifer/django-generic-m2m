from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from forms import PostForm

from basic.blog.models import Post
from completion import site


def create_post(request):
    form = PostForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        # do some other stuff
        new_post = form.save()
        
        for obj in form.cleaned_data['hidden_relationships']:
            new_post.related.connect(obj)
        
        return redirect(new_post)
    
    return render_to_response('blog/create_post.html', {'form': form},
        context_instance=RequestContext(request))
