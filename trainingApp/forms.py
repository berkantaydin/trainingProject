from django.utils.translation import ugettext as _
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from models import Author


class UserForm(forms.ModelForm):
    username = forms.CharField(_('Username'),)
    password = forms.CharField(_('Password'), widget=forms.PasswordInput,)
    password_check = forms.CharField(_('Password (Again)'), widget=forms.PasswordInput,)
    email = forms.EmailField(_('Email'), help_text='Must be valid for activation.',)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_check', 'email']

    def clean_username(self):
        """
        username is unique ?
        """
        data = self.cleaned_data

        try:
            User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return data['username']
        raise forms.ValidationError(_("This username is already taken"))

    def clean_email(self):
        """
        email is unique ?
        """
        data = self.cleaned_data

        try:
            User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return data['email']
        raise forms.ValidationError(_("This email is already taken"))

    def clean_password_check(self):
        """
        password check
        """
        data = self.cleaned_data

        if not data['password_check']:
            raise forms.ValidationError(_("You must confirm your password"))
        if data['password'] != data['password_check']:
            raise forms.ValidationError(_("Your passwords do not match"))

        return data['password_check']


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['avatar']


class LoginForm(forms.ModelForm):
    password = forms.CharField(_('Password'), widget=forms.PasswordInput,)

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        """
        login
        """
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user_cache = authenticate(email=email, password=password)
            if user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password."))
            elif not user_cache.is_active:
                raise forms.ValidationError(_("This account is not activated, please check your email for activation."))
        return self.cleaned_data

