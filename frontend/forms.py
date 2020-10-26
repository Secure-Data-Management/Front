from django import forms

class FileForm(forms.Form):
    file = forms.FileField()
    keywords = forms.CharField()


class SearchForm(forms.Form):
    keywords = forms.CharField()