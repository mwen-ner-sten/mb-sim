"""Qt application bootstrap for the Modbus simulator MVP."""

from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication

from mb_sim.simulator.runtime import DeviceDescriptor, SimulationRuntime
from .main_window import MainWindow


def create_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName("mb-sim")
    return app


def run_gui(initial_device_count: int = 1) -> int:
    app = create_app()

    runtime = _build_default_runtime(initial_device_count)

    window = MainWindow(simulation_runtime=runtime)
    window.show()
    return app.exec()


def _build_default_runtime(initial_device_count: int) -> SimulationRuntime:
    """Create a simulation runtime pre-populated with sample devices."""

    runtime = SimulationRuntime()

    if initial_device_count <= 0:
        return runtime

    from mb_sim.models.register_map import RegisterDefinition

    for index in range(initial_device_count):
        device_id = index + 1
        registers = [
            RegisterDefinition(address=40001, value=100 + index * 10),
            RegisterDefinition(address=40002, value=200 + index * 10),
            RegisterDefinition(address=40003, value=300 + index * 10),
        ]

        descriptor = DeviceDescriptor(
            device_id=device_id,
            name=f"Device {device_id}",
            registers=registers,
        )
        runtime.add_device(descriptor)

    return runtime


if __name__ == "__main__":
    raise SystemExit(run_gui())

