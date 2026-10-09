"""Per-user local storage roots."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "user_data"


def user_dir(email: str) -> Path:
    email = (email or "").strip().lower()
    digest = hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]
    safe = re.sub(r"[^a-z0-9._-]+", "_", email)[:40] or "user"
    path = ROOT / f"{safe}_{digest}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def resumes_dir(email: str) -> Path:
    path = user_dir(email) / "resumes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def jobs_dir(email: str) -> Path:
    path = user_dir(email) / "job_descriptions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def conversations_dir(email: str) -> Path:
    path = user_dir(email) / "conversations"
    path.mkdir(parents=True, exist_ok=True)
    return path
