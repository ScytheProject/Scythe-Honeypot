"""Scrollable list of canary cards - Scythe Honeypot."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from scythe_honeypot.core.canary import Canary
from scythe_honeypot.widgets.canary_card import CanaryCard


class CanariesList(Widget):
    """Holds all canary cards in a scrollable container."""

    def compose(self) -> ComposeResult:
        yield Static("Active Canaries", classes="panel-title")
        yield VerticalScroll(id="canaries-scroll")

    def refresh_data(self, canaries: list[Canary]) -> None:
        """Rebuild the list of cards from scratch."""
        scroll = self.query_one("#canaries-scroll", VerticalScroll)
        # Vire toutes les cards existantes
        scroll.remove_children()

        if not canaries:
            scroll.mount(Static("◌  No canaries deployed yet", classes="empty-state"))
            return

        # Ajoute une card par canary
        for canary in canaries:
            scroll.mount(CanaryCard(canary))