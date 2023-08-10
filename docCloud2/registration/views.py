from django.shortcuts import render , redirect
from django.http import HttpResponse , HttpResponseRedirect
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from container_management.decorators import user_is_authenticated 
from django.contrib.auth.models import User 
from .models import UserActionLog




def login_view(request):   
    if request.method == 'POST':
        # Get the username and password from the request
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log in the user and redirect to the home page
            login(request, user)
            logUserAction_view(request , {'action':'Login'})
            message = "Login successfully.."
            messages.info(request, message)
            return HttpResponseRedirect('/')
        else:
            # Show an error message if authentication fails
            message = "Invalid login credentials"
            messages.warning(request, message)
            return HttpResponseRedirect('/login/')
    else:
        error_message = None
        
    # Render the login page with the error message
    return render(request, 'login.html', {'error_message': error_message})




def logout_view(request):
    logUserAction_view( request, {'action':'Logout'})
    logout(request)
    message = "Logout successfully.."
    messages.info(request, message)
    return HttpResponseRedirect('/login/')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email= request.POST.get('email')
        password = request.POST.get('password')
        User.objects.create_user(username, email, password)
        logUserAction_view(request , {'action':'SignUp'})
        message = "User Created Successfully"
        messages.info(request, message)
        return redirect('index')
    else:
        return render(request , 'signup.html' , {})


@user_is_authenticated
def dashboard_view(request):
    return render(request, 'dashboard.html', {})



@user_is_authenticated
def edit_profile_view(request):
    if request.method == 'POST':
        # Process the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Update the user's profile information
        user = request.user
        user.username = username
        user.email = email
        if password:
            user.set_password(password)
        user.save()
        logUserAction_view(request , {'action':'Edit Profile'})
        message = "User Information Edited Successfully"
        messages.info(request, message)
        login(request, user)
        return redirect('index')
    else:
        # Render the edit profile form
        user = request.user
        context = {
            'username': user.username,
            'email': user.email,
        }
        return render(request, 'edit_profile.html', context)
    

def logUserAction_view(request,Useraction):
    if request.user.is_authenticated: 
        action =  Useraction['action']
        new_log = UserActionLog(
            action= action,
            user= request.user, 
            )
        new_log.save()  






