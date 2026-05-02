"""Top navigation header - Scythe Honeypot."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class AppHeader(Widget):
    """Custom header with navigation tabs and status indicator."""

    active_view = reactive("home")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("↪ Scythe", classes="header-logo")
            yield Static("0.1.0", classes="header-version")
            yield Static("Home", id="nav-home", classes="header-nav-active")
            yield Static("Generator", id="nav-generator", classes="header-nav-inactive")
            yield Static("Settings", id="nav-settings", classes="header-nav-inactive")
            yield Static("", classes="header-spacer")
            yield Static("● Active", classes="header-status")