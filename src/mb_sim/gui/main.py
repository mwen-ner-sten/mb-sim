"""Main entry point for launching the GUI application."""

from __future__ import annotations

import sys

from mb_sim.gui.app import run_gui


def main() -> int:
    """Start the GUI simulator."""
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())