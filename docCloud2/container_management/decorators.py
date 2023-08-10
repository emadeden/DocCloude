from functools import wraps
from django.contrib import messages
from django.shortcuts import get_object_or_404 , redirect
from django.http import HttpResponseRedirect , HttpResponse , JsonResponse
from .models import Container





def container_auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, container_id, *args, **kwargs):
        # Get the container object from the database
        container = get_object_or_404(Container, id=container_id)

        # Check if the user is an admin or the container owner
        if request.user.is_staff or container.owner == request.user:
            return view_func(request, container_id, *args, **kwargs)
        else:
            message = "You do not have permission to access this container."
            messages.warning(request, message)
            return HttpResponseRedirect('/')

    return wrapper

def user_is_authenticated(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            message = "You do not have permission to access."
            messages.warning(request, message)
            return HttpResponseRedirect('/login/')
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def is_admin(redirect_url='/'):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_superuser:
                message = "You do not have permission to access."
                messages.warning(request, message)
                return HttpResponseRedirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def is_numeric(field_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            value = request.POST.get(field_name)
            if value is not None and not str(value).isdigit():
                message = f"{field_name.capitalize()} must be a numeric value."
                messages.warning(request, message)
                data = {
                    'success': True,
                    'message': 'Container created successfully',
                    'redirect_url': '/list_images/',  
                }
                return JsonResponse(data)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator



