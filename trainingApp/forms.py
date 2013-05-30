from django.utils.translation import ugettext as _
from django import forms
from django.contrib.auth.models import User
from models import Author, Post, Category, Comment


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['avatar']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class LoginForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput, )

    class Meta:
        model = User
        fields = ['email', 'password']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text_title', 'text_body', 'category', 'date_pub']


class CommentAuthorForm(forms.ModelForm):
    content = forms.CharField(label=_('Comment'))

    class Meta:
        model = Comment
        fields = ['content', 'parent_id', 'parent_type']


class CommentAnonymousForm(forms.ModelForm):
    tmp_name = forms.CharField(label=_('Name'))
    tmp_mail = forms.EmailField(label=_('Mail'), help_text=_('Need for Validation'))
    content = forms.CharField(label=_('Comment'))

    class Meta:
        model = Comment
        fields = ['tmp_name', 'tmp_mail', 'content', 'parent_id', 'parent_type']


class UserPasswordForm(forms.ModelForm):
    password = forms.CharField(_('Password'), widget=forms.PasswordInput, )
    password_check = forms.CharField(_('Password (Again)'), widget=forms.PasswordInput, )

    class Meta:
        model = User
        fields = ['password', 'password_check']

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


class UserEmailForm(forms.ModelForm):
    email = forms.EmailField(label=_('Email'), help_text='Must be valid for activation.', )

    class Meta:
        model = User
        fields = ['email']

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


class UserForm(UserPasswordForm, UserEmailForm):
    username = forms.CharField(label=_('Username'), )
    email = forms.EmailField(label=_('Email'), help_text='Must be valid for activation.', )

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