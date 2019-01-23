from django import forms
from django.contrib.auth.models import User
from django.db import models
from grumblr.models import *
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class LoginForm(forms.Form):
    username = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'username','class':'form-control'}))
    password = forms.CharField(label='',widget=forms.PasswordInput(attrs={'placeholder':'password','class':'form-control'}))

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        password = self.cleaned_data.get('password')
        username = self.cleaned_data.get('username')
        user = authenticate(username=username, password=password)

        if not User.objects.filter(username=username):
            raise forms.ValidationError("Username does not exist.") 
        if user is None:
            raise forms.ValidationError("Password is not correct.")

        return self.cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'username','class':'form-control'}))
    password1 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'placeholder':'password','class':'form-control'}))
    password2 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'placeholder':'confirm password','class':'form-control'}))
    firstname= forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'first name','class':'form-control'}))
    lastname = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'last name','class':'form-control'}))
    email = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'email','class':'form-control'}))

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if password1 != password2:
            raise forms.ValidationError('Passwords did not match.')
        if User.objects.filter(username=username):
            raise forms.ValidationError("Username is already taken.")
        try:
           validate_email(email)
        except ValidationError as e:
           raise forms.ValidationError("Email address is not valid.")

        return self.cleaned_data

class EditProfileForm(forms.Form):
    first_name = forms.CharField(required=False, label='First Name',widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(required=False, label='Last Name',widget=forms.TextInput(attrs={'class':'form-control'}))
    age = forms.IntegerField(required=False, label='Age',widget=forms.TextInput(attrs={'class':'form-control'}))
    bio = forms.CharField(required=False, label='Short Bio',widget=forms.TextInput(attrs={'class':'form-control'}))
    picture = forms.ImageField(required=False, label='Picture', widget=forms.FileInput())

    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()
        age = self.cleaned_data.get('age')

        if age is not None:
            if not type(age) is int or not age >= 0:
                raise forms.ValidationError("Age is not valid.")

        return cleaned_data

class ChangePasswordForm(forms.Form):
    password = forms.CharField(label='',widget=forms.PasswordInput(attrs={'placeholder':'old password','class':'form-control'}))
    password1 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'placeholder':'new password','class':'form-control'}))
    password2 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'placeholder':'confirm new password','class':'form-control'}))

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data

class EmailResetForm(forms.Form):
    username = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'username','class':'form-control'}))
    email = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'email','class':'form-control'}))

    def clean(self):
        cleaned_data = super(EmailResetForm, self).clean()
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if not User.objects.filter(username=username):
            raise forms.ValidationError("User does not exist.") 
        if not User.objects.filter(username=username, email=email):
            raise forms.ValidationError("Email address is not valid.")

        return cleaned_data

class PostForm(forms.Form):
    post = forms.CharField(max_length = 42)

class CommentForm(forms.Form):
    comment = forms.CharField(max_length = 42)
