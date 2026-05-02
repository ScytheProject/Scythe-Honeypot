"""Canary details modal - Scythe Honeypot."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from scythe_honeypot.core.canary import Canary


class CanaryDetailsModal(ModalScreen[None]):
    """Shows detailed info about a canary."""

    def __init__(self, canary: Canary):
        super().__init__()
        self.canary = canary

    def compose(self) -> ComposeResult:
        c = self.canary

        # Détection options en string
        opts = []
        if c.detection.on_read:    opts.append("Read")
        if c.detection.on_open:    opts.append("Open")
        if c.detection.on_copy:    opts.append("Copy")
        if c.detection.on_modify:  opts.append("Modify")
        if c.detection.capture_process: opts.append("Capture process")
        opts_str = ", ".join(opts) if opts else "None"

        # Format dates
        created = c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        last_trig = (
            c.last_triggered_at.strftime("%Y-%m-%d %H:%M:%S")
            if c.last_triggered_at else "Never"
        )

        with Container(id="modal-container"):
            with Vertical(id="modal-box-large"):
                yield Static(f"◆ Canary #{c.id:04d}", id="modal-title")
                yield Static(c.name, classes="details-name")

                yield Static("─" * 50, classes="details-sep")

                yield Static(self._row("Type",       c.type.display_name))
                yield Static(self._row("Status",     c.status.value.upper()))
                yield Static(self._row("File",       str(c.filepath)))
                yield Static(self._row("Detection",  opts_str))
                yield Static(self._row("Created",    created))
                yield Static(self._row("Last trig.", last_trig))
                yield Static(self._row("Triggers",   str(c.trigger_count)))

                yield Static("─" * 50, classes="details-sep")

                yield Button("Close", id="btn-close", variant="primary")

    @staticmethod
    def _row(label: str, value: str) -> str:
        return f"{label:<14} {value}"

    @on(Button.Pressed, "#btn-close")
    def _on_close(self) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)