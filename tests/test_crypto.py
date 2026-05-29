import pytest

from crypto.modes import crypt_bytes, pkcs7_pad, pkcs7_unpad
from crypto.triple_des import triple_des_decrypt_block, triple_des_encrypt_block
from utils.validators import ValidationError, prepare_key


KEY_HEX = "1234567890abcdef1234567890abcdef1234567890abcdef"
IV = bytes.fromhex("0102030405060708")


def test_pkcs7_padding_roundtrip_for_unaligned_data():
    data = b"hello triple des"

    padded = pkcs7_pad(data)

    assert len(padded) % 8 == 0
    assert pkcs7_unpad(padded) == data


def test_pkcs7_padding_adds_full_block_for_aligned_data():
    data = b"12345678"

    padded = pkcs7_pad(data)

    assert len(padded) == 16
    assert padded[-1] == 8
    assert pkcs7_unpad(padded) == data


def test_pkcs7_unpad_rejects_invalid_padding():
    with pytest.raises(ValidationError):
        pkcs7_unpad(b"invalid\x00")


def test_triple_des_block_encrypt_then_decrypt_returns_original_block():
    k1, k2, k3 = prepare_key(KEY_HEX)
    block = b"12345678"

    encrypted = triple_des_encrypt_block(block, k1, k2, k3)
    decrypted = triple_des_decrypt_block(encrypted, k1, k2, k3)

    assert encrypted != block
    assert decrypted == block


@pytest.mark.parametrize("mode", ["ECB", "CBC", "CFB"])
def test_modes_encrypt_then_decrypt_returns_original_data(mode):
    keys = prepare_key(KEY_HEX)
    iv = None if mode == "ECB" else IV
    data = b"roundtrip payload for ecb cbc cfb"

    encrypted = crypt_bytes(data, "encrypt", mode, keys, iv)
    decrypted = crypt_bytes(encrypted, "decrypt", mode, keys, iv)

    assert decrypted == data
