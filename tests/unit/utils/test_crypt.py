import pytest
from cryptography.fernet import Fernet, InvalidToken

from forgesteel_warehouse.utils.crypt import Crypt


def test_crypt_string_key():
    test_key_str = Fernet.generate_key().decode("utf-8")
    c = Crypt(test_key_str)
    test_str = "some string 1234"

    enc = c.encrypt(test_str)
    assert enc != test_str

    dec = c.decrypt(enc)
    assert dec == test_str


def test_crypt_multi_key():
    test_key_1 = Fernet.generate_key().decode("utf-8")
    test_key_2 = Fernet.generate_key().decode("utf-8")
    test_key_multi = ";".join([test_key_2, test_key_1])

    c = Crypt(test_key_multi)
    test_str = "some string 1234"

    enc = c.encrypt(test_str)
    assert enc != test_str

    dec = c.decrypt(enc)
    assert dec == test_str


def test_crypt_multi_key_rotated():
    test_key_1 = Fernet.generate_key().decode("utf-8")
    test_key_2 = Fernet.generate_key().decode("utf-8")
    test_key_multi = ";".join([test_key_2, test_key_1])

    c1 = Crypt(test_key_1)
    test_str = "some string 1234"

    ## Encrypt with some original key
    enc1 = c1.encrypt(test_str)
    assert enc1 != test_str
    dec1 = c1.decrypt(enc1)
    assert dec1 == test_str

    ## need to rotate the keys! add new key as first in multi-key, and rotate
    cr = Crypt(test_key_multi)
    dec2 = cr.decrypt(enc1)
    assert dec2 == test_str
    rot = cr.rotate(enc1)
    decRot = cr.decrypt(rot)
    assert decRot == test_str

    ## initial key no longer works
    with pytest.raises(InvalidToken):
        c1.decrypt(rot)

    ## now we can decode using only the new key
    c2 = Crypt(test_key_2)
    dec2 = c2.decrypt(rot)
    assert dec2 == test_str
