"""Qt application bootstrap for the Modbus simulator MVP."""

from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow


def create_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName("mb-sim")
    return app


def run_gui(initial_device_count: int = 1) -> int:
    app = create_app()
    window = MainWindow(initial_device_count=initial_device_count)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_gui())

