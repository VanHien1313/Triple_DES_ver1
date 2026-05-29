from __future__ import annotations

from typing import Optional, Tuple

from crypto.des import BLOCK_SIZE
from crypto.triple_des import triple_des_decrypt_block, triple_des_encrypt_block
from utils.validators import ValidationError


def pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    if not data:
        raise ValidationError("Padding không hợp lệ")
    pad_len = data[-1]
    if pad_len == 0 or pad_len > block_size:
        raise ValidationError("Padding không hợp lệ")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValidationError("Padding bị hỏng")
    return data[:-pad_len]


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def crypt_bytes(
    data: bytes,
    operation: str,
    mode: str,
    keys: Tuple[bytes, bytes, bytes],
    iv: Optional[bytes],
) -> bytes:
    mode = mode.upper()
    if mode not in ("ECB", "CBC", "CFB"):
        raise ValidationError("Chế độ không hợp lệ. Chỉ hỗ trợ ECB, CBC, CFB.")

    if mode in ("CBC", "CFB") and not iv:
        raise ValidationError(f"Thiếu IV cho chế độ {mode}.")

    k1, k2, k3 = keys

    if operation == "encrypt":
        if mode in ("ECB", "CBC"):
            data = pkcs7_pad(data)

        if mode == "ECB":
            return b"".join(
                triple_des_encrypt_block(data[i:i + BLOCK_SIZE], k1, k2, k3)
                for i in range(0, len(data), BLOCK_SIZE)
            )

        if mode == "CBC":
            ciphertext = b""
            prev = iv
            for i in range(0, len(data), BLOCK_SIZE):
                block = data[i:i + BLOCK_SIZE]
                block = _xor_bytes(block, prev)
                encrypted = triple_des_encrypt_block(block, k1, k2, k3)
                ciphertext += encrypted
                prev = encrypted
            return ciphertext

        ciphertext = b""
        prev = iv
        for i in range(0, len(data), BLOCK_SIZE):
            block = data[i:i + BLOCK_SIZE]
            keystream = triple_des_encrypt_block(prev, k1, k2, k3)
            cipher_block = _xor_bytes(block, keystream[:len(block)])
            ciphertext += cipher_block
            if len(block) == BLOCK_SIZE:
                prev = cipher_block
        return ciphertext

    if mode in ("ECB", "CBC") and len(data) % BLOCK_SIZE != 0:
        raise ValidationError("Dữ liệu không đúng kích thước khối 8 byte.")

    if mode == "ECB":
        decrypted = b"".join(
            triple_des_decrypt_block(data[i:i + BLOCK_SIZE], k1, k2, k3)
            for i in range(0, len(data), BLOCK_SIZE)
        )
        return pkcs7_unpad(decrypted)

    if mode == "CBC":
        plaintext = b""
        prev = iv
        for i in range(0, len(data), BLOCK_SIZE):
            block = data[i:i + BLOCK_SIZE]
            decrypted = triple_des_decrypt_block(block, k1, k2, k3)
            plaintext += _xor_bytes(decrypted, prev)
            prev = block
        return pkcs7_unpad(plaintext)

    plaintext = b""
    prev = iv
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i:i + BLOCK_SIZE]
        keystream = triple_des_encrypt_block(prev, k1, k2, k3)
        plain_block = _xor_bytes(block, keystream[:len(block)])
        plaintext += plain_block
        if len(block) == BLOCK_SIZE:
            prev = block
    return plaintext
