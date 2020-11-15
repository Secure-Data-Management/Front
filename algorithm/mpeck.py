#!/usr/bin/python3
import base64
import json
from typing import List, Tuple, Dict

from Crypto.Cipher import AES
from algorithm.genkey import *
import hashlib


def encrypt(message: Union[bytearray, bytes, str], key: Union[bytearray, bytes]) -> Tuple[bytes, bytes, bytes]:
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return ciphertext, tag, cipher.nonce


def decrypt(message: Union[bytearray, bytes, str], key: Union[bytearray, bytes], tag: Union[bytearray, bytes], nonce: Union[bytearray, bytes]) -> Tuple[bytes, bool]:
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext: bytes = cipher.decrypt(message)
    try:
        cipher.verify(tag)
        res = True
    except ValueError:
        res = False
    return plaintext, res


def mpeck(pk_list: List[str], keyword_list: List[str], genkey: KeyGen, message: bytes = b"") -> Tuple[Dict[str, str], Element, List[Element], List[Element]]:
    """
    multi Public key Encryption with Conjuctive Keyword. Encrypts both message and keywords !
    Performs the encryption of the keywords and of the message, using the mPECK model. Encrypts the keywords in W using the public keys in pk_list
    Parameters:
        pk_list: list of keys (from Keygen.keys)
        keyword_list: set of keywords
        genkey: the genkey instance
        message: a message to encrypt (if any)
    Returns:
        [E, A, B, C] as in the paper, E={} if there was no message [A, B, C] with A=g^r, B=[B1, ..., Bn] and C=[C1, ..., Cl]
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
        yj: Element = Element(genkey.pairing, G1, value=pk_list[j])
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
    E: Dict[str, str] = dict()
    if len(message) > 0:
        e_g_g: Element = genkey.e(genkey.g, genkey.g)
        e_r_s: Element = r * s
        e_g_g1: Element = e_g_g ** e_r_s
        e_g_g2: bytes = hashlib.sha256(e_g_g1.__str__().encode()).digest()
        ciphertext, tag, nonce = encrypt(message, e_g_g2)
        E: Dict[str, str] = {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "tag": base64.b64encode(tag).decode(),
            "nonce": base64.b64encode(nonce).decode(),
        }
    return E, A, B, C


def mdec(xj: str, E: Dict[str,str], Bj: str, A: str, k: KeyGen):
    """Decrypts the cipher E, using private key xj, Bj and A"""
    secret_key = int(xj, base=16)
    secret_key = Element(k.pairing, Zr, value=secret_key)  # Convert to Element
    A = Element(k.pairing, G1, value=A)  # Convert to Element
    Bj = Element(k.pairing, G1, value=Bj)  # Convert to Element

    e_A_Bj: Element = k.e(A, Bj)
    res: Element = e_A_Bj ** (~secret_key)
    Xj = hashlib.sha256(res.__str__().encode()).digest()
    plaintext, verify = decrypt(base64.b64decode(j["ciphertext"]), Xj, base64.b64decode(j["tag"]), base64.b64decode(j["nonce"]))
    return plaintext.decode() if verify else None
