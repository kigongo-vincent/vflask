"""Watch for generated module changes and regenerate docs."""

from __future__ import annotations

import time
from pathlib import Path

from rich.console import Console
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

console = Console()


class ModuleHandler(FileSystemEventHandler):
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.debounce: dict[str, float] = {}

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        
        path = Path(event.src_path) # type: ignore
        if path.name != "handlers.py" or "__pycache__" in path.parts:
            return

        now = time.time()
        key = str(path)
        if key in self.debounce and now - self.debounce[key] < 0.5:
            return
        self.debounce[key] = now

        console.print(f"  [yellow]📝[/] {path.relative_to(self.project_root)}")
        self._regenerate_docs(path.parent)

    def _regenerate_docs(self, module_dir: Path) -> None:
        try:
            from vflask.core.docgen import DocGenerator

            docgen = DocGenerator(self.project_root)
            docgen.generate_for_module(module_dir)
            console.print(f"  [green]📚[/] {module_dir.name}/docs.md regenerated")
        except Exception as exc:  # pragma: no cover
            console.print(f"  [red]✗[/] Doc error: {exc}")


def start_watcher(project_root: Path) -> None:
    observer = Observer()
    handler = ModuleHandler(Path(project_root).resolve())
    modules_path = Path(project_root).resolve() / "app" / "modules"
    if not modules_path.exists():
        console.print(f"[yellow]No modules directory at {modules_path}; creating it.[/]")
        modules_path.mkdir(parents=True, exist_ok=True)

    observer.schedule(handler, str(modules_path), recursive=True)
    observer.start()
    console.print(f"[bold green]👁️  Watching {modules_path}[/]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()


__all__ = ["ModuleHandler", "start_watcher"]
