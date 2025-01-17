from typing import List, Dict, Union, Tuple, Optional

import requests
from algorithm.genkey import KeyGen
from algorithm.mpeck import mpeck, mdec
from algorithm.trapdoor import generate_trapdoor
from django.conf import settings

import json
import base64

KEYGEN: KeyGen = None

ADDRESS: str = 'http://127.0.0.1:14000/'


def get_current_genkey() -> KeyGen:
    global KEYGEN
    return KEYGEN


def get_address() -> str:
    global ADDRESS
    return ADDRESS


def get_genkey():
    if not contact_server(ADDRESS):
        return None

    global_params = requests.get(ADDRESS + 'keys/get_params')
    global_g = requests.get(ADDRESS + 'keys/get_generator')

    # Construct the GenKey
    key_gen = KeyGen(global_params.text, global_g.text)

    return key_gen


def contact_server(address: str) -> bool:
    try:
        r = requests.get(address)
        return r.text == "mPECK server"
    except Exception:
        return False


def change_address(address: str):
    global ADDRESS
    ADDRESS = address.rstrip("/") + "/"


def get_consultant() -> Tuple[str, Optional[int]]:
    # Contact the server
    consultant_information = requests.get(ADDRESS + 'keys/get_key?user=consultant')
    # Returns id, str(public_key)
    consultant_object = consultant_information.text.split(',')
    if len(consultant_object) != 2:
        return "".join(map(str, consultant_object)), None
    consultant_id: int = int(consultant_object[0])
    public_key: str = consultant_object[1]
    return public_key, consultant_id


def get_user_list():
    response = requests.get(ADDRESS + 'keys/get_users')
    json_object = json.loads(response.text)
    return json_object


def encryption(file_encrypt: bytes, keywords: List[str], public_keys: List[str], id_list: List[int])->str:
    """Encrypt the given file and send it to the server """
    global KEYGEN

    if KEYGEN is None:
        print("ERROR", "KEYGEN is not defined in encryption")
        return ""
    key_gen = KEYGEN

    # MPECK
    (cipherdict, A, B, C) = mpeck(public_keys, keywords, key_gen, file_encrypt)
    A = str(A)  # transforms elements into string
    B = [str(i) for i in B]
    C = [str(i) for i in C]

    # Send everything to the server
    dictionnary = {
        "E": cipherdict,
        "A": A,
        "B": B,
        "C": C,
        "id_list": id_list,  # Autant d'éléments que dans B
    }

    r = requests.post(ADDRESS + 'file/upload', data=json.dumps(dictionnary))
    return r.text


def search_keywords(keywords, private_key, user_id):
    """ Given a keyword, send it to the server (that performs the encrypted search) adn return the result ;
    Decrypt the files and store them into the "files" directory """
    # generate_trapdoor(priv_key: Element, index_list: List[int], keyword_list: List[str], genkey: KeyGen)
    global KEYGEN

    if KEYGEN is None:
        raise Exception("KEYGEN is not defined in search_keywords")

    key_gen = KEYGEN
    keywords_list = []
    index_list = []
    for index, keyword in enumerate(keywords):
        if keyword != "":
            keywords_list.append(keyword)
            index_list.append(index)

    # Generate the trapdoor
    trapdoor = generate_trapdoor(private_key, keywords_list, key_gen)

    trapdoor = list(map(str, trapdoor))

    data_json = {
        "trapdoor": trapdoor,
        "index_list": index_list,
        "id": user_id
    }
    # Send to the server
    r = requests.post(ADDRESS + 'search', data=json.dumps(data_json))

    # Decode the received files
    file_list = []

    r_list = json.loads(r.text)
    for index, data in enumerate(r_list):
        cipher_dict: Dict[str, str] = data['E']
        A = data['A']
        Bj = data['B']
        result = mdec(private_key, cipher_dict, Bj, A, KEYGEN)
        if result is not None:
            file_path = settings.MEDIA_ROOT + 'file_' + str(index) + '.txt'
            with open(file_path, 'wb') as file:
                file.write(result)
                file_list.append('file_' + str(index) + '.txt')
        else:
            print("WARNING",index,"error")
    return file_list


def load_key(priv_key: str) -> bool:
    global KEYGEN
    KEYGEN = get_genkey()
    if KEYGEN is None:
        return False
    try:
        KEYGEN.gen_public_key(int(priv_key, 16))
        return True
    except Exception:
        return False


def reset_keygen():
    global KEYGEN
    KEYGEN = None


def get_username_and_id() -> Tuple[str, int]:
    try:
        r = requests.get(ADDRESS + 'keys/get_username?key=' + str(KEYGEN.pub_key))
        s = r.text.split(";")
        if len(s) != 2:
            return r.text, -1
        try:
            id = int(s[0])
            if id < 0:
                return s[1], -1
            else:
                return s[1], id
        except ValueError:
            return s[1], -1

    except Exception as e:
        return "Server error : " + str(e), -1


def keygen(username: str):
    """ Contact the server, gets the global parameters and compute the key pair for a user """
    global KEYGEN
    KEYGEN = get_genkey()
    if KEYGEN is None:
        return "", "", -2

    KEYGEN.gen_keys()
    public_key = str(KEYGEN.pub_key)
    secret_key = str(KEYGEN.priv_key)

    # Send the public key to the server
    try:
        key_request = requests.get(ADDRESS + 'keys/add_key' + '?key=' + str(public_key) + '&user=' + username)
        try:
            user_id = int(key_request.text)
            return public_key, secret_key, user_id
        except ValueError:
            return key_request.text, "", -3
    except Exception as e:
        return e, "", -3
