#!/usr/bin/python3

import hashlib
from typing import Union, Callable, Any

from pypbc import *


class KeyGen:
    def __init__(self, params_string: str, g):
        self.params: Parameters = Parameters(params_string)  # the parameter are given by the server
        self.pairing: Pairing = Pairing(self.params)
        # those two hash function are hardcoded and are the same for all clients
        self.h1: Callable[[Union[bytes, bytearray, str]], Element] = self.get_hash_function(self.pairing, hashlib.sha3_256)
        self.h2: Callable[[Union[bytes, bytearray, str]], Element] = self.get_hash_function(self.pairing, hashlib.sha3_512)
        self.e: Callable[[Element, Element], Element] = lambda e1, e2: self.pairing.apply(e1, e2)
        self.g = Element(self.pairing, G2, value=g)  # The generator g is given by the global parameters sent by the server
        self.priv_key: Element = Element.random(self.pairing, Zr)
        self.pub_key: Element = Element(self.pairing, G1, value=self.g ** self.priv_key)

    def get_hash_function(self, pairing, hash_function: Callable[[Union[bytes, bytearray]], Any]) -> Callable[[Union[bytes, bytearray, str]], Element]:
        return lambda text: Element.from_hash(pairing, G1, hash_function(text).digest()) if isinstance(text, (bytes, bytearray)) else \
            Element.from_hash(pairing, G1, hash_function(text.encode()).digest())

    def __str__(self):
        return f"(pk,sk) key: ({self.pub_key},{self.priv_key}), generator g: {self.g}, params: {self.params}"
