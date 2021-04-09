from django import forms
from .models import User

class UserForm(forms.ModelForm):
    """
    A form for user to register.
    """
    # Set the form widget to PasswordInput
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', ]


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=40)
    password = forms.CharField(widget=forms.PasswordInput)