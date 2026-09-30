"""Watch command entrypoint for vflask generated projects."""

from __future__ import annotations

from pathlib import Path

from vflask.core.watcher import start_watcher


def main() -> None:
    start_watcher(Path.cwd())


if __name__ == "__main__":
    main()
