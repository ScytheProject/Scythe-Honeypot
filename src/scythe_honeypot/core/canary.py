"""Canary data model - Scythe Honeypot."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class CanaryType(str, Enum):
    """Types of canary files we can deploy."""
    WALLET   = "wallet"       # .dat - faux wallet crypto
    SSH_KEY  = "ssh_key"      # .pem - fausse clé privée SSH
    PASSWORD = "password"     # .txt - faux fichier de mots de passe
    DATABASE = "database"     # .sql - faux dump SQL
    PDF      = "pdf"          # .pdf - faux doc confidentiel
    ZIP      = "zip"          # .zip - fausse archive

    @property
    def extension(self) -> str:
        """File extension for this type."""
        return {
            self.WALLET: ".dat",
            self.SSH_KEY: ".pem",
            self.PASSWORD: ".txt",
            self.DATABASE: ".sql",
            self.PDF: ".pdf",
            self.ZIP: ".zip",
        }[self]

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return {
            self.WALLET: "Crypto Wallet",
            self.SSH_KEY: "SSH Private Key",
            self.PASSWORD: "Password File",
            self.DATABASE: "Database Dump",
            self.PDF: "Confidential PDF",
            self.ZIP: "Source Archive",
        }[self]


class CanaryStatus(str, Enum):
    """Current status of a canary."""
    ARMED     = "armed"      # En place, prêt à détecter
    TRIGGERED = "triggered"  # A été touché par quelque chose
    DISARMED  = "disarmed"   # Désactivé temporairement
    ERROR     = "error"      # Problème (fichier introuvable, etc.)


class CanaryDetectionOptions(BaseModel):
    """Options to configure what triggers an alert."""
    on_read: bool          = True
    on_open: bool          = True
    on_copy: bool          = False
    on_modify: bool        = True
    capture_process: bool  = True


class Canary(BaseModel):
    """A canary file - a trap deployed to detect intrusions."""

    id: int                       = 0  # auto-set by DB
    name: str                     = Field(..., min_length=1, max_length=64)
    type: CanaryType
    path: str                     # Full file path on disk
    status: CanaryStatus          = CanaryStatus.ARMED
    detection: CanaryDetectionOptions = Field(default_factory=CanaryDetectionOptions)
    created_at: datetime          = Field(default_factory=datetime.now)
    last_triggered_at: Optional[datetime] = None
    trigger_count: int            = 0

    @property
    def filepath(self) -> Path:
        """Full Path object including filename + extension."""
        return Path(self.path) / f"{self.name}{self.type.extension}"

    @property
    def short_path(self) -> str:
        """Truncated path for display."""
        full = str(self.filepath)
        if len(full) > 30:
            return full[:15] + "..." + full[-12:]
        return full