"""Home dashboard view - Scythe Honeypot."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical

from scythe_honeypot.widgets.canaries_list import CanariesList
from scythe_honeypot.widgets.canary_creator import CanaryCreator
from scythe_honeypot.widgets.events_table import EventsTable
from scythe_honeypot.widgets.last_alert import LastAlertPanel
from scythe_honeypot.widgets.stats_panel import StatsPanel


class HomeView(Container):
    """Main dashboard view."""

    def compose(self) -> ComposeResult:
        # Première ligne : stats + canaries cards
        with Horizontal(classes="row"):
            with Vertical(classes="left-col"):
                yield StatsPanel()
            with Vertical(classes="right-col"):
                yield CanariesList()

        # Deuxième ligne : last alert + events
        with Horizontal(classes="row"):
            with Vertical(classes="left-col"):
                yield LastAlertPanel()
            with Vertical(classes="right-col"):
                yield EventsTable()

        # Troisième ligne : créateur de canary
        yield CanaryCreator()