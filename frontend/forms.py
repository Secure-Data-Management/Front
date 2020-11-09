from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class FileForm(forms.Form):
    file = forms.FileField()
    keywords_to = forms.CharField(label="To", required=False)
    keywords_from = forms.CharField(label="From", required=False)
    keywords_date = forms.DateField(label="Date", required=False)


class ConsultantFileForm(forms.Form):
    file = forms.FileField()
    keywords_to = forms.CharField(label="To", required=False)
    keywords_from = forms.CharField(label="From", required=False)
    keywords_date = forms.DateField(label="Date", required=False)

    def __init__(self, user_list, *args, **kwargs):
        CHOICES = []
        for user in user_list:
            CHOICES.append((user['id'], user['name']))
        super(ConsultantFileForm, self).__init__(*args, **kwargs)
        self.fields['encrypt_to'] = forms.ChoiceField(choices=CHOICES)


class SearchForm(forms.Form):
    keywords_to = forms.CharField(label="To", required=False)
    keywords_from = forms.CharField(label="From", required=False)
    keywords_date = forms.DateField(label="Date", required=False)


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']