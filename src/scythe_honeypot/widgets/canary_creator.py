"""Canary creator form - Scythe Honeypot."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Input, RadioButton, RadioSet, Static

from scythe_honeypot.core.canary import CanaryDetectionOptions, CanaryType


# Affichage : (label, CanaryType)
CANARY_TYPE_CHOICES = [
    ("Crypto Wallet (.dat)",    CanaryType.WALLET),
    ("SSH Private Key (.pem)",  CanaryType.SSH_KEY),
    ("Password File (.txt)",    CanaryType.PASSWORD),
    ("Database Dump (.sql)",    CanaryType.DATABASE),
    ("Confidential PDF (.pdf)", CanaryType.PDF),
    ("Source Archive (.zip)",   CanaryType.ZIP),
]


class CanaryCreator(Widget):
    """Form to create a new canary file."""

    class Deploy(Message):
        """Posted when user clicks DEPLOY successfully."""
        def __init__(
            self,
            name: str,
            canary_type: CanaryType,
            path: str,
            detection: CanaryDetectionOptions,
        ):
            super().__init__()
            self.name = name
            self.canary_type = canary_type
            self.path = path
            self.detection = detection

    def compose(self) -> ComposeResult:
        yield Static("Create New Canary", classes="panel-title")

        with Vertical(classes="creator-form"):
            with Horizontal(classes="form-row"):
                yield Static("Name", classes="form-label")
                yield Input(
                    placeholder="wallet_backup_2026",
                    id="input-name",
                )

            with Horizontal(classes="form-row"):
                yield Static("Type", classes="form-label")
                with RadioSet(id="input-type"):
                    for i, (label, _) in enumerate(CANARY_TYPE_CHOICES):
                        yield RadioButton(label, value=(i == 0))

            with Horizontal(classes="form-row"):
                yield Static("Path", classes="form-label")
                yield Input(
                    placeholder=r"C:\Users\Admin\Documents",
                    id="input-path",
                )

            with Horizontal(classes="form-row"):
                yield Static("Detect", classes="form-label")
                with Horizontal(classes="form-checkboxes"):
                    yield Checkbox("Read",         value=True,  id="opt-read")
                    yield Checkbox("Open",         value=True,  id="opt-open")
                    yield Checkbox("Copy",         value=False, id="opt-copy")
                    yield Checkbox("Modify",       value=True,  id="opt-modify")
                    yield Checkbox("Capture proc", value=True,  id="opt-capture")

            with Horizontal(classes="form-row"):
                yield Static(" ", classes="form-label")
                yield Button(
                    "▲ DEPLOY CANARY",
                    id="btn-deploy",
                    variant="success",
                )

    @on(Button.Pressed, "#btn-deploy")
    def on_deploy_pressed(self, event: Button.Pressed) -> None:
        """Validate and emit a Deploy message."""
        name = self.query_one("#input-name", Input).value.strip()
        path = self.query_one("#input-path", Input).value.strip()

        if not name:
            self.notify("Name is required", severity="error")
            return
        if not path:
            self.notify("Path is required", severity="error")
            return

        # Type sélectionné
        radio_set = self.query_one("#input-type", RadioSet)
        type_idx = radio_set.pressed_index
        if type_idx < 0:
            self.notify("Select a type", severity="error")
            return
        canary_type = CANARY_TYPE_CHOICES[type_idx][1]

        # Options de détection
        detection = CanaryDetectionOptions(
            on_read=self.query_one("#opt-read", Checkbox).value,
            on_open=self.query_one("#opt-open", Checkbox).value,
            on_copy=self.query_one("#opt-copy", Checkbox).value,
            on_modify=self.query_one("#opt-modify", Checkbox).value,
            capture_process=self.query_one("#opt-capture", Checkbox).value,
        )

        # On poste un message - l'App s'occupera de la création réelle
        self.post_message(self.Deploy(name, canary_type, path, detection))

    def clear_form(self) -> None:
        """Reset all inputs after successful deploy."""
        self.query_one("#input-name", Input).value = ""
        # On garde le path et le type pour faciliter les déploiements multiples