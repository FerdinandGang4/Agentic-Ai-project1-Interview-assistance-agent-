"""Persist and reload past interview conversations (text + audio)."""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import conversations_dir


def conversation_title(job_name: str = "", created_at: str = "") -> str:
    """Meaningful label: job-file stem - local-looking datetime."""
    stem = Path(job_name).stem.strip() if job_name else ""
    if not stem:
        stem = "Interview"

    stamp = ""
    if created_at:
        try:
            # 2026-10-09T19:13:56... -> 2026-10-09 19:13
            stamp = created_at.replace("T", " ")[:16]
        except Exception:
            stamp = str(created_at)[:16]
    if not stamp:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    return f"{stem} - {stamp}"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def list_conversations(email: str) -> list[dict]:
    root = conversations_dir(email)
    rows = []
    for folder in sorted(root.iterdir(), reverse=True):
        if not folder.is_dir():
            continue
        meta = _load_json(folder / "meta.json", {})
        if not meta:
            continue
        meta["id"] = meta.get("id") or folder.name
        meta["path"] = str(folder)
        rows.append(meta)
    rows.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return rows


def get_conversation(email: str, conversation_id: str) -> dict | None:
    if not conversation_id:
        return None
    folder = conversations_dir(email) / conversation_id
    if not folder.exists():
        return None
    meta = _load_json(folder / "meta.json", {})
    turns = _load_json(folder / "turns.json", [])
    if not meta:
        return None
    meta["id"] = conversation_id
    meta["turns"] = turns if isinstance(turns, list) else []
    return meta


def save_conversation(
    email: str,
    *,
    questions: list[str],
    answers: list[str],
    feedback: str,
    question_audio_paths: list[str | None] | None = None,
    answer_audio_paths: list[str | None] | None = None,
    resume_name: str = "",
    job_name: str = "",
) -> dict:
    conversation_id = uuid.uuid4().hex[:12]
    folder = conversations_dir(email) / conversation_id
    audio_dir = folder / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    q_audio = question_audio_paths or []
    a_audio = answer_audio_paths or []
    turns = []
    for index, (question, answer) in enumerate(zip(questions, answers), start=1):
        turn = {
            "index": index,
            "question": question,
            "answer": answer,
            "question_audio": None,
            "answer_audio": None,
        }
        if index - 1 < len(q_audio) and q_audio[index - 1]:
            src = Path(q_audio[index - 1])
            if src.exists():
                dest = audio_dir / f"q{index}{src.suffix or '.mp3'}"
                shutil.copy2(src, dest)
                turn["question_audio"] = str(dest)
        if index - 1 < len(a_audio) and a_audio[index - 1]:
            src = Path(a_audio[index - 1])
            if src.exists():
                dest = audio_dir / f"a{index}{src.suffix or '.wav'}"
                shutil.copy2(src, dest)
                turn["answer_audio"] = str(dest)
        turns.append(turn)

    created_at = datetime.now(timezone.utc).isoformat()
    title = conversation_title(job_name=job_name, created_at=created_at)

    meta = {
        "id": conversation_id,
        "title": title,
        "created_at": created_at,
        "resume_name": resume_name,
        "job_name": job_name,
        "turn_count": len(turns),
        "feedback": feedback or "",
    }
    (folder / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (folder / "turns.json").write_text(json.dumps(turns, indent=2), encoding="utf-8")
    return meta
