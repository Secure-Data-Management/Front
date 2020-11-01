#!/usr/bin/python3
from typing import Callable, List, Tuple

from pooc.genkey import *
# Antoine
import hashlib


def xor(message: Union[bytearray, bytes, str], key: Union[bytearray, bytes]) -> bytearray:
    """Takes a string message and a bytes sequence and hash it with a displacing key sequence"""
    res: bytearray = bytearray()
    if type(message) == str:
        message = bytearray(message.encode())
    elif type(message) == bytes:
        message = bytearray(message)
    if type(key) == bytes:
        key = bytearray(key)
    if len(message) > len(key):
        for i in range(len(message)):
            res.append(message[i] ^ key[i % len(key)])
    else:
        for i in range(len(message)):
            res.append(key[i] ^ message[i % len(message)])
    return res


def mpeck(pk_list: List[Element], keyword_list: List[str], genkey: KeyGen, message: str = "") -> Tuple[bytearray, Element, List[Element], List[Element]]:
    """
    multi Public key Encryption with Conjuctive Keyword. Encrypts both message and keywords !
    Performs the encryption of the keywords and of the message, using the mPECK model. Encrypts the keywords in W using the public keys in pk_list
    Parameters:
        pk: list of keys (from Keygen.keys)
        keyword_list: set of keywords
        params: a dictionary containing the security parameters
    Returns:
        [E, A, B, C] as in the paper, E=b"" if there was no message
            [A, B, C] with A=g^r, B=[B1, ..., Bn] and C=[C1, ..., Cl]
            :param keyword_list:
            :param pk_list:
            :param message:
            :param genkey:
    """
    # selects two random values in Zp*
    s: Element = Element.random(genkey.pairing, Zr)
    r: Element = Element.random(genkey.pairing, Zr)
    # computes the A=g^r
    A: Element = genkey.g ** r
    # computes B = pk**s for each public key
    n = len(pk_list)
    B: List[Element] = []
    for j in range(n):
        yj: Element = genkey.pub_keys[j]
        B.append(yj ** s)
    # computes C = (h^r)(f^s) for each keyword
    C: List[Element] = []
    for i, kw in enumerate(keyword_list):
        h = genkey.h1(kw)
        f = genkey.h2(kw)
        temp1: Element = h ** r
        temp2: Element = f ** s
        C.append(temp1 * temp2)
    # encode the message
    E: bytearray = bytearray()
    if len(message) > 0:
        e_g_g: Element = genkey.pairing.apply(genkey.g, genkey.g)
        e_r_s: Element = r * s
        e_g_g1: Element = e_g_g ** e_r_s
        e_g_g2: bytes = hashlib.sha256(e_g_g1.__str__().encode()).digest()
        E: bytearray = xor(message, e_g_g2)
    return E, A, B, C


def mdec(xj: Element, E: bytearray, Bj: Element, A: Element, k: KeyGen):
    """Decrypts the cipher E, using private key xj, Bj and A"""
    e_A_Bj: Element = k.e(A, Bj)
    res: Element = e_A_Bj ** (~xj)
    Xj = hashlib.sha256(res.__str__().encode()).digest()
    m = xor(E, Xj)
    m = m.decode()
    return m


if __name__ == "__main__":
    # number of participants
    _n = 3
    k = KeyGen(_n)
    # encryption of the message
    _message = "This is the message"
    _keywords = ["test", "encryption"]
    # there are 3 clients, only allow 0 and 1 to search and decrypt
    _recipients = [0, 1]
    _recipients_pk = [k.pub_keys[r] for r in _recipients]
    _E, _A, _B, _C = mpeck(_recipients_pk, _keywords, k, message=_message)
    print(f"Message \"{_message}\" encrypted, only recipients {_recipients} are allowed to decrypt")
    # decrypt as 0
    for _i in range(len(_recipients)):
        m = mdec(k.priv_keys[_i], _E, _B[_i], _A, k)
        print(f"Client {_i}: decryption is: {m}")
