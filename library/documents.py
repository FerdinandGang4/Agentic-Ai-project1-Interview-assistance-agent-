"""Save / list / delete resume and job-description files per user."""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .paths import jobs_dir, resumes_dir

ALLOWED_EXT = {".pdf", ".docx", ".txt"}


def _index_path(folder: Path) -> Path:
    return folder / "index.json"


def _load_index(folder: Path) -> list[dict]:
    path = _index_path(folder)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_index(folder: Path, items: list[dict]) -> None:
    _index_path(folder).write_text(json.dumps(items, indent=2), encoding="utf-8")


def _folder_for(email: str, kind: str) -> Path:
    if kind == "resume":
        return resumes_dir(email)
    if kind == "job":
        return jobs_dir(email)
    raise ValueError(f"Unknown document kind: {kind}")


def list_documents(email: str, kind: str) -> list[dict]:
    folder = _folder_for(email, kind)
    items = _load_index(folder)
    # Drop missing files
    kept = []
    for item in items:
        path = folder / item.get("stored_name", "")
        if path.exists():
            kept.append(item)
    if len(kept) != len(items):
        _save_index(folder, kept)
    return kept


def save_document(email: str, kind: str, source_path: str | Path, display_name: str | None = None) -> dict:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")

    ext = source.suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("Only .pdf, .docx, and .txt files are supported.")

    folder = _folder_for(email, kind)
    doc_id = uuid.uuid4().hex[:10]
    original = display_name or source.name
    stored_name = f"{doc_id}_{original}"
    dest = folder / stored_name
    shutil.copy2(source, dest)

    item = {
        "id": doc_id,
        "name": original,
        "stored_name": stored_name,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    items = list_documents(email, kind)
    items.insert(0, item)
    _save_index(folder, items)
    return item


def get_document_path(email: str, kind: str, doc_id: str) -> Path | None:
    if not doc_id:
        return None
    folder = _folder_for(email, kind)
    for item in list_documents(email, kind):
        if item.get("id") == doc_id:
            path = folder / item["stored_name"]
            return path if path.exists() else None
    return None


def delete_document(email: str, kind: str, doc_id: str) -> bool:
    folder = _folder_for(email, kind)
    items = list_documents(email, kind)
    kept = []
    deleted = False
    for item in items:
        if item.get("id") == doc_id:
            path = folder / item.get("stored_name", "")
            if path.exists():
                path.unlink()
            deleted = True
        else:
            kept.append(item)
    if deleted:
        _save_index(folder, kept)
    return deleted
