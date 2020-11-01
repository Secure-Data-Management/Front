#!/usr/bin/python3
# - KeyGen(1k): Given the a security parameter 1k, it returns params = (G1, G2,
# eˆ, H1(·), H2(·), g) where H1:{0, 1}log w → G1 and H2:{0, 1}log w → G1 are
# two different collision-resistance hash functions and g is a generator of G1.
# It chooses n random values x1,...,xn in Z∗
# p and computes yi = gxi . The
# public/private key pairs (pk1, sk1),...,(pkn, skn) are given by
# (pki, ski)=(yi, xi).
# Erwan

from typing import Union, Tuple, List, Callable, Any

import hashlib

from pooc.bn256 import *

from pypbc import *


class KeyGen:
    def __init__(self, params_string: str, g, n=1):
        self.params: Parameters = Parameters(params_string)  #  
        self.pairing: Pairing = Pairing(self.params)
        self.h1: Callable[[Union[bytes, bytearray, str]], Element] = self.get_hash_function(self.pairing, hashlib.sha3_256)
        self.h2: Callable[[Union[bytes, bytearray, str]], Element] = self.get_hash_function(self.pairing, hashlib.sha3_512)
        self.e: Callable[[Element, Element], Element] = lambda e1, e2: self.pairing.apply(e1, e2)
        self.pub_keys: List[Element] = []
        self.keys: List[Tuple[Element, Element]] = []
        self.priv_keys: List[Element] = []
        self.g = Element(self.pairing, G2, value=g)  # The generator g is given by the global parameters sent by the server
        for _ in range(n):
            sk: Element = Element.random(self.pairing, Zr)
            pk: Element = Element(self.pairing, G1, value=self.g ** sk)
            self.keys.append((sk, pk))
            self.pub_keys.append(pk)
            self.priv_keys.append(sk)

    def get_hash_function(self, pairing, hash_function: Callable[[Union[bytes, bytearray]], Any]) -> Callable[[Union[bytes, bytearray, str]], Element]:
        return lambda text: Element.from_hash(pairing, G1, hash_function(text).digest()) if isinstance(text, (bytes, bytearray)) else \
            Element.from_hash(pairing, G1, hash_function(text.encode()).digest())

    @staticmethod
    def test():
        # this is a test for the BLS short signature system
        params = Parameters(qbits=512, rbits=160)
        pairing = Pairing(params)

        # build the common parameter g
        g = Element.random(pairing, G2)

        # build the public and private keys
        private_key = Element.random(pairing, Zr)
        public_key = Element(pairing, G2, value=g ** private_key)

        # set the magic hash value
        hash_value = Element.from_hash(pairing, G1, "hashofmessage")

        # create the signature
        signature = hash_value ** private_key

        # fill temp2
        temp2 = pairing.apply(hash_value, public_key)

        # and again...
        temp1 = pairing.apply(signature, g)

        # compare
        assert (temp1 == temp2)
        print("test passed")

    def __str__(self):
        return f"\n".join([f"keys (s{i},p{i})=({self.keys[i][0]},{self.keys[i][1]})" for i, key in enumerate(self.keys)])


if __name__ == '__main__':
    KeyGen.test()
    print(KeyGen(3))