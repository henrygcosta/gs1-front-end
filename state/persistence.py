"""Optional persistence adapter for human feedback history using SQLite.

This module provides a lightweight adapter to persist moderation records so
that decisions survive Streamlit sessions. Persistence is optional and
controlled via settings in `utils.config`.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from utils.config import get_settings


def init_db() -> None:
    """Initialize the SQLite database and tables if persistence is enabled."""
    settings = get_settings()
    if not settings.enable_feedback_persistence:
        return
    db_path = Path(settings.feedback_db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT,
                event_id TEXT,
                decision TEXT,
                status TEXT,
                created_at TEXT,
                payload JSON
            )
            """
        )
        conn.commit()


def save_feedback(record: dict[str, object]) -> None:
    """Persist a feedback record to the database if enabled."""
    settings = get_settings()
    if not settings.enable_feedback_persistence:
        return
    db_path = Path(settings.feedback_db_path)
    payload = json.dumps({k: (v if v is not None else None) for k, v in record.items()}, default=str, ensure_ascii=False)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO feedback_history (alert_id, event_id, decision, status, created_at, payload) VALUES (?, ?, ?, ?, ?, ?)",
            (
                record.get("alert_id"),
                record.get("event_id"),
                record.get("decision"),
                record.get("status"),
                record.get("created_at"),
                payload,
            ),
        )
        conn.commit()


def fetch_history(limit: int = 200) -> list[dict[str, object]]:
    """Return persisted feedback history as a list of records (most recent first)."""
    settings = get_settings()
    if not settings.enable_feedback_persistence:
        return []
    db_path = Path(settings.feedback_db_path)
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT payload FROM feedback_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
    results: list[dict[str, object]] = []
    for (payload_json,) in rows:
        try:
            results.append(json.loads(payload_json))
        except Exception:
            # best-effort parse fallback
            results.append({"payload": payload_json})
    return results
