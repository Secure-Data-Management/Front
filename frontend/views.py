from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from frontend.forms import FileForm, SearchForm, UserForm
from frontend.functions import encryption, search_keywords, keygen
from frontend.models import Profile


# Create your views here.
def home(request):
    ''' Homepage of the application '''
    if request.user.is_authenticated:
        return render(request, 'frontend/home.html', locals())
    else:
        return redirect('login')


@login_required
def upload_file(request):
    ''' Upload a file onto the server '''
    form = FileForm(request.POST or None, request.FILES)
    upload = False

    if form.is_valid():
        # file_encrypt must be a string
        file_e = form.cleaned_data['file']
        file_encrypt = file_e.read()
        
        keywords = form.cleaned_data['keywords'].split(', ')  # TODO : how to split
        print(keywords)

        # The list of public keys of the users we want to encrypt the file for (i.e. author + consultant)
        # TODO : find the key of the consultant
        public_keys = [request.user.profile.public_key]

        encryption(file_encrypt, keywords, public_keys)  # Empty function performing the encryption of the file and sending it to the server
        upload = True

        form = FileForm()

    return render(request, 'frontend/upload.html', locals())



@login_required
def search_files(request):
    ''' Search keywords among encrypted files '''
    form = SearchForm(request.POST or None)
    search = False

    if form.is_valid():
        keywords = form.cleaned_data['keywords'].split(', ')
        print(keywords)
        files = search_keywords(keywords, request.user.profile.secret_key)  # Empty function performing the search and returning the files
        search = True
    
    return render(request, 'frontend/search.html', locals())


# QUESTIONS
# How is the KeyGen performed ? How are the keys distributed ?
# How is the server setup ? How do we communicate with it ?
# When are the keywords generated ? Before or after we upload a form ?
# What to do with the local decrypted files



def create_account(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        # Create the User object
        new_user = form.save()

        # Contact the server to get the global param and compute the pair of keys
        public_key, secret_key = keygen()
        
        # Save the keys to the database
        new_profile = Profile()
        new_profile.user = new_user
        new_profile.secret_key = secret_key
        new_profile.public_key = public_key
        new_profile.save()

        # Redirect to the login page
        return redirect('frontend:home')

    return render(request, 'frontend/sign.html', locals())