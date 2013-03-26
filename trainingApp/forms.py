from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from models import Author


class RegisterForm(UserCreationForm):

    username = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.CharField(max_length=200)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'last_name', 'email')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        password = forms.CharField(max_length=50, );
        exclude = ['is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'groups', 'user_permissions']

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        exclude = ['user']