from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from frontend.forms import FileForm, SearchForm
from frontend.functions import encryption, search_keywords


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
        file = form.cleaned_data['file']
        keywords = form.cleaned_data['keywords']
        encryption(file, keywords)  # Empty function performing the encryption of the file and sending it to the server
        upload = True

        form = FileForm()

    return render(request, 'frontend/upload.html', locals())




@login_required
def search_files(request):
    '''Search keywords among encrypted files'''
    form = SearchForm(request.POST or None)
    search = False

    if form.is_valid():
        keywords = form.cleaned_data['keywords']
        files = search_keywords(keywords)  # Empty function performing the search and returning the files
        search = True
    
    return render(request, 'frontend/search.html', locals())


# QUESTIONS
# How is the KeyGen performed ? How are the keys distributed ?
# How is the server setup ? How do we communicate with it ?
# When are the keywords generated ? Before or after we upload a form ?
