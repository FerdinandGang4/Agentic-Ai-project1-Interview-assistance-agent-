"""Gradio-facing auth handlers. Keeps login/register/logout out of app.py."""

from __future__ import annotations

import html
from typing import Any

import gradio as gr

from .users import login_user, register_user


def render_user_chip(user: dict | None) -> str:
    if not user:
        return (
            '<div class="user-chip user-chip-guest">'
            "<span>Not signed in</span>"
            "</div>"
        )
    name = html.escape(user.get("name", "User"))
    email = html.escape(user.get("email", ""))
    initial = html.escape((user.get("name") or "U")[:1].upper())
    return (
        '<div class="user-chip">'
        f'<div class="user-avatar">{initial}</div>'
        '<div class="user-meta">'
        f"<strong>{name}</strong>"
        f"<span>{email}</span>"
        "</div>"
        "</div>"
    )


def _logged_in_ui(user: dict, message: str) -> tuple[Any, ...]:
    return (
        user,
        render_user_chip(user),
        message,
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
        "",
        "",
        "",
    )


def _logged_out_ui(message: str) -> tuple[Any, ...]:
    return (
        None,
        render_user_chip(None),
        message,
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        "",
        "",
        "",
    )


def handle_register(name: str, email: str, password: str) -> tuple[Any, ...]:
    user, message = register_user(name, email, password)
    if user is None:
        return (
            None,
            render_user_chip(None),
            f"❌ {message}",
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            name,
            email,
            "",
        )
    return _logged_in_ui(user, f"✅ {message}")


def handle_login(email: str, password: str) -> tuple[Any, ...]:
    user, message = login_user(email, password)
    if user is None:
        return (
            None,
            render_user_chip(None),
            f"❌ {message}",
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            "",
            email,
            "",
        )
    return _logged_in_ui(user, f"✅ {message}")


def handle_logout() -> tuple[Any, ...]:
    return _logged_out_ui("👋 Signed out. Log in to continue.")
