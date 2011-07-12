from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from forms import PhotoForm, PostForm


def generic_completion_view(request, form_class, template):
    form = form_class(request.POST or None, request.FILES or None)
    
    if request.method == 'POST' and form.is_valid():
        # save the new object instance
        new_obj = form.save()
        
        # grab the related objects from the form and add them
        # to the new post instance
        for obj in form.cleaned_data['hidden_relationships']:
            new_obj.related.connect(obj)
        
        return redirect(new_obj)
    
    return render_to_response(template, {'form': form},
        context_instance=RequestContext(request))

def create_photo(request):
    return generic_completion_view(request, PhotoForm, 'media/create_photo.html')

def create_post(request):
    return generic_completion_view(request, PostForm, 'blog/create_post.html')
