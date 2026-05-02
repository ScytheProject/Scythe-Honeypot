"""Recent events table - Scythe Honeypot."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Static

from scythe_honeypot.core.event import TriggerEvent


class EventsTable(Widget):
    """Table showing recent canary trigger events."""

    def compose(self) -> ComposeResult:
        yield Static("Recent Events", classes="panel-title")
        yield DataTable(id="events-dt", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#events-dt", DataTable)
        table.add_columns("Time", "Canary", "Event", "Process", "PID")

    def refresh_data(self, events: list[TriggerEvent]) -> None:
        """Replace all rows with the given events."""
        table = self.query_one("#events-dt", DataTable)
        table.clear()
        if not events:
            table.add_row("—", "No events yet", "", "", "")
            return

        for e in events:
            table.add_row(
                e.time_str,
                e.canary_name,
                e.event_label,
                e.process_name or "—",
                str(e.process_pid) if e.process_pid else "—",
            )