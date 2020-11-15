from django import forms


class FileForm(forms.Form):
    TYPE_CHOICE = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit')
    ]
    file = forms.FileField()
    keywords_type = forms.ChoiceField(label="Debit or Credit", choices=TYPE_CHOICE)
    keywords_to = forms.CharField(label="To")
    keywords_amount = forms.IntegerField(label="Amount")
    keywords_date = forms.DateField(label="Date")
    keywords_bank = forms.CharField(label="Bank")


class ConsultantFileForm(forms.Form):
    TYPE_CHOICE = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit')
    ]

    file = forms.FileField()
    keywords_type = forms.ChoiceField(label="Debit or Credit", choices=TYPE_CHOICE)
    keywords_to = forms.CharField(label="To")
    keywords_amount = forms.IntegerField(label="Amount")
    keywords_date = forms.DateField(label="Date")
    keywords_bank = forms.CharField(label="Bank")

    def __init__(self, user_list, *args, **kwargs):
        CHOICES = []
        for user in user_list:
            CHOICES.append((user['id'], user['name']))
        super(ConsultantFileForm, self).__init__(*args, **kwargs)
        self.fields['encrypt_to'] = forms.ChoiceField(choices=CHOICES)


class SearchForm(forms.Form):
    TYPE_CHOICE = [
        ('', '- - - -'),
        ('Debit', 'Debit'),
        ('Credit', 'Credit')
    ]

    keywords_type = forms.ChoiceField(label="Debit or Credit", choices=TYPE_CHOICE, required=False)
    keywords_to = forms.CharField(label="To", required=False)
    keywords_amount = forms.IntegerField(label="Amount", required=False)
    keywords_date = forms.DateField(label="Date", required=False)
    keywords_bank = forms.CharField(label="Bank", required=False)


class ServerForm(forms.Form):
    server_ip = forms.CharField(label="Server IP", max_length=70)


class UserForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)


class LoginForm(forms.Form):
    private_key = forms.CharField(label="Input your private key here",widget=forms.PasswordInput())