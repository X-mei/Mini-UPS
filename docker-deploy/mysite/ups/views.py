from django.shortcuts import render
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

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


def login(request):
    """
    A view to provide the form for user to register.
    """
    register_state = False
    if request.method == 'POST':
        # Get the form.
        u_form = UserForm(data=request.POST)
        if u_form.is_valid():
            # We should save it as a user object.
            user = u_form.save()
            # Set its password.
            user.set_password(user.password)
            user.save()
            register_state = True
            # We should test the user whether the register is success or not.
        else:
            # There are errors inside the fields.
            print(u_form.errors)

    else:
        # Display the form for register.
        u_form = UserForm()
    
    return render(request, 'ups/login.html', {'u_form': u_form, 'success': register_state})