from django.shortcuts import render
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .models import *

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

    register_form = UserForm()
    return render(request, 'ups/register.html', locals())

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
                    request.session['user_name'] = user.username
                    return redirect('/index')
                else:
                    message = "Wrong password！"
            except:
                message = "User do not exist！"
        return render(request, 'ups/login.html', locals())

    login_form = LoginForm()
    return render(request, 'ups/login.html', locals())


def user_logout(request):
    if not request.session.get('is_login', None):
        # If not logged in, no need to log out
        return redirect('/index')
    #logout(request)
    request.session.flush()
    return HttpResponseRedirect(reverse('ups:index'))


@csrf_protect
def track_package(request):
    if request.method == "POST":
        track_package_form = TrackPackageForm(request.POST)
        if track_package_form.is_valid():
            tracking_number = track_package_form.cleaned_data['tracking_number']
            if Package.objects.filter(tracking_num = tracking_number).count() == 0:               
                messages.error(request, 'The tracking number you entered is not valid. Please input again or contact the sender to verify the number.')
                track_package_form = TrackPackageForm()
                return render(request, 'ups/track_package.html', {'track_package_form': track_package_form})
               # return render(request, 'ups/track_package.html', locals())          
            context = {
                'package' : Package.objects.get(tracking_num = tracking_number)
            }
            #TODO: Need to change the render later.
            return render(request, 'ups/show_track_result.html', context)
        return render(request, 'ups/track_package.html', locals())
    track_package_form = TrackPackageForm(request.POST)
    return render(request, 'ups/track_package.html', locals())


@csrf_protect
def see_packages(request):
    #Users can access this function only after they log in.
    if not request.session.get('is_login',None):  
        return redirect('/login')
    else:
        request_user = User.objects.get(username=request.session.get('user_name', None))
        context = {
            'packages' : Package.objects.filter(user = request_user)
        }
        return render(request, 'ups/see_packages.html', context)

@csrf_protect
def modify_destination_x(request, package_id):
    if request.method == "POST":
        modify_destination_x_form = ModifyDestinationXForm(request.POST, instance = Package.objects.filter(id = package_id)[0])
        if modify_destination_x_form.is_valid():
          modify_destination_x_form.save()
          return redirect('/see_packages')
    else:
        modify_destination_x_form = ModifyDestinationXForm()
    return render(request, 'ups/modify_destination_x.html', {'modify_destination_x_form': modify_destination_x_form})

@csrf_protect
def modify_destination_y(request, package_id):
    if request.method == "POST":
        modify_destination_y_form = ModifyDestinationYForm(request.POST, instance = Package.objects.filter(id = package_id)[0])
        if modify_destination_y_form.is_valid():
          modify_destination_y_form.save()
          return redirect('/see_packages')
    else:
        modify_destination_y_form = ModifyDestinationYForm()
    return render(request, 'ups/modify_destination_y.html', {'modify_destination_y_form': modify_destination_y_form})


@csrf_protect
def see_products(request, package_id):
    package = Package.objects.filter(id = package_id)[0]
    context = {
        'products' : package.product_set.all()
    }
    return render(request, 'ups/see_products.html', context)
