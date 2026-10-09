"""UI helpers for library dropdowns and history preview."""

from __future__ import annotations

import html

import gradio as gr

from .conversations import conversation_title, get_conversation, list_conversations
from .documents import list_documents


def user_key(user: dict | None) -> str:
    if not user:
        return ""
    return (user.get("email") or "").strip().lower()


def document_choices(email: str, kind: str) -> list[tuple[str, str]]:
    items = list_documents(email, kind)
    return [(f"{item['name']}  ·  {item['id']}", item["id"]) for item in items]


def conversation_choices(email: str) -> list[tuple[str, str]]:
    rows = list_conversations(email)
    choices = []
    for row in rows:
        label = conversation_title(
            job_name=row.get("job_name") or "",
            created_at=row.get("created_at") or "",
        )
        choices.append((label, row["id"]))
    return choices


def library_dropdowns(user: dict | None) -> tuple:
    email = user_key(user)
    if not email:
        empty = gr.update(choices=[], value=None)
        return empty, empty, empty, "Select a past interview to review.", None, None

    resumes = document_choices(email, "resume")
    jobs = document_choices(email, "job")
    history = conversation_choices(email)
    return (
        gr.update(choices=resumes, value=resumes[0][1] if resumes else None),
        gr.update(choices=jobs, value=jobs[0][1] if jobs else None),
        gr.update(choices=history, value=None),
        "Select a past interview to review.",
        None,
        None,
    )


def render_conversation_preview(email: str, conversation_id: str) -> tuple[str, str | None, str | None]:
    data = get_conversation(email, conversation_id)
    if not data:
        return "Conversation not found.", None, None

    display_title = conversation_title(
        job_name=data.get("job_name") or "",
        created_at=data.get("created_at") or "",
    )
    parts = [
        f"<div class='history-preview'>",
        f"<strong>{html.escape(display_title)}</strong>",
        f"<div class='history-meta'>{html.escape(data.get('resume_name') or 'Resume')} · "
        f"{html.escape(data.get('job_name') or 'Job description')} · "
        f"{data.get('turn_count', 0)} answers</div>",
    ]
    first_q_audio = None
    first_a_audio = None
    for turn in data.get("turns", []):
        q = html.escape(turn.get("question") or "")
        a = html.escape(turn.get("answer") or "")
        parts.append(
            f"<div class='history-turn'><div class='hq'>Q{turn.get('index')}: {q}</div>"
            f"<div class='ha'>A: {a}</div></div>"
        )
        if not first_q_audio and turn.get("question_audio"):
            first_q_audio = turn["question_audio"]
        if not first_a_audio and turn.get("answer_audio"):
            first_a_audio = turn["answer_audio"]

    feedback = (data.get("feedback") or "").strip()
    if feedback:
        parts.append(f"<div class='history-feedback'><strong>Feedback</strong><br>{html.escape(feedback)}</div>")
    parts.append("</div>")
    return "\n".join(parts), first_q_audio, first_a_audio


def audio_choices_for_conversation(email: str, conversation_id: str) -> list[tuple[str, str]]:
    data = get_conversation(email, conversation_id)
    if not data:
        return []
    choices = []
    for turn in data.get("turns", []):
        idx = turn.get("index")
        if turn.get("question_audio"):
            choices.append((f"Q{idx} question audio", turn["question_audio"]))
        if turn.get("answer_audio"):
            choices.append((f"Q{idx} your answer audio", turn["answer_audio"]))
    return choices
