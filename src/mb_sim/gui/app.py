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

    # Create simulation runtime
    from mb_sim.simulator.runtime import SimulationRuntime

    runtime = SimulationRuntime()

    # Create some initial devices if requested
    if initial_device_count > 0:
        from mb_sim.models.device import DeviceConfig
        from mb_sim.models.register_map import RegisterDefinition

        for i in range(initial_device_count):
            device_config = DeviceConfig(
                device_id=i + 1,
                name=f"Device {i + 1}",
                description=f"Initial device {i + 1}"
            )

            # Add some initial registers
            initial_registers = [
                RegisterDefinition(address=40001, value=100 + i * 10),
                RegisterDefinition(address=40002, value=200 + i * 10),
                RegisterDefinition(address=40003, value=300 + i * 10),
            ]

            class DeviceDescriptor:
                def __init__(self, device_id, name, registers):
                    self.device_id = device_id
                    self.name = name
                    self.registers = registers

            descriptor = DeviceDescriptor(i + 1, f"Device {i + 1}", initial_registers)
            device = runtime.add_device(descriptor)
            device.config = device_config

    window = MainWindow(simulation_runtime=runtime)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_gui())

