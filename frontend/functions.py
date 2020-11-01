import requests
from pooc.genkey import KeyGen
from pooc.mpeck import mpeck
from pooc.trapdoor import generate_trapdoor

import json
import base64
ADDRESS = 'http://192.168.1.67:8000/'


def get_genkey():
    # Contact the server
    global_params = requests.get(ADDRESS + 'keys/get_params')
    global_g = requests.get(ADDRESS + 'keys/get_generator')

    # Construct the GenKey
    key_gen = KeyGen(global_params.text, global_g.text)

    return key_gen


def encryption(file_encrypt:str, keywords, public_keys):
    '''Encrypt the given file and send it to the server '''
    # mpeck(pk_list: list of public keys, keyword_list, genkey, message: file)
    key_gen = get_g'Readme.md']enkey()

    # MPECK
    (ciphertext, A, B, C) = mpeck(public_keys, keywords, key_gen, file_encrypt)
    A = str(A)  # transforms elements into string
    B = [str(i) for i in B]
    C = [str(i) for i in C]

    cipher = base64.b64encode(ciphertext).decode('ASCII')

    # Send everything to the server
    dictionnary = {
        "ciphertext": cipher,
        "A": A,
        "B": B,
        "C": C,
    }

    r = requests.post(ADDRESS + 'file/upload', data=json.dumps(dictionnary))


def search_keywords(keywords, private_key):
    ''' Given a keyword, send it to the server (that performs the encrypted search) adn return the result ;
    Decrypt the files and store them into the "files" directory'''
    # generate_trapdoor(priv_key: Element, index_list: List[int], keyword_list: List[str], genkey: KeyGen)
    key_gen = get_genkey()
    index_list = [i for i in range(len(keywords))]
    print(index_list)

    # Generate the trapdoor
    trapdoor = generate_trapdoor(private_key, index_list, keywords, key_gen)

    for i in range(3):
        trapdoor[i] = str(trapdoor[i])

    # Send to the server
    r = requests.post(ADDRESS + 'search', data=str(trapdoor).replace("'", "\""))

    return ['Readme.md']


def keygen():
    ''' Contact the server, gets the global parameters and compute the key pair for a user '''
    key_gen = get_genkey()

    public_key = str(key_gen.pub_keys[0])
    secret_key = str(key_gen.priv_keys[0])

    # Send the public key to the server
    key_request = requests.get(ADDRESS + 'keys/add_key' + '?key=' + str(public_key))
    
    return public_key, secret_key