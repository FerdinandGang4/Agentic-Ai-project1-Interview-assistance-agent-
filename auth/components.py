"""Reusable Gradio auth UI pieces (professional, compact)."""

from __future__ import annotations

import gradio as gr

from .handlers import render_user_chip


def build_header() -> tuple[gr.HTML, gr.Button]:
    """Header: product title left, user chip + compact logout right."""
    with gr.Row(elem_id="app-header"):
        with gr.Column(scale=4, min_width=220):
            gr.Markdown(
                """
                **Interview workspace**
                # AI Interview Coach
                """,
                elem_id="header-copy",
            )
        with gr.Column(scale=0, min_width=280, elem_id="user-panel"):
            with gr.Row():
                user_chip = gr.HTML(render_user_chip(None), elem_id="user-chip")
                logout_button = gr.Button(
                    "Log out",
                    variant="secondary",
                    visible=False,
                    elem_id="logout-button",
                    scale=0,
                    min_width=84,
                )
    return user_chip, logout_button


def build_auth_panel() -> dict:
    """Compact login / register card."""
    with gr.Group(visible=True, elem_id="auth-section", elem_classes=["panel-card"]) as auth_section:
        gr.Markdown("### Account", elem_classes=["section-heading"])
        with gr.Row(equal_height=True):
            name_input = gr.Textbox(
                label="Name (new account)",
                placeholder="Your name",
                scale=1,
                max_lines=1,
            )
            email_input = gr.Textbox(
                label="Email",
                placeholder="you@example.com",
                scale=1,
                max_lines=1,
            )
            password_input = gr.Textbox(
                label="Password",
                type="password",
                placeholder="Min 6 chars",
                scale=1,
                max_lines=1,
            )
            with gr.Column(scale=0, min_width=120):
                login_button = gr.Button("Log in", variant="primary", elem_id="login-button")
                register_button = gr.Button(
                    "Register",
                    variant="secondary",
                    elem_id="register-button",
                )
        auth_status = gr.Textbox(
            label="Account status",
            value="Log in or register to open the interview workspace.",
            interactive=False,
            lines=1,
            max_lines=1,
            elem_id="auth-status",
            show_label=False,
        )

    return {
        "auth_section": auth_section,
        "name_input": name_input,
        "email_input": email_input,
        "password_input": password_input,
        "login_button": login_button,
        "register_button": register_button,
        "auth_status": auth_status,
    }
