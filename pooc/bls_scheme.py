#!/usr/bin/python


"""
Demonstrate the bn256 module using the BLS short signature scheme
"""
from . import bn256


def bls_keygen():
    k, g = bn256.g2_random()
    return (k, g)


def bls_sign(privkey, msg):
    pt = bn256.g1_hash_to_point(msg)
    assert pt.is_on_curve()
    sig=pt.scalar_mul(privkey)
    print(sig,type(sig))
    print(bn256.g1_compress(sig),type(bn256.g1_compress(sig)))
    return bn256.g1_compress(sig)


def bls_verify(pubkey, msg, csig):
    sig = bn256.g1_uncompress(csig)

    assert type(pubkey) == bn256.CurveTwist
    assert type(sig) == bn256.CurvePoint

    msg_pt = bn256.g1_hash_to_point(msg)

    assert msg_pt.is_on_curve()

    v1 = bn256.optimal_ate(pubkey, msg_pt)
    v2 = bn256.optimal_ate(bn256.twist_G, sig)

    return v1 == v2


def test():
    (priv, pub) = bls_keygen()
    import time
    for i in range(1000):
        msg = ("message @ %f" % time.time()).encode("utf-8")

        print(msg)
        sig = bls_sign(priv, msg)

        print("sig", sig)

        ok = bls_verify(pub, msg, sig)
        assert ok


if __name__ == '__main__':
    test()
