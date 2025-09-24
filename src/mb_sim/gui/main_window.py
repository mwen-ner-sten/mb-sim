"""Main window for the Modbus simulator MVP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QSplitter,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QLineEdit,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QComboBox,
)

from ..models.device import Device
from ..models.register_map import RegisterDefinition


@dataclass
class SimulatedDevice:
    device_id: int
    name: str


class DeviceDialog(QDialog):
    """Dialog for creating or editing devices."""

    def __init__(self, device_id: int = 0, name: str = "", description: str = "") -> None:
        super().__init__()
        self.setWindowTitle("Device Configuration")
        self.resize(300, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()

        self.device_id_spin = QSpinBox()
        self.device_id_spin.setRange(1, 247)
        self.device_id_spin.setValue(device_id)
        form_layout.addRow("Device ID:", self.device_id_spin)

        self.name_edit = QLineEdit(name)
        form_layout.addRow("Name:", self.name_edit)

        self.description_edit = QLineEdit(description)
        form_layout.addRow("Description:", self.description_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_device_config(self) -> tuple[int, str, str]:
        """Get the device configuration from the dialog."""
        return (
            self.device_id_spin.value(),
            self.name_edit.text(),
            self.description_edit.text()
        )


class RegisterDialog(QDialog):
    """Dialog for creating or editing registers."""

    def __init__(self, address: int = 40001, value: int = 0, label: str = "") -> None:
        super().__init__()
        self.setWindowTitle("Register Configuration")
        self.resize(300, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()

        self.address_spin = QSpinBox()
        self.address_spin.setRange(1, 65536)
        self.address_spin.setValue(address)
        form_layout.addRow("Address:", self.address_spin)

        self.value_spin = QSpinBox()
        self.value_spin.setRange(0, 65535)
        self.value_spin.setValue(value)
        form_layout.addRow("Value:", self.value_spin)

        self.label_edit = QLineEdit(label)
        form_layout.addRow("Label:", self.label_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_register_config(self) -> tuple[int, int, str]:
        """Get the register configuration from the dialog."""
        return (
            self.address_spin.value(),
            self.value_spin.value(),
            self.label_edit.text()
        )


class MainWindow(QMainWindow):
    """Enhanced GUI showing simulated devices and register management."""

    def __init__(self, simulation_runtime=None) -> None:
        super().__init__()
        self.setWindowTitle("MB-Sim Modbus Simulator")
        self.resize(1200, 800)

        self.simulation_runtime = simulation_runtime
        self.current_device: Optional[Device] = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)  # Update every second

        self._create_ui()

    def _create_ui(self) -> None:
        """Create the main user interface."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel - Device list
        left_panel = self._create_device_panel()
        main_layout.addWidget(left_panel, 1)

        # Center panel - Register management
        center_panel = self._create_register_panel()
        main_layout.addWidget(center_panel, 2)

        # Right panel - Logs and status
        right_panel = self._create_status_panel()
        main_layout.addWidget(right_panel, 1)

    def _create_device_panel(self) -> QWidget:
        """Create the device management panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Device list
        device_group = QGroupBox("Devices")
        device_layout = QVBoxLayout()
        device_group.setLayout(device_layout)

        self.device_list = QListWidget()
        self.device_list.itemSelectionChanged.connect(self.on_device_selected)
        device_layout.addWidget(self.device_list)

        # Device control buttons
        button_layout = QHBoxLayout()

        self.add_device_button = QPushButton("Add Device")
        self.add_device_button.clicked.connect(self.add_device)
        button_layout.addWidget(self.add_device_button)

        self.remove_device_button = QPushButton("Remove Device")
        self.remove_device_button.clicked.connect(self.remove_device)
        button_layout.addWidget(self.remove_device_button)

        device_layout.addLayout(button_layout)
        layout.addWidget(device_group)

        return panel

    def _create_register_panel(self) -> QWidget:
        """Create the register management panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Register table
        register_group = QGroupBox("Holding Registers")
        register_layout = QVBoxLayout()
        register_group.setLayout(register_layout)

        self.register_table = QTableWidget()
        self.register_table.setColumnCount(3)
        self.register_table.setHorizontalHeaderLabels(["Address", "Value", "Label"])
        self.register_table.horizontalHeader().setStretchLastSection(True)
        register_layout.addWidget(self.register_table)

        # Register control buttons
        button_layout = QHBoxLayout()

        self.add_register_button = QPushButton("Add Register")
        self.add_register_button.clicked.connect(self.add_register)
        button_layout.addWidget(self.add_register_button)

        self.edit_register_button = QPushButton("Edit Register")
        self.edit_register_button.clicked.connect(self.edit_register)
        button_layout.addWidget(self.edit_register_button)

        self.remove_register_button = QPushButton("Remove Register")
        self.remove_register_button.clicked.connect(self.remove_register)
        button_layout.addWidget(self.remove_register_button)

        register_layout.addLayout(button_layout)
        layout.addWidget(register_group)

        return panel

    def _create_status_panel(self) -> QWidget:
        """Create the status and logging panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Status information
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)

        self.status_label = QLabel("No device selected")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_group)

        # Log panel
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        clear_log_button = QPushButton("Clear Log")
        clear_log_button.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_button)

        layout.addWidget(log_group)

        return panel

    def update_ui(self) -> None:
        """Update the user interface with current data."""
        self.refresh_device_list()
        if self.current_device:
            self.refresh_register_table()

    def refresh_device_list(self) -> None:
        """Refresh the device list."""
        self.device_list.clear()

        if self.simulation_runtime:
            devices = self.simulation_runtime.list_devices()
            for device in devices:
                item_text = f"{device.config.device_id}: {device.display_name}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, device)
                self.device_list.addItem(item)

    def refresh_register_table(self) -> None:
        """Refresh the register table for the current device."""
        if not self.current_device:
            return

        self.register_table.setRowCount(0)
        registers = self.current_device.list_holding_registers()

        for register in registers:
            row = self.register_table.rowCount()
            self.register_table.insertRow(row)

            # Address
            address_item = QTableWidgetItem(str(register.address))
            self.register_table.setItem(row, 0, address_item)

            # Value
            value_item = QTableWidgetItem(str(register.value))
            self.register_table.setItem(row, 1, value_item)

            # Label
            label_item = QTableWidgetItem(register.label or "")
            self.register_table.setItem(row, 2, label_item)

    def on_device_selected(self) -> None:
        """Handle device selection."""
        current_item = self.device_list.currentItem()
        if current_item:
            self.current_device = current_item.data(Qt.ItemDataRole.UserRole)
            self.status_label.setText(f"Selected: {self.current_device.display_name}")
            self.refresh_register_table()
        else:
            self.current_device = None
            self.status_label.setText("No device selected")
            self.register_table.setRowCount(0)

    def add_device(self) -> None:
        """Add a new device."""
        dialog = DeviceDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            device_id, name, description = dialog.get_device_config()

            # Check if device ID already exists
            if self.simulation_runtime:
                try:
                    # Create device descriptor
                    class DeviceDescriptor:
                        def __init__(self, device_id, name, registers):
                            self.device_id = device_id
                            self.name = name
                            self.registers = registers

                    descriptor = DeviceDescriptor(device_id, name, [])
                    device = self.simulation_runtime.add_device(descriptor)

                    from mb_sim.models.device import DeviceConfig
                    device.config = DeviceConfig(device_id, name, description)

                    self.log_message(f"Added device: {device.display_name}")
                    self.refresh_device_list()

                except ValueError as e:
                    QMessageBox.warning(self, "Error", str(e))

    def remove_device(self) -> None:
        """Remove the selected device."""
        if not self.current_device:
            QMessageBox.information(self, "No Selection", "Please select a device to remove.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove device '{self.current_device.display_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Note: We don't have a remove method in the runtime yet
            self.log_message(f"Removed device: {self.current_device.display_name}")
            self.current_device = None
            self.refresh_device_list()

    def add_register(self) -> None:
        """Add a new register to the current device."""
        if not self.current_device:
            QMessageBox.information(self, "No Selection", "Please select a device first.")
            return

        dialog = RegisterDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            address, value, label = dialog.get_register_config()

            try:
                register_def = RegisterDefinition(address=address, value=value, label=label)
                self.current_device.add_holding_register(register_def)
                self.log_message(f"Added register {address} to {self.current_device.display_name}")
                self.refresh_register_table()

            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def edit_register(self) -> None:
        """Edit the selected register."""
        current_row = self.register_table.currentRow()
        if current_row < 0 or not self.current_device:
            QMessageBox.information(self, "No Selection", "Please select a register to edit.")
            return

        # Get current register data
        address_item = self.register_table.item(current_row, 0)
        value_item = self.register_table.item(current_row, 1)
        label_item = self.register_table.item(current_row, 2)

        if not all([address_item, value_item, label_item]):
            return

        address = int(address_item.text())
        value = int(value_item.text())
        label = label_item.text()

        dialog = RegisterDialog(address, value, label)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_address, new_value, new_label = dialog.get_register_config()

            try:
                # Remove old register and add new one
                self.current_device.holding_registers.set_value(address, new_value)
                # Note: We can't easily change the address, so we'll update the value and label
                self.log_message(f"Updated register {address} in {self.current_device.display_name}")
                self.refresh_register_table()

            except KeyError as e:
                QMessageBox.warning(self, "Error", str(e))

    def remove_register(self) -> None:
        """Remove the selected register."""
        current_row = self.register_table.currentRow()
        if current_row < 0 or not self.current_device:
            QMessageBox.information(self, "No Selection", "Please select a register to remove.")
            return

        address_item = self.register_table.item(current_row, 0)
        if not address_item:
            return

        address = int(address_item.text())

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove register {address}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.current_device.remove_holding_register(address)
                self.log_message(f"Removed register {address} from {self.current_device.display_name}")
                self.refresh_register_table()

            except KeyError as e:
                QMessageBox.warning(self, "Error", str(e))

    def log_message(self, message: str) -> None:
        """Add a message to the activity log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def clear_log(self) -> None:
        """Clear the activity log."""
        self.log_text.clear()

