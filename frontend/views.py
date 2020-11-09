from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from frontend.forms import FileForm, SearchForm, UserForm
from frontend.functions import encryption, search_keywords, keygen, get_consultant
from frontend.models import UserKeys

USERKEYS: UserKeys = None
CONSULTANT: UserKeys = None


# Create your views here.
def home(request):
    """ Homepage of the application """
    if request.user.is_authenticated:
        return render(request, 'frontend/home.html', locals())
    else:
        return redirect('login')


def keys_from_file():
    ''' Get the keys from a user.txt file '''
    global USERKEYS, CONSULTANT

    if USERKEYS is None:
        raise Exception("PASS")
        json_object = UserKeys.get_from_file()
        USERKEYS = UserKeys(json_object['id'], json_object['username'], json_object['public_key'], json_object['private_key'])

        # Create consultant
        consultant_key, consultant_id = get_consultant()
        CONSULTANT = UserKeys(consultant_id, "consultant", consultant_key, "noonecares")
        print(USERKEYS, CONSULTANT)


@login_required
def upload_file(request):
    global USERKEYS, CONSULTANT
    keys_from_file()

    ''' Upload a file onto the server '''
    form = FileForm(request.POST or None, request.FILES)
    upload = False

    if form.is_valid():
        # file_encrypt must be a string
        file_e = form.cleaned_data['file']
        file_encrypt = file_e.read()
        
        # TODO : modify keywords form field
        keywords_to = form.cleaned_data['keywords_to']  # TODO : check if empty forms create empty string
        # keywords_from = form.cleaned_data['keywords_from']
        # keywords_date = form.cleaned_data['keywords_date'].strftime("%d %m %Y")
        keywords = [keywords_to]  # [keywords_to, keywords_from, keywords_date]
        print(keywords)

        # The list of public keys of the users we want to encrypt the file for (i.e. author + consultant)
        public_keys = [USERKEYS.public_key]  #, CONSULTANT.public_key]
        public_ids = [USERKEYS.id]  #, CONSULTANT.id]

        encryption(file_encrypt, keywords, public_keys, public_ids, USERKEYS.secret_key)  # Empty function performing the encryption of the file and sending it to the server
        upload = True

        form = FileForm()

    return render(request, 'frontend/upload.html', locals())


@login_required
def search_files(request):
    ''' Search keywords among encrypted files '''
    global USERKEYS, CONSULTANT
    keys_from_file()

    form = SearchForm(request.POST or None)
    search = False

    if form.is_valid():
        # Generate the keywords
        keywords_to = form.cleaned_data['keywords_to']
        keywords_from = form.cleaned_data['keywords_from']

        if form.cleaned_data['keywords_date'] is None:
            keywords_date = ""
        else:
            keywords_date = form.cleaned_data['keywords_date'].strftime("%d %m %Y")

        keywords = [keywords_to] #, keywords_from, keywords_date]
        print(keywords)

        # Perform the search => send to the server
        files = search_keywords(keywords, USERKEYS.secret_key, USERKEYS.id) 
        search = True
    
    return render(request, 'frontend/search.html', locals())    


# QUESTIONS
# How is the KeyGen performed ? How are the keys distributed ?
# How is the server setup ? How do we communicate with it ?
# When are the keywords generated ? Before or after we upload a form ?
# What to do with the local decrypted files



def create_account(request):
    global USERKEYS, CONSULTANT

    form = UserForm(request.POST or None)
    if form.is_valid():
        if form.cleaned_data['username'] != 'consultant':
            # Create the User object
            new_user = form.save()

        # Contact the server to get the global param and compute the pair of keys
        public_key, secret_key, user_id = keygen(form.cleaned_data['username'])

        # Save the user information in a JSON file
        USERKEYS = UserKeys(user_id, form.cleaned_data['username'], public_key, secret_key)
        USERKEYS.save_to_file()

        # Create consultant
        consultant_key, consultant_id = get_consultant()
        CONSULTANT = UserKeys(consultant_id, "consultant", consultant_key, "noonecares")

        # Redirect to the login page
        return redirect('frontend:home')

    return render(request, 'frontend/sign.html', locals())