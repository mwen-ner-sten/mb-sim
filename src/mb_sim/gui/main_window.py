"""Main window for the Modbus simulator MVP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass
class SimulatedDevice:
    device_id: int
    name: str


class MainWindow(QMainWindow):
    """Simple GUI showing simulated devices and register placeholders."""

    def __init__(self, initial_device_count: int = 1) -> None:
        super().__init__()
        self.setWindowTitle("MB-Sim Modbus Simulator")
        self.resize(960, 600)

        self.devices: List[SimulatedDevice] = self._create_initial_devices(initial_device_count)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.device_list = QListWidget()
        self.refresh_device_list()

        layout.addWidget(self.device_list, 1)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        self.status_label = QLabel("Select a device to view details")
        right_layout.addWidget(self.status_label)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_device_list)
        right_layout.addWidget(self.refresh_button)

        layout.addWidget(right_panel, 2)

    def _create_initial_devices(self, count: int) -> List[SimulatedDevice]:
        return [SimulatedDevice(device_id=i + 1, name=f"Device {i + 1}") for i in range(count)]

    def refresh_device_list(self) -> None:
        self.device_list.clear()
        for device in self.devices:
            item = QListWidgetItem(f"{device.device_id}: {device.name}")
            self.device_list.addItem(item)

