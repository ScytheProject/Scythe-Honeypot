"""Quick stats panel - Scythe Honeypot."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class StatsPanel(Widget):
    """Compact stats panel showing canary counters."""

    # init=False : on ne déclenche pas les watchers à la création
    # (ils ne se déclencheront qu'aux changements ultérieurs)
    armed = reactive(0, init=False)
    triggered = reactive(0, init=False)
    total = reactive(0, init=False)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Quick Stats",         classes="panel-title")
            yield Static(self._fmt_armed(),     id="stat-armed",     classes="stat-line stat-armed")
            yield Static(self._fmt_triggered(), id="stat-triggered", classes="stat-line stat-triggered")
            yield Static(self._fmt_total(),     id="stat-total",     classes="stat-line stat-total")

    def _fmt_armed(self) -> str:
        return f"● Armed     {self.armed:>3}"

    def _fmt_triggered(self) -> str:
        return f"▲ Triggered {self.triggered:>3}"

    def _fmt_total(self) -> str:
        return f"↻ Total     {self.total:>3}"

    def watch_armed(self, value: int) -> None:
        # is_mounted = sécurité au cas où le watcher est appelé avant le mount
        if self.is_mounted:
            self.query_one("#stat-armed", Static).update(self._fmt_armed())

    def watch_triggered(self, value: int) -> None:
        if self.is_mounted:
            self.query_one("#stat-triggered", Static).update(self._fmt_triggered())

    def watch_total(self, value: int) -> None:
        if self.is_mounted:
            self.query_one("#stat-total", Static).update(self._fmt_total())