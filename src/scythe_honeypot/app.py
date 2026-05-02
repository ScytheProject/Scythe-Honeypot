"""Main Textual application - Scythe Honeypot."""

from textual.app import App, ComposeResult

from scythe_honeypot.core.canary_service import CanaryService
from scythe_honeypot.core.event import TriggerEvent
from scythe_honeypot.core.monitor import CanaryMonitor
from scythe_honeypot.screens.home import HomeView
from scythe_honeypot.widgets.canaries_list import CanariesList
from scythe_honeypot.widgets.canary_card import CanaryCard
from scythe_honeypot.widgets.canary_creator import CanaryCreator
from scythe_honeypot.widgets.canary_details_modal import CanaryDetailsModal
from scythe_honeypot.widgets.confirm_modal import ConfirmModal
from scythe_honeypot.widgets.events_table import EventsTable
from scythe_honeypot.widgets.footer import AppFooter
from scythe_honeypot.widgets.header import AppHeader
from scythe_honeypot.widgets.last_alert import LastAlertPanel
from scythe_honeypot.widgets.stats_panel import StatsPanel


class ScytheHoneypotApp(App):
    """Scythe Honeypot - Personal intrusion detection TUI."""

    CSS_PATH = "styles.tcss"
    TITLE = "Scythe Honeypot"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.canary_service = CanaryService()
        self.monitor = CanaryMonitor(on_trigger=self._on_trigger_from_thread)

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield HomeView(id="home-view")
        yield AppFooter()

    def on_mount(self) -> None:
        self._refresh_dashboard()
        canaries = self.canary_service.list_canaries()
        self.monitor.start(canaries)

    def on_unmount(self) -> None:
        self.monitor.stop()

    # ---------- Trigger from monitor thread ----------

    def _on_trigger_from_thread(self, event: TriggerEvent) -> None:
        self.call_from_thread(self._handle_trigger_on_ui, event)

    def _handle_trigger_on_ui(self, event: TriggerEvent) -> None:
        self.canary_service.record_trigger(event)
        proc_str = event.process_name or "unknown process"
        self.notify(
            f"{event.canary_name} → {event.event_label} by {proc_str}",
            severity="warning",
            title="⚠ CANARY TRIGGERED",
            timeout=8,
        )
        self._refresh_dashboard()

    # ---------- Card action handlers ----------

    def on_canary_card_toggle(self, event: CanaryCard.Toggle) -> None:
        """Pause / resume a canary."""
        from scythe_honeypot.core.canary import CanaryStatus

        canary = self.canary_service.get_canary(event.canary_id)
        if canary is None:
            return

        if canary.status in (CanaryStatus.ARMED, CanaryStatus.TRIGGERED):
            self.canary_service.disarm_canary(event.canary_id)
            self.notify(f"'{canary.name}' disarmed", severity="information")
        else:
            self.canary_service.rearm_canary(event.canary_id)
            self.notify(f"'{canary.name}' rearmed", severity="information")

        # Synchronise le monitor avec le nouveau statut (pour les 2 cas)
        updated = self.canary_service.get_canary(event.canary_id)
        if updated:
            self.monitor.update_canary(updated)

        self._refresh_dashboard()

    def on_canary_card_view(self, event: CanaryCard.View) -> None:
        """Open the details modal."""
        canary = self.canary_service.get_canary(event.canary_id)
        if canary is None:
            return
        self.push_screen(CanaryDetailsModal(canary))

    def on_canary_card_delete(self, event: CanaryCard.Delete) -> None:
        """Confirm + delete a canary."""
        canary = self.canary_service.get_canary(event.canary_id)
        if canary is None:
            return

        def after_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            self.canary_service.delete_canary(event.canary_id, also_delete_file=True)
            self.notify(
                f"Canary '{canary.name}' deleted",
                severity="warning",
                title="✕ Deleted",
            )
            self._refresh_dashboard()

        self.push_screen(
            ConfirmModal(
                title="Delete canary?",
                message=(
                    f"This will permanently delete '{canary.name}{canary.type.extension}' "
                    f"and remove the file from disk.\n\nThis cannot be undone."
                ),
                confirm_label="✕ Delete",
                cancel_label="Cancel",
                danger=True,
            ),
            after_confirm,
        )

    # ---------- Deploy handler ----------

    def on_canary_creator_deploy(self, event: CanaryCreator.Deploy) -> None:
        try:
            canary = self.canary_service.deploy_canary(
                name=event.name,
                canary_type=event.canary_type,
                deploy_path=event.path,
                detection=event.detection,
            )
        except (ValueError, RuntimeError) as e:
            self.notify(str(e), severity="error", title="Deploy failed")
            return

        self.monitor.add_canary(canary)
        self.notify(
            f"'{canary.name}{canary.type.extension}' deployed at {canary.path}",
            severity="information",
            title="✓ Canary armed",
            timeout=5,
        )
        self.query_one(CanaryCreator).clear_form()
        self._refresh_dashboard()

    # ---------- Dashboard refresh ----------

    def _refresh_dashboard(self) -> None:
        canaries = self.canary_service.list_canaries()
        events = self.canary_service.get_recent_events(limit=10)
        last_event = self.canary_service.get_last_event()
        stats = self.canary_service.get_stats()

        self.query_one(CanariesList).refresh_data(canaries)
        self.query_one(EventsTable).refresh_data(events)
        self.query_one(LastAlertPanel).update_alert(last_event)

        stats_panel = self.query_one(StatsPanel)
        stats_panel.armed = stats["armed"]
        stats_panel.triggered = stats["triggered"]
        stats_panel.total = stats["total"]


def main() -> None:
    app = ScytheHoneypotApp()
    app.run()


if __name__ == "__main__":
    main()