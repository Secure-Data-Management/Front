import requests
from algorithm.genkey import KeyGen
from algorithm.mpeck import mpeck, mdec
from algorithm.trapdoor import generate_trapdoor
from django.conf import settings

import json
import base64

ADDRESS = 'http://192.168.1.67:8000/'
KEYGEN: KeyGen = None


def get_genkey():
    # Contact the server
    global_params = requests.get(ADDRESS + 'keys/get_params')
    global_g = requests.get(ADDRESS + 'keys/get_generator')

    # Construct the GenKey
    key_gen = KeyGen(global_params.text, global_g.text)

    return key_gen


def get_consultant():
    # Contact the server
    consultant_information = requests.get(ADDRESS + 'keys/get_key?user=consultant')
    # Returns id, str(public_key)
    consultant_object = consultant_information.text.split(',')

    # Return the public information for the consultant : id, public key
    public_key = consultant_object[1]
    consultant_id = int(consultant_object[0])
    return public_key, consultant_id


def get_user_list():
    response = requests.get(ADDRESS + 'keys/get_users')
    json_object = json.loads(response.text)
    return json_object


def encryption(file_encrypt: str, keywords, public_keys, id_list, private_key):
    """Encrypt the given file and send it to the server """
    # mpeck(pk_list: list of public keys, keyword_list, genkey, message: file)
    global KEYGEN

    if KEYGEN is None:
        print("ERROR", "KEYGEN is not defined in encryption")
        return
    key_gen = KEYGEN

    # MPECK
    (ciphertext, A, B, C) = mpeck(public_keys, keywords, key_gen, file_encrypt)
    A = str(A)  # transforms elements into string
    B = [str(i) for i in B]
    C = [str(i) for i in C]

    cipher = base64.b64encode(ciphertext).decode('ASCII')

    # Send everything to the server
    dictionnary = {
        "E": cipher,
        "A": A,
        "B": B,
        "C": C,
        "id_list": id_list,  # Autant d'éléments que dans B
    }

    # result = mdec(private_key, base64.b64decode(cipher), B[0], A, KEYGEN)
    # print('RESULT ', result, '\n\n\n')

    r = requests.post(ADDRESS + 'file/upload', data=json.dumps(dictionnary))
    # TODO upload successful or no answer


def search_keywords(keywords, private_key, user_id):
    """ Given a keyword, send it to the server (that performs the encrypted search) adn return the result ;
    Decrypt the files and store them into the "files" directory """
    # generate_trapdoor(priv_key: Element, index_list: List[int], keyword_list: List[str], genkey: KeyGen)
    global KEYGEN

    if KEYGEN is None:
        raise Exception("KEYGEN is not defined in search_keywords")

    key_gen = KEYGEN
    liste_keywords = []
    liste_index = []
    for index, keyword in enumerate(keywords):
        if keyword != "":
            liste_keywords.append(keyword)
            liste_index.append(index)

    # Generate the trapdoor
    trapdoor = generate_trapdoor(private_key, liste_index, liste_keywords, key_gen)

    for i in range(3):
        trapdoor[i] = str(trapdoor[i])
    
    data_json = {
        "trapdoor": trapdoor,
        "id": user_id
    }
    print(user_id)
    print(data_json)

    # Send to the server
    r = requests.post(ADDRESS + 'search', data=json.dumps(data_json))

    # Decode the received files
    file_list = []

    r_list = json.loads(r.text)
    for index, data in enumerate(r_list):
        cipher = base64.b64decode(data['E'])
        A = data['A']
        Bj = data['B']
        print(data)

        # mdec(private_key: str, ciphertext: bytearray, Bj: str, A: str, k: KeyGen):
        result = mdec(private_key, cipher, Bj, A, KEYGEN)

        file_path = settings.MEDIA_ROOT + 'file_' + str(index) + '.txt'
        with open(file_path, 'w') as file:
            file.write(result)

            file_list.append('file_' + str(index) + '.txt')

    return file_list


def keygen(username: str):
    """ Contact the server, gets the global parameters and compute the key pair for a user """
    global KEYGEN
    KEYGEN = get_genkey()

    public_key = str(KEYGEN.pub_key[0])
    secret_key = str(KEYGEN.priv_key[0])

    # Send the public key to the server
    key_request = requests.get(ADDRESS + 'keys/add_key' + '?key=' + str(public_key) + '&user=' + username)
    user_id = int(key_request.text)
    
    # TODO case "user_already_exist"
    return public_key, secret_key, user_id

