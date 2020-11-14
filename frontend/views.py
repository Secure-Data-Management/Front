from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from frontend.file_generator import generate_files
from frontend.forms import FileForm, ConsultantFileForm, SearchForm, UserForm
from frontend.functions import encryption, search_keywords, keygen, get_consultant, get_user_list
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
        # json_object = UserKeys.get_from_file()
        # USERKEYS = UserKeys(json_object['id'], json_object['username'], json_object['public_key'], json_object['private_key'])
        #
        # # Create consultant
        # consultant_key, consultant_id = get_consultant()
        # CONSULTANT = UserKeys(consultant_id, "consultant", consultant_key, "noonecares")
        # print(USERKEYS, CONSULTANT)


@login_required
def upload_file(request):
    global USERKEYS, CONSULTANT
    keys_from_file()
    
    generate = False
    ''' Generate random file and the Keywords file associated '''
    if(request.GET.get('generate_button')):
        generate_files()
        f = open('./frontend/data_user/File.csv', 'r')
        file_content = f.read()
        f.close()
        f = open('./frontend/data_user/File_keywords.csv', 'r')
        file_keywords_content = f.read()
        f.close()
        context = {'file_content': file_content, 'file_keywords_content': file_keywords_content}
        generate = True


    ''' Upload a file onto the server '''
    print(USERKEYS.public_key, CONSULTANT.public_key)
    if USERKEYS.public_key == CONSULTANT.public_key:
        # It is the consultant
        users_json = get_user_list()
        list_choices = []
        # In the list, add every user except the consultant itself
        for user_object in users_json:
            if user_object['id'] != USERKEYS.id:
                list_choices.append({"id": user_object['id'], "name": user_object['name']})

        if not generate:
            form = ConsultantFileForm(list_choices, request.POST or None, request.FILES)
        else:
            if request.method == "POST":
                form = ConsultantFileForm(list_choices, request.POST, request.FILES)
            else:
                form_dict = {
                    'keywords_to': context['file_keywords_content'].split(',')[1], 
                    'keywords_type': context['file_keywords_content'].split(',')[0],
                    'keywords_amount': context['file_keywords_content'].split(',')[2],
                    'keywords_date': context['file_keywords_content'].split(',')[3],
                    'keywords_bank': context['file_keywords_content'].split(',')[4],
                    }
                print(form_dict)
                form = ConsultantFileForm(list_choices, initial=form_dict)
    else:
        if not generate:
            form = FileForm(request.POST or None, request.FILES)
        else:
            if request.method == "POST":
                form = FileForm(request.POST, request.FILES)
            else:
                form_dict = {
                    'keywords_to': context['file_keywords_content'].split(',')[1], 
                    'keywords_type': context['file_keywords_content'].split(',')[0],
                    'keywords_amount': context['file_keywords_content'].split(',')[2],
                    'keywords_date': context['file_keywords_content'].split(',')[3],
                    'keywords_bank': context['file_keywords_content'].split(',')[4],
                    }
                print(form_dict)
                form = FileForm(initial=form_dict)
    upload = False

    if(request.GET.get('generate_button')):
        generate_files()

    if form.is_valid():
        # file_encrypt must be a string
        file_e = form.cleaned_data['file']
        file_encrypt = file_e.read()
        
        keywords_type = form.cleaned_data['keywords_type']
        keywords_to = form.cleaned_data['keywords_to']
        keywords_amount = str(form.cleaned_data['keywords_amount'])
        keywords_date = form.cleaned_data['keywords_date'].strftime("%d %m %Y")
        keywords_bank = form.cleaned_data['keywords_bank']
        keywords = [keywords_type, keywords_to, keywords_amount, keywords_date, keywords_bank]

        if USERKEYS.public_key == CONSULTANT.public_key:
            public_keys = [USERKEYS.public_key]
            public_ids = [USERKEYS.id]

            encrypt_to = form.cleaned_data['encrypt_to']  # id of the user which can read the file
            for user_object in users_json:
                if user_object['id'] == int(encrypt_to):
                    public_keys.append(user_object['key'])
                    public_ids.append(user_object['id'])

        else:
            # The list of public keys of the users we want to encrypt the file for (i.e. author + consultant)
            public_keys = [USERKEYS.public_key, CONSULTANT.public_key]
            public_ids = [USERKEYS.id, CONSULTANT.id]

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
        keywords_type = form.cleaned_data['keywords_type']
        keywords_to = form.cleaned_data['keywords_to']

        if form.cleaned_data['keywords_amount'] is None:
            keywords_amount = ""
        else:
            keywords_amount = str(form.cleaned_data['keywords_amount'])
        keywords_bank = form.cleaned_data['keywords_bank']
        

        if form.cleaned_data['keywords_date'] is None or form.cleaned_data['keywords_date'] == 'None':
            keywords_date = ""
        else:
            keywords_date = form.cleaned_data['keywords_date'].strftime("%d %m %Y")

        keywords = [keywords_type, keywords_to, keywords_amount, keywords_date, keywords_bank]

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
