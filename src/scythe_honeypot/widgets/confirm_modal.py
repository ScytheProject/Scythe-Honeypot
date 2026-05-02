"""Confirmation modal - Scythe Honeypot."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmModal(ModalScreen[bool]):
    """Generic yes/no confirmation modal. Returns True if confirmed."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        danger: bool = False,
    ):
        super().__init__()
        self.modal_title = title
        self.message = message
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.danger = danger

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            with Vertical(id="modal-box"):
                yield Static(self.modal_title, id="modal-title")
                yield Static(self.message, id="modal-message")
                with Horizontal(id="modal-actions"):
                    yield Button(self.cancel_label, id="btn-cancel", variant="default")
                    yield Button(
                        self.confirm_label,
                        id="btn-confirm",
                        variant="error" if self.danger else "primary",
                    )

    @on(Button.Pressed, "#btn-confirm")
    def _on_confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#btn-cancel")
    def _on_cancel(self) -> None:
        self.dismiss(False)

    def on_key(self, event) -> None:
        # Echap = cancel
        if event.key == "escape":
            self.dismiss(False)