import base64
import re
from io import BytesIO

import pytest

import app as app_module


KEY_HEX = "1234567890abcdef1234567890abcdef1234567890abcdef"
IV_HEX = "0102030405060708"


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(app_module, "log_event", lambda *args, **kwargs: None)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_generate_key_returns_hex_and_base64(client):
    response = client.post("/api/generate-key")

    assert response.status_code == 200
    data = response.get_json()
    assert re.fullmatch(r"[0-9a-f]{48}", data["key_hex"])
    assert base64.b64decode(data["key_base64"]) == bytes.fromhex(data["key_hex"])


def test_process_text_cbc_encrypt_then_decrypt_returns_plaintext(client):
    plaintext = "hello Triple DES"

    encrypt_response = client.post(
        "/process-text",
        data={
            "operation": "encrypt",
            "mode": "CBC",
            "key": KEY_HEX,
            "iv": IV_HEX,
            "text": plaintext,
        },
    )

    assert encrypt_response.status_code == 200
    encrypted_data = encrypt_response.get_json()
    assert encrypted_data["result"] != plaintext
    assert encrypted_data["iv_used"] == IV_HEX

    decrypt_response = client.post(
        "/process-text",
        data={
            "operation": "decrypt",
            "mode": "CBC",
            "key": KEY_HEX,
            "iv": IV_HEX,
            "text": encrypted_data["result"],
        },
    )

    assert decrypt_response.status_code == 200
    assert decrypt_response.get_json()["result"] == plaintext


def test_process_file_too_large_returns_json_error(client):
    original_limit = app_module.app.config["MAX_CONTENT_LENGTH"]
    app_module.app.config["MAX_CONTENT_LENGTH"] = 128
    try:
        response = client.post(
            "/process-file",
            data={
                "operation": "encrypt",
                "mode": "CBC",
                "key": KEY_HEX,
                "iv": IV_HEX,
                "file": (BytesIO(b"x" * 1024), "large.txt"),
            },
            content_type="multipart/form-data",
        )
    finally:
        app_module.app.config["MAX_CONTENT_LENGTH"] = original_limit

    assert response.status_code == 413
    assert response.is_json
    assert "vượt quá giới hạn" in response.get_json()["error"]
