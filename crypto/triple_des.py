from __future__ import annotations

from crypto.des import des_decrypt_block, des_encrypt_block


def triple_des_encrypt_block(block: bytes, k1: bytes, k2: bytes, k3: bytes) -> bytes:
    step1 = des_encrypt_block(block, k1)
    step2 = des_decrypt_block(step1, k2)
    return des_encrypt_block(step2, k3)


def triple_des_decrypt_block(block: bytes, k1: bytes, k2: bytes, k3: bytes) -> bytes:
    step1 = des_decrypt_block(block, k3)
    step2 = des_encrypt_block(step1, k2)
    return des_decrypt_block(step2, k1)
