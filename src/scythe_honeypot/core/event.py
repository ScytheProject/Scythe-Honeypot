"""Trigger event model - Scythe Honeypot."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Type of file system event detected on a canary."""
    READ     = "read"      # Lecture du fichier
    MODIFIED = "modified"  # Contenu modifié
    DELETED  = "deleted"   # Fichier supprimé
    MOVED    = "moved"     # Fichier déplacé/renommé
    OPENED   = "opened"    # Fichier ouvert (proxy de READ pour Windows)


class TriggerEvent(BaseModel):
    """An event that triggered a canary alert."""

    id: int                       = 0  # auto-set by DB
    canary_id: int
    canary_name: str              = ""  # denormalisé pour afficher facilement
    event_type: EventType
    process_name: Optional[str]   = None
    process_pid: Optional[int]    = None
    timestamp: datetime           = Field(default_factory=datetime.now)

    @property
    def time_str(self) -> str:
        """Format HH:MM:SS for display."""
        return self.timestamp.strftime("%H:%M:%S")

    @property
    def event_label(self) -> str:
        """Uppercase label for display."""
        return self.event_type.value.upper()