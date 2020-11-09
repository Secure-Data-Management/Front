from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class FileForm(forms.Form):
    file = forms.FileField()
    keywords_file = forms.FileField()


class SearchForm(forms.Form):
    keywords = forms.CharField()


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
