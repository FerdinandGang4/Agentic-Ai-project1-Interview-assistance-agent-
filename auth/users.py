"""Simple email/password auth with hashed passwords stored in users.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

import bcrypt

USERS_FILE = Path(__file__).resolve().parent / "users.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict) -> None:
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def get_public_user(user: dict | None) -> dict | None:
    if not user:
        return None
    return {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
    }


def register_user(name: str, email: str, password: str) -> tuple[dict | None, str]:
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if len(name) < 2:
        return None, "Please enter your full name (at least 2 characters)."
    if not EMAIL_RE.match(email):
        return None, "Please enter a valid email address."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."

    users = _load_users()
    if email in users:
        return None, "An account with this email already exists. Please log in."

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users[email] = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
    }
    _save_users(users)
    return get_public_user(users[email]), f"Welcome, {name}! Account created."


def login_user(email: str, password: str) -> tuple[dict | None, str]:
    email = (email or "").strip().lower()
    password = password or ""

    if not email or not password:
        return None, "Email and password are required."

    users = _load_users()
    record = users.get(email)
    if not record:
        return None, "Invalid email or password."

    stored = record.get("password_hash", "").encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored):
        return None, "Invalid email or password."

    public = get_public_user(record)
    return public, f"Welcome back, {public['name']}!"
