"""Service layer that orchestrates canary creation - Scythe Honeypot."""

from pathlib import Path
from typing import Optional

from scythe_honeypot.core.canary import (
    Canary,
    CanaryDetectionOptions,
    CanaryStatus,
    CanaryType,
)
from scythe_honeypot.core.canary_factory import generate_content
from scythe_honeypot.core.event import TriggerEvent
from scythe_honeypot.storage.database import CanaryDatabase


class CanaryService:
    """Handles canary lifecycle: create file + persist + manage."""

    def __init__(self, db: Optional[CanaryDatabase] = None):
        self.db = db or CanaryDatabase()

    def deploy_canary(
        self,
        name: str,
        canary_type: CanaryType,
        deploy_path: str,
        detection: Optional[CanaryDetectionOptions] = None,
    ) -> Canary:
        path = Path(deploy_path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {deploy_path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {deploy_path}")

        canary = Canary(
            name=name,
            type=canary_type,
            path=str(path.resolve()),
            status=CanaryStatus.ARMED,
            detection=detection or CanaryDetectionOptions(),
        )

        target = canary.filepath
        if target.exists():
            raise ValueError(f"File already exists: {target}")

        content = generate_content(canary_type)

        try:
            target.write_bytes(content)
        except OSError as e:
            raise RuntimeError(f"Failed to write canary: {e}") from e

        canary.id = self.db.insert_canary(canary)
        return canary

    def list_canaries(self) -> list[Canary]:
        return self.db.list_canaries()

    def delete_canary(self, canary_id: int, also_delete_file: bool = True) -> None:
        canary = self.db.get_canary(canary_id)
        if canary is None:
            return

        if also_delete_file:
            try:
                canary.filepath.unlink(missing_ok=True)
            except OSError:
                pass

        self.db.delete_canary(canary_id)

    def get_canary(self, canary_id: int) -> Optional[Canary]:
        """Fetch a single canary by id."""
        return self.db.get_canary(canary_id)

    def disarm_canary(self, canary_id: int) -> None:
        """Pause monitoring without deleting (file stays on disk)."""
        from scythe_honeypot.core.canary import CanaryStatus
        self.db.update_status(canary_id, CanaryStatus.DISARMED)

    def rearm_canary(self, canary_id: int) -> None:
        """Resume monitoring after disarm."""
        from scythe_honeypot.core.canary import CanaryStatus
        self.db.update_status(canary_id, CanaryStatus.ARMED)

    def record_trigger(self, event: TriggerEvent) -> None:
        """Persist a trigger event and mark the canary as triggered."""
        self.db.insert_event(event)
        self.db.mark_triggered(event.canary_id)

    def get_recent_events(self, limit: int = 20) -> list[TriggerEvent]:
        return self.db.list_recent_events(limit=limit)

    def get_last_event(self) -> Optional[TriggerEvent]:
        return self.db.get_last_event()

    def get_stats(self) -> dict:
        return {
            "armed":     self.db.count_by_status(CanaryStatus.ARMED),
            "triggered": self.db.count_by_status(CanaryStatus.TRIGGERED),
            "total":     self.db.total_count(),
            "events":    self.db.total_events(),
        }