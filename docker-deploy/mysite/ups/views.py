from django.shortcuts import render
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

# Create your views here.
def show_index(request):
    """
    Show the index for the web app
    """
    return render(request, 'ups/index.html')

def show_generic(request):
    return render(request, 'ups/generic.html')


def show_elements(request):
    return render(request, 'ups/elements.html')

@csrf_protect
def user_register(request):
    if request.session.get('is_login', None):
        # Cannot register when logged in
        return redirect("/index")
    if request.method == "POST":
        register_form = UserForm(data=request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            # Check if password same
            if password1 != password2:
                message = "Please enter the same password"
                return render(request, 'ups/register.html', locals())
            else:
                # Check username
                same_name_user = User.objects.filter(username=username)
                if same_name_user: 
                    message = 'User already exist'
                    return render(request, 'ups/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                # Check email
                if same_email_user: 
                    message = 'Email already exist'
                    return render(request, 'ups/register.html', locals())
                new_user = User.objects.create()
                new_user.username = username
                new_user.password = password1
                new_user.email = email
                new_user.save()
                # We should test the user whether the register is success or not.
                return HttpResponseRedirect(reverse('ups:login'))
                return redirect('/login') 

    register_form = UserForm()
    return render(request, 'ups/register.html', locals())

    '''
    """
    A view to provide the form for user to register.
    """
    if request.method == 'POST':
        # Get the form.
        form = UserForm(data=request.POST)
        if form.is_valid():
            # We should save it as a user object.
            user = form.save()
            # Set its password.
            user.set_password(user.password)
            user.save()
            # We should test the user whether the register is success or not.
            return HttpResponseRedirect(reverse('ups:login'))
        else:
            # There are errors inside the fields.
            print(form.errors)

    else:
        # Display the form for register.
        form = UserForm()
    
    return render(request, 'ups/register.html', {'form': form})
    '''
@csrf_protect
def user_login(request):
    if request.session.get('is_login',None):
        return redirect('/index')

    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index')
                else:
                    message = "Wrong password！"
            except:
                message = "User do not exist！"
        return render(request, 'ups/login.html', locals())

    login_form = LoginForm()
    return render(request, 'ups/login.html', locals())


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('ups:index'))