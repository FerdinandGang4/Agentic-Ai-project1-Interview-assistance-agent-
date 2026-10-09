"""High-level report builders used by the Gradio app."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from openai import OpenAI

from .exporters import (
    write_feedback_docx,
    write_feedback_pdf,
    write_study_pack_docx,
    write_study_pack_pdf,
)
from .study_pack_agent import StudyPackAgent

DOWNLOADS_DIR = Path(__file__).resolve().parent.parent / "downloads"


def _user_bits(user: dict | None) -> tuple[str, str]:
    user = user or {}
    return user.get("name") or "Candidate", user.get("email") or "unknown@example.com"


def build_feedback_report(
    *,
    user: dict | None,
    feedback: str,
    questions: list[str],
    answers: list[str],
    fmt: str = "pdf",
) -> str | None:
    if not (feedback or "").strip():
        return None

    name, email = _user_bits(user)
    qa_pairs = list(zip(questions, answers))
    file_id = uuid.uuid4().hex[:10]
    fmt = (fmt or "pdf").lower()
    if fmt == "docx":
        path = DOWNLOADS_DIR / f"feedback_{file_id}.docx"
        write_feedback_docx(
            path,
            candidate_name=name,
            candidate_email=email,
            feedback=feedback,
            qa_pairs=qa_pairs,
        )
    else:
        path = DOWNLOADS_DIR / f"feedback_{file_id}.pdf"
        write_feedback_pdf(
            path,
            candidate_name=name,
            candidate_email=email,
            feedback=feedback,
            qa_pairs=qa_pairs,
        )
    return str(path)


def build_study_pack(
    *,
    client: OpenAI,
    user: dict | None,
    analysis: dict[str, Any],
    resume_text: str,
    job_description: str,
    interview_questions: list[str] | None = None,
    fmt: str = "pdf",
) -> tuple[str | None, str]:
    if not analysis and not resume_text:
        return None, "Start an interview first so we can personalize the study pack."

    agent = StudyPackAgent(client)
    items = agent.generate(
        analysis=analysis or {},
        resume_text=resume_text or "",
        job_description=job_description or "",
        interview_questions=interview_questions,
    )
    if not items:
        return None, "Could not generate the study pack. Try again in a moment."

    name, email = _user_bits(user)
    file_id = uuid.uuid4().hex[:10]
    fmt = (fmt or "pdf").lower()
    if fmt == "docx":
        path = DOWNLOADS_DIR / f"study_pack_{file_id}.docx"
        write_study_pack_docx(
            path,
            candidate_name=name,
            candidate_email=email,
            items=items,
        )
    else:
        path = DOWNLOADS_DIR / f"study_pack_{file_id}.pdf"
        write_study_pack_pdf(
            path,
            candidate_name=name,
            candidate_email=email,
            items=items,
        )
    return str(path), f"Study pack ready ({len(items)} expected questions)."
