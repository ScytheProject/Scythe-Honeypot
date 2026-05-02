"""SQLite wrapper for canaries persistence - Scythe Honeypot."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from scythe_honeypot.core.canary import (
    Canary,
    CanaryDetectionOptions,
    CanaryStatus,
    CanaryType,
)
from scythe_honeypot.core.event import EventType, TriggerEvent


DEFAULT_DB_PATH = Path.home() / ".scythe-honeypot" / "canaries.db"


class CanaryDatabase:
    """SQLite database for canaries and their events."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS canaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'armed',
                    detection_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_triggered_at TEXT,
                    trigger_count INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canary_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    process_name TEXT,
                    process_pid INTEGER,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (canary_id) REFERENCES canaries(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    # ---------- CANARIES ----------

    def insert_canary(self, canary: Canary) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO canaries
                   (name, type, path, status, detection_json, created_at, last_triggered_at, trigger_count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    canary.name,
                    canary.type.value,
                    canary.path,
                    canary.status.value,
                    canary.detection.model_dump_json(),
                    canary.created_at.isoformat(),
                    canary.last_triggered_at.isoformat() if canary.last_triggered_at else None,
                    canary.trigger_count,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def list_canaries(self) -> list[Canary]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM canaries ORDER BY created_at DESC").fetchall()
            return [self._row_to_canary(row) for row in rows]

    def get_canary(self, canary_id: int) -> Optional[Canary]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM canaries WHERE id = ?", (canary_id,)).fetchone()
            return self._row_to_canary(row) if row else None

    def delete_canary(self, canary_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM canaries WHERE id = ?", (canary_id,))
            conn.commit()

    def update_status(self, canary_id: int, status: CanaryStatus) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE canaries SET status = ? WHERE id = ?",
                (status.value, canary_id),
            )
            conn.commit()

    def mark_triggered(self, canary_id: int) -> None:
        """Update status + last_triggered_at + increment trigger_count atomically."""
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """UPDATE canaries
                   SET status = ?,
                       last_triggered_at = ?,
                       trigger_count = trigger_count + 1
                   WHERE id = ?""",
                (CanaryStatus.TRIGGERED.value, now, canary_id),
            )
            conn.commit()

    def count_by_status(self, status: CanaryStatus) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM canaries WHERE status = ?",
                (status.value,),
            ).fetchone()
            return row["n"]

    def total_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM canaries").fetchone()
            return row["n"]

    # ---------- EVENTS ----------

    def insert_event(self, event: TriggerEvent) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO events
                   (canary_id, event_type, process_name, process_pid, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    event.canary_id,
                    event.event_type.value,
                    event.process_name,
                    event.process_pid,
                    event.timestamp.isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def list_recent_events(self, limit: int = 20) -> list[TriggerEvent]:
        """Get the N most recent events with canary names joined."""
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT e.*, c.name AS canary_name
                   FROM events e
                   LEFT JOIN canaries c ON c.id = e.canary_id
                   ORDER BY e.timestamp DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [self._row_to_event(row) for row in rows]

    def get_last_event(self) -> Optional[TriggerEvent]:
        """Get the single most recent event."""
        events = self.list_recent_events(limit=1)
        return events[0] if events else None

    def total_events(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()
            return row["n"]

    # ---------- INTERNAL ----------

    @staticmethod
    def _row_to_canary(row: sqlite3.Row) -> Canary:
        detection_data = json.loads(row["detection_json"])
        return Canary(
            id=row["id"],
            name=row["name"],
            type=CanaryType(row["type"]),
            path=row["path"],
            status=CanaryStatus(row["status"]),
            detection=CanaryDetectionOptions(**detection_data),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_triggered_at=(
                datetime.fromisoformat(row["last_triggered_at"])
                if row["last_triggered_at"] else None
            ),
            trigger_count=row["trigger_count"],
        )

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> TriggerEvent:
        return TriggerEvent(
            id=row["id"],
            canary_id=row["canary_id"],
            canary_name=row["canary_name"] or "<deleted>",
            event_type=EventType(row["event_type"]),
            process_name=row["process_name"],
            process_pid=row["process_pid"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
        )