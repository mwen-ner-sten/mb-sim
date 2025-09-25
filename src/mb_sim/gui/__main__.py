"""Entry point for running the GUI module directly."""

from __future__ import annotations

from .app import run_gui


def main() -> None:
    """Launch the GUI application."""
    raise SystemExit(run_gui())


if __name__ == "__main__":
    main()
