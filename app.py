from __future__ import annotations

import base64
import hashlib
import io
import os
from datetime import datetime
from typing import Optional, Tuple

from flask import Flask, jsonify, render_template, request, send_file

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(APP_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "operations.log")

app = Flask(__name__)

BLOCK_SIZE = 8


class ValidationError(Exception):
    pass


# ─────────────────────────────────────────────
# BẢNG HẰNG SỐ DES (FIPS 46-3)
# ─────────────────────────────────────────────

IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
]

FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
]

E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1,
]

P = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25,
]

PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4,
]

PC2 = [
    14, 17, 11, 24, 1, 5, 3, 28,
    15, 6, 21, 10, 23, 19, 12, 4,
    26, 8, 16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55, 30, 40,
    51, 45, 33, 48, 44, 49, 39, 56,
    34, 53, 46, 42, 50, 36, 29, 32,
]

SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

SBOXES = [
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]],
]


def _ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def _log_event(kind: str, operation: str, mode: str, size: int, duration_ms: int) -> None:
    _ensure_log_dir()
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp}\t{kind}\t{operation}\t{mode}\t{size}\t{duration_ms}ms\n"
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(line)


def bytes_to_bits(data: bytes) -> list:
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_bytes(bits: list) -> bytes:
    result = []
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit
        result.append(byte)
    return bytes(result)


def permute(bits: list, table: list) -> list:
    return [bits[i - 1] for i in table]


def xor_bits(a: list, b: list) -> list:
    return [x ^ y for x, y in zip(a, b)]


def left_shift(bits: list, n: int) -> list:
    return bits[n:] + bits[:n]


def generate_subkeys(key_bytes: bytes) -> list:
    key_bits = bytes_to_bits(key_bytes)
    key_56 = permute(key_bits, PC1)
    c = key_56[:28]
    d = key_56[28:]

    subkeys = []
    for shift in SHIFT_SCHEDULE:
        c = left_shift(c, shift)
        d = left_shift(d, shift)
        subkeys.append(permute(c + d, PC2))
    return subkeys


def s_box_substitute(bits_48: list) -> list:
    output = []
    for i in range(8):
        chunk = bits_48[i * 6:i * 6 + 6]
        row = (chunk[0] << 1) | chunk[5]
        col = (chunk[1] << 3) | (chunk[2] << 2) | (chunk[3] << 1) | chunk[4]
        val = SBOXES[i][row][col]
        for bit_pos in range(3, -1, -1):
            output.append((val >> bit_pos) & 1)
    return output


def f_function(r_bits: list, subkey: list) -> list:
    expanded = permute(r_bits, E)
    xored = xor_bits(expanded, subkey)
    substituted = s_box_substitute(xored)
    return permute(substituted, P)


def des_block(block_bytes: bytes, subkeys: list) -> bytes:
    bits = bytes_to_bits(block_bytes)
    perm = permute(bits, IP)

    l_bits = perm[:32]
    r_bits = perm[32:]

    for subkey in subkeys:
        l_bits, r_bits = r_bits, xor_bits(l_bits, f_function(r_bits, subkey))

    combined = r_bits + l_bits
    cipher_bits = permute(combined, FP)
    return bits_to_bytes(cipher_bits)


def des_encrypt_block(block: bytes, key: bytes) -> bytes:
    return des_block(block, generate_subkeys(key))


def des_decrypt_block(block: bytes, key: bytes) -> bytes:
    return des_block(block, generate_subkeys(key)[::-1])


def triple_des_encrypt_block(block: bytes, k1: bytes, k2: bytes, k3: bytes) -> bytes:
    step1 = des_encrypt_block(block, k1)
    step2 = des_decrypt_block(step1, k2)
    return des_encrypt_block(step2, k3)


def triple_des_decrypt_block(block: bytes, k1: bytes, k2: bytes, k3: bytes) -> bytes:
    step1 = des_decrypt_block(block, k3)
    step2 = des_encrypt_block(step1, k2)
    return des_decrypt_block(step2, k1)


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


def _is_hex_string(value: str) -> bool:
    value = value.strip()
    if len(value) == 0 or len(value) % 2 != 0:
        return False
    try:
        bytes.fromhex(value)
        return True
    except ValueError:
        return False


def _prepare_key(key_input: str) -> Tuple[bytes, bytes, bytes]:
    key_input = key_input.strip()
    if not key_input:
        raise ValidationError("Vui lòng nhập khóa.")

    if _is_hex_string(key_input):
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


def _prepare_iv(mode: str, iv_input: str, operation: str) -> Tuple[Optional[bytes], Optional[str]]:
    mode = mode.upper()
    iv_input = (iv_input or "").strip()

    if mode == "ECB":
        return None, None

    if operation == "decrypt" and not iv_input:
        raise ValidationError("Cần IV để giải mã với chế độ này.")

    if iv_input:
        if not _is_hex_string(iv_input):
            raise ValidationError("IV phải là chuỗi hex hợp lệ.")
        iv_bytes = bytes.fromhex(iv_input)
        if len(iv_bytes) != BLOCK_SIZE:
            raise ValidationError("IV phải dài 8 byte (16 ký tự hex).")
        return iv_bytes, iv_input.lower()

    iv_bytes = os.urandom(BLOCK_SIZE)
    return iv_bytes, iv_bytes.hex()


def _crypt_bytes(data: bytes, operation: str, mode: str, keys: Tuple[bytes, bytes, bytes], iv: Optional[bytes]) -> bytes:
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


def _generate_key_hex() -> str:
    return os.urandom(24).hex()


@app.context_processor
def inject_now() -> dict:
    return {"now": datetime.now}


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/guide")
def guide() -> str:
    return render_template("guide.html")


@app.route("/api/generate-key", methods=["POST"])
def generate_key() -> "flask.Response":
    key_hex = _generate_key_hex()
    key_base64 = base64.b64encode(bytes.fromhex(key_hex)).decode("ascii")
    return jsonify({"key_hex": key_hex, "key_base64": key_base64})


@app.route("/process-text", methods=["POST"])
def process_text() -> "flask.Response":
    operation = request.form.get("operation", "encrypt").lower()
    mode = request.form.get("mode", "CBC").upper()
    key_input = request.form.get("key", "")
    iv_input = request.form.get("iv", "")
    text = request.form.get("text", "")

    if operation not in ("encrypt", "decrypt"):
        return jsonify({"error": "Tác vụ không hợp lệ."}), 400

    try:
        keys = _prepare_key(key_input)
        iv, iv_hex = _prepare_iv(mode, iv_input, operation)
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    start = datetime.now()
    try:
        if operation == "encrypt":
            raw = text.encode("utf-8")
            encrypted = _crypt_bytes(raw, operation, mode, keys, iv)
            result = base64.b64encode(encrypted).decode("ascii")
        else:
            raw = base64.b64decode(text)
            decrypted = _crypt_bytes(raw, operation, mode, keys, iv)
            result = decrypted.decode("utf-8", errors="replace")
    except (ValueError, ValidationError, base64.binascii.Error) as exc:
        return jsonify({"error": f"Không thể xử lý dữ liệu: {exc}"}), 400

    duration_ms = int((datetime.now() - start).total_seconds() * 1000)
    _log_event("text", operation, mode, len(text.encode("utf-8")), duration_ms)

    return jsonify({"result": result, "iv_used": iv_hex, "duration_ms": duration_ms})


@app.route("/process-file", methods=["POST"])
def process_file() -> "flask.Response":
    operation = request.form.get("operation", "encrypt").lower()
    mode = request.form.get("mode", "CBC").upper()
    key_input = request.form.get("key", "")
    iv_input = request.form.get("iv", "")

    if operation not in ("encrypt", "decrypt"):
        return jsonify({"error": "Tác vụ không hợp lệ."}), 400

    if "file" not in request.files:
        return jsonify({"error": "Vui lòng chọn tập tin."}), 400

    upload = request.files["file"]
    if upload.filename == "":
        return jsonify({"error": "Tên tập tin không hợp lệ."}), 400

    try:
        keys = _prepare_key(key_input)
        iv, iv_hex = _prepare_iv(mode, iv_input, operation)
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    data = upload.read()

    start = datetime.now()
    try:
        processed = _crypt_bytes(data, operation, mode, keys, iv)
    except (ValueError, ValidationError) as exc:
        return jsonify({"error": f"Không thể xử lý tập tin: {exc}"}), 400

    duration_ms = int((datetime.now() - start).total_seconds() * 1000)
    _log_event("file", operation, mode, len(data), duration_ms)

    base_name = os.path.basename(upload.filename)
    if operation == "encrypt":
        output_name = f"{base_name}.des3"
    else:
        output_name = f"{base_name}.dec"

    buffer = io.BytesIO(processed)
    buffer.seek(0)

    response = send_file(
        buffer,
        as_attachment=True,
        download_name=output_name,
        mimetype="application/octet-stream",
    )
    if iv_hex:
        response.headers["X-IV-Used"] = iv_hex
    response.headers["X-Duration-Ms"] = str(duration_ms)
    return response


if __name__ == "__main__":
    app.run(debug=True)
