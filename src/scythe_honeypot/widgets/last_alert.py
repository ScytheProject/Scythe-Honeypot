"""Last alert panel - Scythe Honeypot."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static

from scythe_honeypot.core.event import TriggerEvent


class LastAlertPanel(Widget):
    """Compact panel showing the last triggered alert."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Last Alert",  classes="panel-title")
            yield Static("None yet",    id="alert-name",    classes="alert-name")
            yield Static("",            id="alert-event",   classes="alert-event")
            yield Static("",            id="alert-process", classes="alert-process")
            yield Static("",            id="alert-time",    classes="alert-time")

    def update_alert(self, event: Optional[TriggerEvent]) -> None:
        """Refresh display with the most recent event."""
        if event is None:
            self.query_one("#alert-name",    Static).update("None yet")
            self.query_one("#alert-event",   Static).update("")
            self.query_one("#alert-process", Static).update("")
            self.query_one("#alert-time",    Static).update("Waiting for triggers...")
            return

        self.query_one("#alert-name",    Static).update(event.canary_name)
        self.query_one("#alert-event",   Static).update(event.event_label)
        self.query_one("#alert-process", Static).update(event.process_name or "Unknown process")
        self.query_one("#alert-time",    Static).update(event.timestamp.strftime("%H:%M:%S"))