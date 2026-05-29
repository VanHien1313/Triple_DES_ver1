from __future__ import annotations

import hashlib
import os
from typing import Optional, Tuple

from crypto.des import BLOCK_SIZE


class ValidationError(Exception):
    pass


def is_hex_string(value: str) -> bool:
    value = value.strip()
    if len(value) == 0 or len(value) % 2 != 0:
        return False
    try:
        bytes.fromhex(value)
        return True
    except ValueError:
        return False


def prepare_key(key_input: str) -> Tuple[bytes, bytes, bytes]:
    key_input = key_input.strip()
    if not key_input:
        raise ValidationError("Vui lòng nhập khóa.")

    if is_hex_string(key_input):
        key_bytes = bytes.fromhex(key_input)
        if len(key_bytes) not in (16, 24):
            raise ValidationError("Khóa hex phải dài 16 hoặc 24 byte (32/48 ký tự hex).")
    else:
        digest = hashlib.sha256(key_input.encode("utf-8")).digest()
        key_bytes = digest[:24]

    if len(key_bytes) == 16:
        k1 = key_bytes[:8]
        k2 = key_bytes[8:16]
        k3 = k1
    else:
        k1 = key_bytes[:8]
        k2 = key_bytes[8:16]
        k3 = key_bytes[16:24]

    return k1, k2, k3


def prepare_iv(mode: str, iv_input: str, operation: str) -> Tuple[Optional[bytes], Optional[str]]:
    mode = mode.upper()
    iv_input = (iv_input or "").strip()

    if mode == "ECB":
        return None, None

    if operation == "decrypt" and not iv_input:
        raise ValidationError("Cần IV để giải mã với chế độ này.")

    if iv_input:
        if not is_hex_string(iv_input):
            raise ValidationError("IV phải là chuỗi hex hợp lệ.")
        iv_bytes = bytes.fromhex(iv_input)
        if len(iv_bytes) != BLOCK_SIZE:
            raise ValidationError("IV phải dài 8 byte (16 ký tự hex).")
        return iv_bytes, iv_input.lower()

    iv_bytes = os.urandom(BLOCK_SIZE)
    return iv_bytes, iv_bytes.hex()
