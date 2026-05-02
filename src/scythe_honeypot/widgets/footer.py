"""Bottom footer with keyboard shortcuts - Scythe Honeypot."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static


class AppFooter(Widget):
    """Footer showing keyboard shortcuts (Bagels-style)."""

    SHORTCUTS = [
        ("a", "Add"),
        ("d", "Delete"),
        ("e", "Edit"),
        ("v", "View"),
        ("f", "Filter"),
        ("^q", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            for key, desc in self.SHORTCUTS:
                yield Static(f" {key} ", classes="key")
                yield Static(desc, classes="desc")
            yield Static("", classes="footer-spacer")
            yield Static("● Connected", classes="footer-status")