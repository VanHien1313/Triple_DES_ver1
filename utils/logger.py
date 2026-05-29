from __future__ import annotations

import os
from datetime import datetime

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(APP_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "operations.log")


def ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def log_event(kind: str, operation: str, mode: str, size: int, duration_ms: int) -> None:
    ensure_log_dir()
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp}\t{kind}\t{operation}\t{mode}\t{size}\t{duration_ms}ms\n"
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(line)
