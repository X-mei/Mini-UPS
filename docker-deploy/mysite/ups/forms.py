from django import forms
from .models import User

class UserForm(forms.ModelForm):
    """
    A form for user to register.
    """
    # Set the form widget to PasswordInput
    username = forms.CharField(label="Username", max_length=128, widget=forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Username'}))
    password1 = forms.CharField(label="Password1", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form__input', 'placeholder': 'Password'}))
    password2 = forms.CharField(label="Password2", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form__input', 'placeholder': 'Password'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form__input', 'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=128, widget=forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Username'}))
    password = forms.CharField(label="Password", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form__input', 'placeholder': 'Password'}))


class TrackPackageForm(forms.Form):
    package_id = forms.IntegerField(label="Package ID", widget=forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Package ID'}))