import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

from .config import settings
from .models import Ticket, TicketCreate


def init_db() -> None:
    with sqlite3.connect(settings.database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                summary TEXT NOT NULL,
                details TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


@contextmanager
def get_conn() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_ticket(payload: TicketCreate) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO tickets (user_id, category, summary, details, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'open', ?, ?)
            """,
            (
                payload.user_id,
                payload.category,
                payload.summary,
                payload.details,
                payload.priority,
                now,
                now,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_ticket(ticket_id: int) -> Optional[Ticket]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            return None

    return Ticket(
        id=row["id"],
        user_id=row["user_id"],
        category=row["category"],
        summary=row["summary"],
        details=row["details"],
        priority=row["priority"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def list_tickets(limit: int = 100) -> list[Ticket]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets ORDER BY datetime(created_at) DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [
        Ticket(
            id=row["id"],
            user_id=row["user_id"],
            category=row["category"],
            summary=row["summary"],
            details=row["details"],
            priority=row["priority"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        for row in rows
    ]


def update_ticket_status(ticket_id: int, status: str) -> bool:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, ticket_id),
        )
        conn.commit()
        return cur.rowcount > 0


def log_audit_event(event_type: str, payload: dict) -> None:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO audit_logs (event_type, payload, created_at) VALUES (?, ?, ?)",
            (event_type, json.dumps(payload), now),
        )
        conn.commit()
