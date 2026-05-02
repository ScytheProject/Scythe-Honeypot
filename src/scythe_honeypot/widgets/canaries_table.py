"""Active canaries table - Scythe Honeypot."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Static

from scythe_honeypot.core.canary import Canary, CanaryStatus


# Symboles pour le statut
STATUS_ICONS = {
    CanaryStatus.ARMED:     "● ARMED",
    CanaryStatus.TRIGGERED: "▲ TRIGGERED",
    CanaryStatus.DISARMED:  "○ DISARMED",
    CanaryStatus.ERROR:     "✗ ERROR",
}


class CanariesTable(Widget):
    """Table showing all active canaries with their status."""

    def compose(self) -> ComposeResult:
        yield Static("Active Canaries", classes="panel-title")
        yield DataTable(id="canaries-dt", cursor_type="row", zebra_stripes=False)

    def on_mount(self) -> None:
        table = self.query_one("#canaries-dt", DataTable)
        table.add_columns("ID", "Name", "Type", "Status", "Path")

    def refresh_data(self, canaries: list[Canary]) -> None:
        """Replace all rows with the given canaries."""
        table = self.query_one("#canaries-dt", DataTable)
        table.clear()
        if not canaries:
            table.add_row("—", "No canaries deployed yet", "", "", "")
            return

        for c in canaries:
            table.add_row(
                f"{c.id:04d}",
                c.name,
                c.type.extension,
                STATUS_ICONS.get(c.status, c.status.value),
                c.short_path,
            )