"""File system monitor for canaries - Scythe Honeypot."""

import threading
from pathlib import Path
from typing import Callable, Optional

import psutil
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from scythe_honeypot.core.canary import Canary, CanaryStatus
from scythe_honeypot.core.event import EventType, TriggerEvent


class CanaryEventHandler(FileSystemEventHandler):
    """Handles filesystem events for the canary directory."""

    def __init__(
        self,
        watched_files: dict[str, Canary],
        on_trigger: Callable[[TriggerEvent], None],
    ):
        super().__init__()
        self.watched_files = watched_files
        self.on_trigger = on_trigger

    def _process_for_file(self, filepath: str) -> tuple[Optional[str], Optional[int]]:
        """
        Try to identify which process is currently using this file.
        Best-effort: peut retourner (None, None) si aucun process ne tient le fichier.
        """
        target = Path(filepath).resolve()
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    for f in proc.open_files():
                        if Path(f.path).resolve() == target:
                            return proc.info["name"], proc.info["pid"]
                except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                    continue
        except Exception:
            pass
        return None, None

    def _handle(self, event_type: EventType, filepath: str) -> None:
        """Common dispatch for all event types."""
        # Normalise le path pour matcher la map
        try:
            resolved = str(Path(filepath).resolve())
        except OSError:
            return

        canary = self.watched_files.get(resolved)
        if canary is None:
            return  # Ce fichier n'est pas un canary qu'on surveille

        # Skip si le canary est désarmé
        if canary.status == CanaryStatus.DISARMED:
            return

        # Vérifie les options de détection du canary
        detection = canary.detection
        relevant = (
            (event_type == EventType.READ and detection.on_read)
            or (event_type == EventType.MODIFIED and detection.on_modify)
            or (event_type == EventType.OPENED and detection.on_open)
            or (event_type in (EventType.DELETED, EventType.MOVED))
        )
        if not relevant:
            return

        # Identifie le process si l'option est activée
        proc_name, proc_pid = (None, None)
        if detection.capture_process:
            proc_name, proc_pid = self._process_for_file(filepath)

        # Construit l'event et notifie le callback
        trigger = TriggerEvent(
            canary_id=canary.id,
            canary_name=canary.name,
            event_type=event_type,
            process_name=proc_name,
            process_pid=proc_pid,
        )
        self.on_trigger(trigger)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle(EventType.MODIFIED, event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle(EventType.DELETED, event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle(EventType.MOVED, event.src_path)


class CanaryMonitor:
    """
    Watches all canary files and triggers callbacks on filesystem events.
    Thread-safe.
    """

    def __init__(self, on_trigger: Callable[[TriggerEvent], None]):
        self.on_trigger = on_trigger
        self.watched_files: dict[str, Canary] = {}
        self.watched_dirs: dict[str, int] = {}
        self.observer: Optional[Observer] = None
        self.handler: Optional[CanaryEventHandler] = None
        self._lock = threading.Lock()

    def start(self, canaries: list[Canary]) -> None:
        """Start watching all the given canaries."""
        if self.observer is not None:
            return

        self.handler = CanaryEventHandler(self.watched_files, self.on_trigger)
        self.observer = Observer()

        for canary in canaries:
            self._add_unsafe(canary)

        self.observer.start()

    def stop(self) -> None:
        """Stop the observer cleanly."""
        if self.observer is None:
            return
        self.observer.stop()
        self.observer.join(timeout=2.0)
        self.observer = None
        self.handler = None
        self.watched_files.clear()
        self.watched_dirs.clear()

    def add_canary(self, canary: Canary) -> None:
        """Add a canary to watch (thread-safe)."""
        with self._lock:
            self._add_unsafe(canary)

    def update_canary(self, canary: Canary) -> None:
        """Update a canary in the watched_files map (after status change)."""
        with self._lock:
            filepath = str(canary.filepath.resolve())
            if filepath in self.watched_files:
                self.watched_files[filepath] = canary

    def _add_unsafe(self, canary: Canary) -> None:
        """Internal add without lock."""
        filepath = str(canary.filepath.resolve())
        directory = str(canary.filepath.parent.resolve())

        self.watched_files[filepath] = canary

        if directory in self.watched_dirs:
            self.watched_dirs[directory] += 1
        else:
            self.watched_dirs[directory] = 1
            if self.observer:
                self.observer.schedule(self.handler, directory, recursive=False)