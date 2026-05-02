"""Canary card widget - Scythe Honeypot."""

from datetime import datetime, timedelta

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Static

from scythe_honeypot.core.canary import Canary, CanaryStatus, CanaryType


# Icônes par type de canary
TYPE_ICONS = {
    CanaryType.WALLET:   "◆",  # diamant doré
    CanaryType.SSH_KEY:  "⚿",  # clé
    CanaryType.PASSWORD: "⚷",  # cadenas
    CanaryType.DATABASE: "⛁",  # cube DB
    CanaryType.PDF:      "▤",  # doc
    CanaryType.ZIP:      "▦",  # grille
}

# Affichage du statut avec icône
STATUS_DISPLAY = {
    CanaryStatus.ARMED:     "● ARMED",
    CanaryStatus.TRIGGERED: "▲ TRIGGERED",
    CanaryStatus.DISARMED:  "○ DISARMED",
    CanaryStatus.ERROR:     "✗ ERROR",
}


def _humanize_age(ts: datetime) -> str:
    """Convert a datetime to '2h ago' / '3d ago' format."""
    delta = datetime.now() - ts
    seconds = delta.total_seconds()

    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    return f"{int(seconds // 86400)}d ago"


def _shorten_path(path: str) -> str:
    """Shorten path with ~ for home directory."""
    from pathlib import Path
    home = str(Path.home())
    if path.startswith(home):
        path = "~" + path[len(home):]
    if len(path) > 50:
        return path[:25] + "..." + path[-22:]
    return path


class CanaryCard(Widget):
    """A card displaying one canary with action buttons."""

    # ---------- Messages bubble vers l'app ----------

    class Toggle(Message):
        """Pause/resume the canary."""
        def __init__(self, canary_id: int):
            super().__init__()
            self.canary_id = canary_id

    class View(Message):
        """Show details modal."""
        def __init__(self, canary_id: int):
            super().__init__()
            self.canary_id = canary_id

    class Delete(Message):
        """Request deletion."""
        def __init__(self, canary_id: int):
            super().__init__()
            self.canary_id = canary_id

    # ---------- Construction ----------

    def __init__(self, canary: Canary):
        super().__init__()
        self.canary = canary
        # CSS classes selon le status pour styling dynamique
        self.add_class(f"status-{canary.status.value}")

    def compose(self) -> ComposeResult:
        c = self.canary
        icon = TYPE_ICONS.get(c.type, "▪")
        status = STATUS_DISPLAY.get(c.status, c.status.value)
        type_label = c.type.display_name
        path_short = _shorten_path(str(c.filepath))
        age = _humanize_age(c.created_at)
        trigger_str = (
            f"{c.trigger_count} trigger{'s' if c.trigger_count != 1 else ''}"
        )

        # Toggle button label dépend du statut
        is_armed = c.status == CanaryStatus.ARMED
        is_triggered = c.status == CanaryStatus.TRIGGERED
        toggle_can_pause = is_armed or is_triggered
        toggle_label = "⏸ Pause" if toggle_can_pause else "▶ Resume"
        toggle_class = f"btn-toggle-{'pause' if toggle_can_pause else 'resume'}"

        with Vertical(classes="card-body"):
            # Header : icone + ID + nom à gauche, statut à droite
            with Horizontal(classes="card-header"):
                yield Static(
                    f"{icon}  #{c.id:04d}  ·  {c.name}",
                    classes=f"card-title type-{c.type.value}",
                )
                yield Static(status, classes=f"card-status status-{c.status.value}")

            # Sous-info : type · path
            yield Static(
                f"{type_label}  ·  {path_short}",
                classes="card-meta",
            )

            # Footer : metadata + boutons
            with Horizontal(classes="card-footer"):
                yield Static(f"Created {age}  ·  {trigger_str}", classes="card-stats")
                with Horizontal(classes="card-actions"):
                    yield Button(
                        toggle_label,
                        id=f"btn-toggle-{c.id}",
                        classes=f"card-btn {toggle_class}",
                    )
                    yield Button(
                        "👁 View",
                        id=f"btn-view-{c.id}",
                        classes="card-btn btn-view",
                    )
                    yield Button(
                        "✕ Delete",
                        id=f"btn-delete-{c.id}",
                        classes="card-btn btn-delete",
                    )

    # ---------- Handlers ----------

    @on(Button.Pressed)
    def _on_button(self, event: Button.Pressed) -> None:
        """Dispatch button presses to typed messages."""
        btn_id = event.button.id or ""
        if btn_id.startswith("btn-toggle-"):
            self.post_message(self.Toggle(self.canary.id))
        elif btn_id.startswith("btn-view-"):
            self.post_message(self.View(self.canary.id))
        elif btn_id.startswith("btn-delete-"):
            self.post_message(self.Delete(self.canary.id))