from __future__ import annotations

import base64
import io
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from crypto.modes import crypt_bytes
from utils.logger import log_event
from utils.validators import ValidationError, prepare_iv, prepare_key

app = Flask(__name__)
MAX_UPLOAD_SIZE = 16 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _generate_key_hex() -> str:
    return os.urandom(24).hex()


@app.context_processor
def inject_now() -> dict:
    return {"now": datetime.now}


@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(exc: RequestEntityTooLarge) -> tuple:
    limit_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
    return jsonify({"error": f"Tập tin vượt quá giới hạn {limit_mb}MB."}), 413


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
        keys = prepare_key(key_input)
        iv, iv_hex = prepare_iv(mode, iv_input, operation)
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    start = datetime.now()
    try:
        if operation == "encrypt":
            raw = text.encode("utf-8")
            encrypted = crypt_bytes(raw, operation, mode, keys, iv)
            result = base64.b64encode(encrypted).decode("ascii")
        else:
            raw = base64.b64decode(text)
            decrypted = crypt_bytes(raw, operation, mode, keys, iv)
            result = decrypted.decode("utf-8", errors="replace")
    except (ValueError, ValidationError, base64.binascii.Error) as exc:
        return jsonify({"error": f"Không thể xử lý dữ liệu: {exc}"}), 400

    duration_ms = int((datetime.now() - start).total_seconds() * 1000)
    log_event("text", operation, mode, len(text.encode("utf-8")), duration_ms)

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
        keys = prepare_key(key_input)
        iv, iv_hex = prepare_iv(mode, iv_input, operation)
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    data = upload.read()

    start = datetime.now()
    try:
        processed = crypt_bytes(data, operation, mode, keys, iv)
    except (ValueError, ValidationError) as exc:
        return jsonify({"error": f"Không thể xử lý tập tin: {exc}"}), 400

    duration_ms = int((datetime.now() - start).total_seconds() * 1000)
    log_event("file", operation, mode, len(data), duration_ms)

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
    app.run(debug=_env_flag("FLASK_DEBUG"))
