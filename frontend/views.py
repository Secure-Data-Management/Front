from pathlib import Path
from typing import Optional, Tuple

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from algorithm.genkey import KeyGen
from frontend.file_generator import generate_files
from frontend.forms import FileForm, ConsultantFileForm, SearchForm, UserForm, ServerForm, LoginForm
from frontend.functions import encryption, search_keywords, keygen, get_consultant, get_user_list, contact_server, change_address, get_address, load_key, get_username_and_id, get_current_genkey, \
    reset_keygen
from frontend.models import UserKeys

CURRENT_USER: Optional[UserKeys] = None
CONSULTANT: Optional[UserKeys] = None


# Create your views here.
def home(request):
    global CURRENT_USER
    """ Homepage of the application """
    if CURRENT_USER is not None:
        return render(request, 'frontend/home.html', {"current_user": CURRENT_USER})
    else:
        return redirect('frontend:login')


def login(request):
    global CURRENT_USER
    form = LoginForm(request.POST or None)
    if form.is_valid():
        res = load_key(form.cleaned_data["private_key"])
        if res:
            username, id = get_username_and_id()
            if id >= 0:
                k: KeyGen = get_current_genkey()
                CURRENT_USER = UserKeys(id, username, str(k.pub_key), str(k.priv_key))
                return redirect('frontend:home')
            else:
                return render(request, 'frontend/login.html', {'form': form, "address": get_address(), "current_user": CURRENT_USER, "errors": [username]})
        else:
            return render(request, 'frontend/login.html', {'form': form, "address": get_address(), "current_user": CURRENT_USER, "errors": ["Key was incorrect"]})
    return render(request, 'frontend/login.html', {'form': form, "address": get_address(), "current_user": CURRENT_USER})


def logout(request):
    global CURRENT_USER, CONSULTANT
    CURRENT_USER = None
    CONSULTANT = None
    reset_keygen()
    return render(request, 'frontend/logged_out.html')


def guarantee_everything() -> Tuple[bool, str]:
    ''' Get the keys from a user.txt file '''
    global CURRENT_USER, CONSULTANT

    if CURRENT_USER is None:
        return False, "You are not logged in"
    if CONSULTANT is None:
        consultant_key, consultant_id = get_consultant()
        if consultant_id is None:
            return False, "No consultant exists on the server"
        CONSULTANT = UserKeys(consultant_id, "consultant", consultant_key, "")
    if get_current_genkey() is None:
        CURRENT_USER = None
        CONSULTANT = None
        reset_keygen()
        return False, "You are not even logged in"
    return True, ""


# TODO validate tokens
def upload_file(request):
    global CURRENT_USER, CONSULTANT
    status, reason = guarantee_everything()
    if not status:
        return render(request, 'frontend/error.html', {"error": reason})
    file_content = ""
    file_keywords_content = ""
    generate = False
    ''' Generate random file and the Keywords file associated '''
    if request.GET.get('generate_button'):
        generate_files()
        filename = Path('./frontend/data_user/File.csv')
        filename.touch(exist_ok=True)
        f = open(filename, 'r')
        file_content = f.read()
        f.close()
        filename = Path('./frontend/data_user/File_keywords.csv')
        filename.touch(exist_ok=True)
        f = open(filename, 'r')
        file_keywords_content = f.read()
        f.close()
        context = {'file_content': file_content, 'file_keywords_content': file_keywords_content}
        generate = True

    ''' Upload a file onto the server '''
    if CURRENT_USER.public_key == CONSULTANT.public_key:
        # It is the consultant
        users_json = get_user_list()
        list_choices = []
        # In the list, add every user except the consultant itself
        for user_object in users_json:
            if user_object['id'] != CURRENT_USER.id:
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
    upload = ""

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

        if CURRENT_USER.public_key == CONSULTANT.public_key:
            public_keys = [CURRENT_USER.public_key]
            public_ids = [CURRENT_USER.id]

            encrypt_to = form.cleaned_data['encrypt_to']  # id of the user which can read the file
            for user_object in users_json:
                if user_object['id'] == int(encrypt_to):
                    public_keys.append(user_object['key'])
                    public_ids.append(user_object['id'])
        else:
            # The list of public keys of the users we want to encrypt the file for (i.e. author + consultant)
            public_keys = [CURRENT_USER.public_key, CONSULTANT.public_key]
            public_ids = [CURRENT_USER.id, CONSULTANT.id]
        res=encryption(file_encrypt, keywords, public_keys, public_ids)  # Empty function performing the encryption of the file and sending it to the server
        upload = res
        form = FileForm()

    return render(request, 'frontend/upload.html', {
        'form': form,
        "address": get_address(),
        "current_user": CURRENT_USER,
        "upload": upload,
        "file_keywords_content": file_keywords_content,
        "file_content": file_content,
    })


# TODO validate tokens
def search_files(request):
    ''' Search keywords among encrypted files '''
    global CURRENT_USER, CONSULTANT
    status, reason = guarantee_everything()
    if not status:
        return render(request, 'frontend/error.html', {"error": reason})

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
        files = search_keywords(keywords, CURRENT_USER.secret_key, CURRENT_USER.id)
        search = True

    return render(request, 'frontend/search.html', locals(), {"current_user": CURRENT_USER})


def create_account(request):
    global CURRENT_USER, CONSULTANT

    form = UserForm(request.POST or None)
    if form.is_valid():
        # Contact the server to get the global param and compute the pair of keys
        public_key, secret_key, user_id = keygen(form.cleaned_data['username'])
        if user_id < 0:
            e = {
                -1: f"The username {form.cleaned_data['username']} already exists",
                -2: f"The server was unreachable at {get_address()}",
                -3: public_key,
            }
            return render(request, 'frontend/sign.html', {'form': form, "address": get_address(), 'errors': [e[user_id] if user_id in e else f"Unknown error {user_id}"], "current_user": CURRENT_USER})
        # Save the user information in a JSON file
        CURRENT_USER = UserKeys(user_id, form.cleaned_data['username'], public_key, secret_key)
        CURRENT_USER.save_to_file()

        # Create consultant
        consultant_key, consultant_id = get_consultant()
        if consultant_id is None:
            return render(request, 'frontend/sign.html', {'form': form, "address": get_address(), 'errors': ["No consultant was registered before"], "current_user": CURRENT_USER})
        CONSULTANT = UserKeys(consultant_id, "consultant", consultant_key, "")

        # Redirect to the login page
        return redirect('frontend:home')

    return render(request, 'frontend/sign.html', {'form': form, "address": get_address(), "current_user": CURRENT_USER})


def change_server(request):
    form = ServerForm(request.POST or None, initial={'server_ip': get_address()})
    if form.is_valid():
        res = contact_server(form.cleaned_data['server_ip'])
        if res:
            change_address(form.cleaned_data['server_ip'])
            return redirect('frontend:home')
        else:
            return render(request, 'frontend/server.html', {'form': form, "address": get_address(), 'errors': ["Ip is unreachable"], "current_user": CURRENT_USER})
    return render(request, 'frontend/server.html', {'form': form, "address": get_address(), "current_user": CURRENT_USER})
