#!/usr/bin/python3
from typing import List

from algorithm.genkey import *
from pypbc import Element, Zr


def generate_trapdoor(priv_key: str, keyword_list: List[str], genkey: KeyGen) -> List[Element]:
    """
    :param priv_key: the private key of the user
    :param keyword_list: list of keywords for the cunjunctive search
    :param genkey: the keygen instance
    :return: [Tjq1, Tjq2, Tjq3] + index_list the three trapdoor element and the index list
    """
    # convert the hexadecimal key to integer
    priv_key = int(priv_key, 16)
    # select a random value t in Zp*
    priv_key = Element(genkey.pairing, Zr, value=priv_key)
    t: Element = Element.random(genkey.pairing, Zr)

    # Tjq1 = g ** t ; g the generator of G1 as defined in KeyGen
    Tjq1 = genkey.g ** t

    # Tjq2 = (hI1... hIm)**t where hIj = h1(wIj)
    Tjq2: Element = Element.one(genkey.pairing, G1)
    for keyword in keyword_list:
        Tjq2 = Tjq2 * genkey.h1(keyword)
    Tjq2 **= t

    # Tjq3 = (fI1... fIm)**(t / xj) where fIj = h2(wIj) ; xj computed in KeyGen
    Tjq3: Element = Element.one(genkey.pairing, G1)
    for keyword in keyword_list:
        Tjq3 = Tjq3 * genkey.h2(keyword)
    Tjq3 **= t.__ifloordiv__(priv_key)

    return [Tjq1, Tjq2, Tjq3]

