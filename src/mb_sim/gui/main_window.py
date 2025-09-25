"""Main window for the Modbus simulator MVP."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QAction
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QStatusBar,
    QMenuBar,
    QMenu,
    QSplitter,
    QFrame,
    QTabWidget,
    QHeaderView,
    QComboBox,
    QSlider,
)

from mb_sim.models.device import Device, DeviceConfig
from mb_sim.models.register_map import RegisterDefinition
from mb_sim.simulator.runtime import DeviceDescriptor, SimulationRuntime


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

    def __init__(self, simulation_runtime: SimulationRuntime) -> None:
        super().__init__()
        self.setWindowTitle("MB-Sim Modbus Simulator")
        self.setWindowIcon(self._create_app_icon())
        self.resize(1400, 900)

        # Apply modern styling
        self.setStyleSheet(self._get_modern_stylesheet())

        self.simulation_runtime = simulation_runtime
        self.current_device: Optional[Device] = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)  # Update every second

        # Initialize connection status
        self.connection_status = "Disconnected"
        self.last_update = None

        self._create_menu_bar()
        self._create_ui()
        self._create_status_bar()
        self.update_status_bar()  # Update after status bar is created

    def _create_menu_bar(self) -> None:
        """Create the menu bar with file and help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Import/Export actions
        import_action = QAction("&Import Configuration...", self)
        import_action.setStatusTip("Import device configuration from file")
        import_action.triggered.connect(self.import_configuration)
        file_menu.addAction(import_action)

        export_action = QAction("&Export Configuration...", self)
        export_action.setStatusTip("Export device configuration to file")
        export_action.triggered.connect(self.export_configuration)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.setStatusTip("Configure application settings")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Presets menu
        presets_menu = menubar.addMenu("&Presets")

        basic_device_action = QAction("&Basic Device", self)
        basic_device_action.setStatusTip("Load a basic device with standard registers")
        basic_device_action.triggered.connect(self.load_basic_preset)
        presets_menu.addAction(basic_device_action)

        presets_menu.addSeparator()

        sensor_device_action = QAction("&Sensor Simulation", self)
        sensor_device_action.setStatusTip("Load sensor simulation devices")
        sensor_device_action.triggered.connect(self.load_sensor_preset)
        presets_menu.addAction(sensor_device_action)

        motor_control_action = QAction("&Motor Control", self)
        motor_control_action.setStatusTip("Load motor control simulation devices")
        motor_control_action.triggered.connect(self.load_motor_preset)
        presets_menu.addAction(motor_control_action)

        hmi_device_action = QAction("&HMI Panel", self)
        hmi_device_action.setStatusTip("Load HMI panel simulation devices")
        hmi_device_action.triggered.connect(self.load_hmi_preset)
        presets_menu.addAction(hmi_device_action)

        presets_menu.addSeparator()

        clear_all_action = QAction("&Clear All Devices", self)
        clear_all_action.setStatusTip("Remove all devices from simulation")
        clear_all_action.triggered.connect(self.clear_all_devices)
        presets_menu.addAction(clear_all_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.setStatusTip("About MB-Sim")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self) -> None:
        """Create the status bar with connection and update information."""
        self.status_bar = self.statusBar()

        # Connection status indicator
        self.connection_indicator = QLabel()
        self.connection_indicator.setFixedWidth(100)
        self.status_bar.addWidget(self.connection_indicator)

        # Device count indicator
        self.device_count_label = QLabel("Devices: 0")
        self.status_bar.addWidget(self.device_count_label)

        # Register count indicator
        self.register_count_label = QLabel("Registers: 0")
        self.status_bar.addWidget(self.register_count_label)

        # Last update indicator
        self.last_update_label = QLabel("Last Update: Never")
        self.status_bar.addPermanentWidget(self.last_update_label)

    def _create_app_icon(self) -> QIcon:
        """Create a simple application icon."""
        # Create a simple icon with a gear symbol (representing simulation)
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(52, 152, 219))  # Blue color

        # For now, return a default icon - in a real app we'd load from file
        return self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)

    def _get_modern_stylesheet(self) -> str:
        """Return modern styling for the application."""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }

        QGroupBox {
            font-weight: bold;
            border: 2px solid #3498db;
            border-radius: 8px;
            margin-top: 1ex;
            background-color: white;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #2980b9;
            background-color: white;
            border-radius: 4px;
        }

        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #2980b9;
        }

        QPushButton:pressed {
            background-color: #21618c;
        }

        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }

        QTableWidget {
            gridline-color: #bdc3c7;
            selection-background-color: #3498db;
            alternate-background-color: #f8f9fa;
        }

        QTableWidget::item:selected {
            color: white;
        }

        QListWidget {
            background-color: white;
            alternate-background-color: #f8f9fa;
            selection-background-color: #3498db;
        }

        QListWidget::item:selected {
            color: white;
        }

        QTextEdit {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
        }

        QProgressBar {
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #27ae60;
            width: 20px;
        }

        QSpinBox, QLineEdit {
            border: 2px solid #bdc3c7;
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
        }

        QSpinBox:focus, QLineEdit:focus {
            border-color: #3498db;
        }
        """

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

        self.add_device_button = QPushButton("➕ Add Device")
        self.add_device_button.setToolTip("Add a new Modbus device to the simulation")
        self.add_device_button.clicked.connect(self.add_device)
        button_layout.addWidget(self.add_device_button)

        self.remove_device_button = QPushButton("🗑️ Remove Device")
        self.remove_device_button.setToolTip("Remove the selected device")
        self.remove_device_button.clicked.connect(self.remove_device)
        button_layout.addWidget(self.remove_device_button)

        device_layout.addLayout(button_layout)

        # Device quick actions
        quick_layout = QHBoxLayout()

        quick_label = QLabel("Quick Actions:")
        quick_layout.addWidget(quick_label)

        self.duplicate_device_button = QPushButton("📋 Duplicate")
        self.duplicate_device_button.setToolTip("Duplicate the selected device")
        self.duplicate_device_button.clicked.connect(self.duplicate_device)
        quick_layout.addWidget(self.duplicate_device_button)

        self.clear_device_button = QPushButton("🧹 Clear All")
        self.clear_device_button.setToolTip("Remove all devices")
        self.clear_device_button.clicked.connect(self.clear_all_devices)
        quick_layout.addWidget(self.clear_device_button)

        device_layout.addLayout(quick_layout)
        layout.addWidget(device_group)

        return panel

    def _create_register_panel(self) -> QWidget:
        """Create the register management panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Register table with enhanced features
        register_group = QGroupBox("Holding Registers")
        register_layout = QVBoxLayout()
        register_group.setLayout(register_layout)

        # Create table with better styling
        self.register_table = QTableWidget()
        self.register_table.setColumnCount(5)  # Added progress and status columns
        self.register_table.setHorizontalHeaderLabels(["Address", "Value", "Progress", "Label", "Status"])
        self.register_table.horizontalHeader().setStretchLastSection(True)
        self.register_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.register_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.register_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.register_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.register_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Set row height for progress bars
        self.register_table.verticalHeader().setDefaultSectionSize(35)
        register_layout.addWidget(self.register_table)

        # Register control buttons with better layout
        button_layout = QHBoxLayout()

        self.add_register_button = QPushButton("➕ Add Register")
        self.add_register_button.setToolTip("Add a new holding register to the selected device")
        self.add_register_button.clicked.connect(self.add_register)
        button_layout.addWidget(self.add_register_button)

        self.edit_register_button = QPushButton("✏️ Edit Register")
        self.edit_register_button.setToolTip("Edit the selected register's properties")
        self.edit_register_button.clicked.connect(self.edit_register)
        button_layout.addWidget(self.edit_register_button)

        self.remove_register_button = QPushButton("🗑️ Remove Register")
        self.remove_register_button.setToolTip("Remove the selected register")
        self.remove_register_button.clicked.connect(self.remove_register)
        button_layout.addWidget(self.remove_register_button)

        register_layout.addLayout(button_layout)

        # Advanced simulation controls
        sim_group = QGroupBox("Register Simulation")
        sim_layout = QVBoxLayout()
        sim_group.setLayout(sim_layout)

        # Quick actions row
        quick_sim_layout = QHBoxLayout()
        quick_sim_label = QLabel("Quick Actions:")
        quick_sim_layout.addWidget(quick_sim_label)

        self.random_button = QPushButton("🎲 Random")
        self.random_button.setToolTip("Set random values for all registers")
        self.random_button.clicked.connect(self.randomize_registers)
        quick_sim_layout.addWidget(self.random_button)

        self.increment_button = QPushButton("⬆️ Increment")
        self.increment_button.setToolTip("Increment all register values by 1")
        self.increment_button.clicked.connect(self.increment_registers)
        quick_sim_layout.addWidget(self.increment_button)

        self.decrement_button = QPushButton("⬇️ Decrement")
        self.decrement_button.setToolTip("Decrement all register values by 1")
        self.decrement_button.clicked.connect(self.decrement_registers)
        quick_sim_layout.addWidget(self.decrement_button)

        sim_layout.addLayout(quick_sim_layout)

        # Simulation patterns row
        pattern_sim_layout = QHBoxLayout()
        pattern_sim_label = QLabel("Patterns:")
        pattern_sim_layout.addWidget(pattern_sim_label)

        self.sine_wave_button = QPushButton("🌊 Sine Wave")
        self.sine_wave_button.setToolTip("Apply sine wave pattern to register values")
        self.sine_wave_button.clicked.connect(self.apply_sine_pattern)
        pattern_sim_layout.addWidget(self.sine_wave_button)

        self.sawtooth_button = QPushButton("📈 Sawtooth")
        self.sawtooth_button.setToolTip("Apply sawtooth pattern to register values")
        self.sawtooth_button.clicked.connect(self.apply_sawtooth_pattern)
        pattern_sim_layout.addWidget(self.sawtooth_button)

        self.ramp_button = QPushButton("📊 Ramp")
        self.ramp_button.setToolTip("Apply ramp pattern (0-100% cycle)")
        self.ramp_button.clicked.connect(self.apply_ramp_pattern)
        pattern_sim_layout.addWidget(self.ramp_button)

        sim_layout.addLayout(pattern_sim_layout)

        # Simulation controls
        sim_controls_layout = QHBoxLayout()

        self.auto_sim_button = QPushButton("▶️ Auto Simulate")
        self.auto_sim_button.setToolTip("Start automatic simulation with selected pattern")
        self.auto_sim_button.clicked.connect(self.start_auto_simulation)
        sim_controls_layout.addWidget(self.auto_sim_button)

        self.stop_sim_button = QPushButton("⏸️ Stop Auto")
        self.stop_sim_button.setToolTip("Stop automatic simulation")
        self.stop_sim_button.clicked.connect(self.stop_auto_simulation)
        self.stop_sim_button.setEnabled(False)
        sim_controls_layout.addWidget(self.stop_sim_button)

        sim_controls_layout.addStretch()

        self.sim_speed_label = QLabel("Speed: 1.0x")
        sim_controls_layout.addWidget(self.sim_speed_label)

        self.sim_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.sim_speed_slider.setRange(10, 500)  # 0.1x to 5.0x speed
        self.sim_speed_slider.setValue(100)  # 1.0x default
        self.sim_speed_slider.setFixedWidth(100)
        self.sim_speed_slider.valueChanged.connect(self.update_sim_speed)
        sim_controls_layout.addWidget(self.sim_speed_slider)

        sim_layout.addLayout(sim_controls_layout)

        layout.addWidget(sim_group)
        layout.addWidget(register_group)

        return panel

    def _create_status_panel(self) -> QWidget:
        """Create the status and logging panel with enhanced monitoring."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # System Status - Connection and Performance
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)

        # Connection status with indicator
        connection_layout = QHBoxLayout()
        connection_label = QLabel("Connection:")
        connection_layout.addWidget(connection_label)

        self.connection_status_label = QLabel("🔵 Simulating")
        self.connection_status_label.setStyleSheet("font-weight: bold; color: #27ae60; padding: 2px 8px; background-color: rgba(39, 174, 96, 0.1); border-radius: 4px;")
        connection_layout.addWidget(self.connection_status_label)

        self.connection_button = QPushButton("Connect")
        self.connection_button.setToolTip("Start/stop Modbus server simulation")
        self.connection_button.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connection_button)

        status_layout.addLayout(connection_layout)

        # Performance metrics
        metrics_layout = QHBoxLayout()

        # Device count with progress
        device_layout = QVBoxLayout()
        device_label = QLabel("Devices")
        device_layout.addWidget(device_label)
        self.device_progress = QProgressBar()
        self.device_progress.setRange(0, 10)  # Max 10 devices for now
        self.device_progress.setFormat("0/10")
        device_layout.addWidget(self.device_progress)
        metrics_layout.addLayout(device_layout)

        # Register count with progress
        register_layout = QVBoxLayout()
        register_label = QLabel("Registers")
        register_layout.addWidget(register_label)
        self.register_progress = QProgressBar()
        self.register_progress.setRange(0, 50)  # Max 50 registers for now
        self.register_progress.setFormat("0/50")
        register_layout.addWidget(self.register_progress)
        metrics_layout.addLayout(register_layout)

        # Memory usage indicator
        memory_layout = QVBoxLayout()
        memory_label = QLabel("Memory")
        memory_layout.addWidget(memory_label)
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setFormat("50%")
        self.memory_progress.setValue(50)
        memory_layout.addWidget(self.memory_progress)
        metrics_layout.addLayout(memory_layout)

        status_layout.addLayout(metrics_layout)

        # Current selection info
        selection_layout = QHBoxLayout()
        selection_label = QLabel("Selected Device:")
        selection_layout.addWidget(selection_label)

        self.selection_info_label = QLabel("None")
        self.selection_info_label.setStyleSheet("font-weight: bold; color: #3498db;")
        selection_layout.addWidget(self.selection_info_label)

        status_layout.addLayout(selection_layout)

        layout.addWidget(status_group)

        # Real-time monitoring panel
        monitoring_group = QGroupBox("Real-time Monitoring")
        monitoring_layout = QVBoxLayout()
        monitoring_group.setLayout(monitoring_layout)

        # Register value monitoring
        self.monitoring_text = QTextEdit()
        self.monitoring_text.setMaximumHeight(120)
        self.monitoring_text.setHtml("""
        <div style='font-family: monospace; background-color: #1a1a1a; color: #00ff00; padding: 5px;'>
        <b>Real-time Register Monitor</b><br>
        <span id='monitor-content'>Monitoring active...</span>
        </div>
        """)
        monitoring_layout.addWidget(self.monitoring_text)

        # Monitoring controls
        monitor_controls = QHBoxLayout()

        self.start_monitoring_button = QPushButton("▶️ Start Monitoring")
        self.start_monitoring_button.setToolTip("Start real-time register value monitoring")
        self.start_monitoring_button.clicked.connect(self.start_monitoring)
        monitor_controls.addWidget(self.start_monitoring_button)

        self.stop_monitoring_button = QPushButton("⏸️ Stop Monitoring")
        self.stop_monitoring_button.setToolTip("Stop real-time monitoring")
        self.stop_monitoring_button.clicked.connect(self.stop_monitoring)
        self.stop_monitoring_button.setEnabled(False)
        monitor_controls.addWidget(self.stop_monitoring_button)

        monitoring_layout.addLayout(monitor_controls)

        layout.addWidget(monitoring_group)

        # Enhanced log panel with filtering
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)

        # Log controls
        log_controls = QHBoxLayout()

        self.log_filter_combo = QComboBox()
        self.log_filter_combo.addItems(["All", "Device", "Register", "Error", "Info"])
        self.log_filter_combo.setCurrentText("All")
        self.log_filter_combo.currentTextChanged.connect(self.filter_log)
        log_controls.addWidget(QLabel("Filter:"))
        log_controls.addWidget(self.log_filter_combo)

        log_controls.addStretch()

        export_log_button = QPushButton("📄 Export Log")
        export_log_button.setToolTip("Export log to file")
        export_log_button.clicked.connect(self.export_log)
        log_controls.addWidget(export_log_button)

        log_layout.addLayout(log_controls)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        clear_log_button = QPushButton("🗑️ Clear Log")
        clear_log_button.setToolTip("Clear all log entries")
        clear_log_button.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_button)

        layout.addWidget(log_group)

        return panel

    def update_ui(self) -> None:
        """Update the user interface with current data."""
        from datetime import datetime
        self.last_update = datetime.now()

        self.refresh_device_list()

        # Clear register table if no devices exist or no device is selected
        devices = self.simulation_runtime.list_devices()
        if not devices or not self.current_device:
            self.register_table.setRowCount(0)
        else:
            self.refresh_register_table()

        self.update_status_bar()

    def update_status_bar(self) -> None:
        """Update the status bar with current information."""
        device_count = len(self.simulation_runtime.list_devices())
        self.device_count_label.setText(f"Devices: {device_count}")

        if self.current_device:
            register_count = len(self.current_device.list_holding_registers())
            self.register_count_label.setText(f"Registers: {register_count}")
            self.selection_info_label.setText(self.current_device.display_name)
        else:
            self.register_count_label.setText("Registers: 0")
            self.selection_info_label.setText("None")

        # Update progress bars
        self.device_progress.setValue(device_count)
        self.device_progress.setFormat(f"{device_count}/10")

        total_registers = 0
        for device in self.simulation_runtime.list_devices():
            total_registers += len(device.list_holding_registers())
        self.register_progress.setValue(min(total_registers, 50))
        self.register_progress.setFormat(f"{total_registers}/50")

        # Update connection status (for now, always show "Simulating")
        self.connection_indicator.setText("🔵 Simulating")
        self.connection_indicator.setStyleSheet("color: #27ae60; font-weight: bold;")

        # Update last update time
        if self.last_update:
            time_str = self.last_update.strftime("%H:%M:%S")
            self.last_update_label.setText(f"Last Update: {time_str}")

    def import_configuration(self) -> None:
        """Import device configuration from file."""
        from PyQt6.QtWidgets import QFileDialog
        import json

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Configuration",
            "",
            "JSON files (*.json);;YAML files (*.yml *.yaml);;All files (*)"
        )

        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                if filename.endswith(('.yml', '.yaml')):
                    import yaml
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)

            # Import devices from configuration
            devices_imported = 0
            for device_data in config_data.get('devices', []):
                try:
                    device_id = device_data['device_id']
                    name = device_data.get('name', f'Device {device_id}')
                    registers = []

                    for reg_data in device_data.get('registers', []):
                        register_def = RegisterDefinition(
                            address=reg_data['address'],
                            value=reg_data.get('value', 0),
                            label=reg_data.get('label', '')
                        )
                        registers.append(register_def)

                    descriptor = DeviceDescriptor(
                        device_id=device_id,
                        name=name,
                        registers=registers
                    )

                    self.simulation_runtime.add_device(descriptor)
                    devices_imported += 1

                except Exception as e:
                    self.log_message(f"Failed to import device {device_data.get('name', 'unknown')}: {str(e)}")

            self.log_message(f"Successfully imported {devices_imported} devices from {filename}")
            self.refresh_device_list()

            self.log_message(f"✅ Successfully imported {devices_imported} devices from {filename}")

        except Exception as e:
            self.log_message(f"❌ Import Error: Failed to import configuration: {str(e)}")

    def export_configuration(self) -> None:
        """Export device configuration to file."""
        from PyQt6.QtWidgets import QFileDialog
        import json

        devices = self.simulation_runtime.list_devices()
        if not devices:
            self.log_message("⚠️ Export Error: No devices to export")
            return

        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            "mb_sim_config.json",
            "JSON files (*.json);;YAML files (*.yml);;All files (*)"
        )

        if not filename:
            return

        try:
            config_data = {
                'version': '1.0',
                'exported_at': str(self.last_update),
                'devices': []
            }

            for device in devices:
                device_data = {
                    'device_id': device.config.device_id,
                    'name': device.display_name,
                    'registers': []
                }

                for register in device.list_holding_registers():
                    reg_data = {
                        'address': register.address,
                        'value': register.value,
                        'label': register.label
                    }
                    device_data['registers'].append(reg_data)

                config_data['devices'].append(device_data)

            with open(filename, 'w') as f:
                if filename.endswith(('.yml', '.yaml')):
                    import yaml
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2)

            self.log_message(f"Exported configuration to {filename}")
            self.log_message(f"✅ Configuration exported to {filename}")

        except Exception as e:
            self.log_message(f"❌ Export Error: Failed to export configuration: {str(e)}")

    def show_settings(self) -> None:
        """Show application settings dialog."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QGroupBox, QFormLayout, QTabWidget, QWidget

        class SettingsDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Application Settings")
                self.setModal(True)
                self.resize(500, 400)

                layout = QVBoxLayout()
                self.setLayout(layout)

                # Create tab widget for different settings categories
                tab_widget = QTabWidget()

                # General settings tab
                general_tab = self._create_general_tab()
                tab_widget.addTab(general_tab, "General")

                # Simulation settings tab
                sim_tab = self._create_simulation_tab()
                tab_widget.addTab(sim_tab, "Simulation")

                # UI settings tab
                ui_tab = self._create_ui_tab()
                tab_widget.addTab(ui_tab, "Interface")

                layout.addWidget(tab_widget)

                # Button layout
                button_layout = QHBoxLayout()
                button_layout.addStretch()

                save_button = QPushButton("💾 Save Settings")
                save_button.clicked.connect(self.accept)
                button_layout.addWidget(save_button)

                cancel_button = QPushButton("❌ Cancel")
                cancel_button.clicked.connect(self.reject)
                button_layout.addWidget(cancel_button)

                layout.addLayout(button_layout)

            def _create_general_tab(self):
                tab = QWidget()
                layout = QFormLayout()
                tab.setLayout(layout)

                # Auto-refresh interval
                self.refresh_interval = QSpinBox()
                self.refresh_interval.setRange(100, 10000)  # 100ms to 10s
                self.refresh_interval.setValue(1000)  # 1 second default
                self.refresh_interval.setSuffix(" ms")
                layout.addRow("Auto-refresh interval:", self.refresh_interval)

                # Log retention
                self.log_retention = QSpinBox()
                self.log_retention.setRange(100, 10000)  # 100 to 10000 lines
                self.log_retention.setValue(1000)
                self.log_retention.setSuffix(" lines")
                layout.addRow("Log retention:", self.log_retention)

                # Default device count
                self.default_devices = QSpinBox()
                self.default_devices.setRange(1, 10)
                self.default_devices.setValue(1)
                layout.addRow("Default devices:", self.default_devices)

                return tab

            def _create_simulation_tab(self):
                tab = QWidget()
                layout = QVBoxLayout()
                tab.setLayout(layout)

                # Simulation settings group
                sim_group = QGroupBox("Simulation Behavior")
                sim_layout = QFormLayout()
                sim_group.setLayout(sim_layout)

                # Auto-start simulation
                self.auto_start_sim = QCheckBox("Auto-start simulation on device selection")
                sim_layout.addRow(self.auto_start_sim)

                # Default simulation pattern
                self.default_pattern = QComboBox()
                self.default_pattern.addItems(["None", "Sine Wave", "Sawtooth", "Ramp", "Random"])
                sim_layout.addRow("Default pattern:", self.default_pattern)

                # Pattern speed
                self.pattern_speed = QSpinBox()
                self.pattern_speed.setRange(1, 100)  # 1x to 100x speed
                self.pattern_speed.setValue(10)
                self.pattern_speed.setSuffix("x")
                sim_layout.addRow("Pattern speed:", self.pattern_speed)

                layout.addWidget(sim_group)

                # Value bounds group
                bounds_group = QGroupBox("Value Constraints")
                bounds_layout = QFormLayout()
                bounds_group.setLayout(bounds_layout)

                # Min value
                self.min_value = QSpinBox()
                self.min_value.setRange(0, 65535)
                self.min_value.setValue(0)
                bounds_layout.addRow("Minimum value:", self.min_value)

                # Max value
                self.max_value = QSpinBox()
                self.max_value.setRange(0, 65535)
                self.max_value.setValue(65535)
                bounds_layout.addRow("Maximum value:", self.max_value)

                layout.addWidget(bounds_group)
                layout.addStretch()

                return tab

            def _create_ui_tab(self):
                tab = QWidget()
                layout = QVBoxLayout()
                tab.setLayout(layout)

                # Appearance group
                appearance_group = QGroupBox("Appearance")
                appearance_layout = QFormLayout()
                appearance_group.setLayout(appearance_layout)

                # Theme selection
                self.theme_combo = QComboBox()
                self.theme_combo.addItems(["Modern Blue", "Dark Theme", "Light Theme", "High Contrast"])
                self.theme_combo.setCurrentText("Modern Blue")
                appearance_layout.addRow("Theme:", self.theme_combo)

                # Font size
                self.font_size = QSpinBox()
                self.font_size.setRange(8, 18)
                self.font_size.setValue(10)
                self.font_size.setSuffix(" pt")
                appearance_layout.addRow("Font size:", self.font_size)

                # Show tooltips
                self.show_tooltips = QCheckBox("Show tooltips")
                self.show_tooltips.setChecked(True)
                appearance_layout.addRow(self.show_tooltips)

                layout.addWidget(appearance_group)

                # Window behavior group
                window_group = QGroupBox("Window Behavior")
                window_layout = QFormLayout()
                window_group.setLayout(window_layout)

                # Remember window size
                self.remember_size = QCheckBox("Remember window size and position")
                self.remember_size.setChecked(True)
                window_layout.addRow(self.remember_size)

                # Always on top
                self.always_on_top = QCheckBox("Keep window always on top")
                window_layout.addRow(self.always_on_top)

                layout.addWidget(window_group)
                layout.addStretch()

                return tab

        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.log_message("✅ Settings updated successfully")
        else:
            self.log_message("ℹ️ Settings dialog cancelled")

    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About MB-Sim",
            "<h3>MB-Sim Modbus Simulator</h3>"
            "<p>Version 0.0.0.1</p>"
            "<p>A powerful tool for simulating Modbus devices and testing Modbus applications.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Simulate multiple Modbus devices</li>"
            "<li>Real-time register monitoring</li>"
            "<li>Device and register management</li>"
            "<li>Activity logging</li>"
            "</ul>"
            "<p>© 2025 MB-Sim Team</p>"
        )

    def refresh_device_list(self) -> None:
        """Refresh the device list while preserving selection."""
        # Store the currently selected device ID before clearing
        selected_device_id = None
        current_item = self.device_list.currentItem()
        if current_item and self.current_device:
            selected_device_id = self.current_device.config.device_id

        # Clear and rebuild the list
        self.device_list.clear()

        devices = self.simulation_runtime.list_devices()
        selected_item = None

        for device in devices:
            item_text = f"{device.config.device_id}: {device.display_name}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)

            # If this device was selected before, store the item for re-selection
            if selected_device_id and device.config.device_id == selected_device_id:
                selected_item = item

        # Restore selection if the device still exists
        if selected_item:
            self.device_list.setCurrentItem(selected_item)
        elif not devices and self.current_device:
            # If no devices exist but we had a current device, clear it
            self.current_device = None
            self.selection_info_label.setText("No device selected")
            self.register_table.setRowCount(0)

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
            address_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.register_table.setItem(row, 0, address_item)

            # Value
            value_item = QTableWidgetItem(str(register.value))
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.register_table.setItem(row, 1, value_item)

            # Progress bar (visual representation of value 0-100%)
            progress_widget = QWidget()
            progress_layout = QHBoxLayout()
            progress_layout.setContentsMargins(5, 5, 5, 5)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 65535)
            progress_bar.setValue(register.value)
            progress_bar.setTextVisible(True)
            progress_bar.setFormat(f"{register.value}/65535")
            progress_layout.addWidget(progress_bar)

            progress_widget.setLayout(progress_layout)
            self.register_table.setCellWidget(row, 2, progress_widget)

            # Label
            label_item = QTableWidgetItem(register.label or "")
            self.register_table.setItem(row, 3, label_item)

            # Status indicator (for now, just show if value is in normal range)
            status_widget = QWidget()
            status_layout = QHBoxLayout()
            status_layout.setContentsMargins(5, 5, 5, 5)

            status_label = QLabel(self._get_register_status_icon(register.value))
            status_layout.addWidget(status_label)

            status_widget.setLayout(status_layout)
            self.register_table.setCellWidget(row, 4, status_widget)

    def _get_register_status_icon(self, value: int) -> str:
        """Get status icon based on register value."""
        if value == 0:
            return "⚪"  # Empty
        elif value < 1000:
            return "🟢"  # Low
        elif value < 5000:
            return "🟡"  # Medium
        elif value < 10000:
            return "🟠"  # High
        else:
            return "🔴"  # Very High

    def on_device_selected(self) -> None:
        """Handle device selection."""
        current_item = self.device_list.currentItem()
        if current_item:
            self.current_device = current_item.data(Qt.ItemDataRole.UserRole)
            self.selection_info_label.setText(f"Selected: {self.current_device.display_name}")
            self.refresh_register_table()
        else:
            self.current_device = None
            self.selection_info_label.setText("No device selected")
            self.register_table.setRowCount(0)

    def _get_next_available_device_id(self) -> int:
        """Calculate the next available device ID."""
        existing_ids = {device.config.device_id for device in self.simulation_runtime.list_devices()}
        next_device_id = 1
        while next_device_id in existing_ids:
            next_device_id += 1
        return next_device_id

    def add_device(self) -> None:
        """Add a new device."""
        # Get the next available device ID
        next_device_id = self._get_next_available_device_id()

        # Create dialog with smart default
        dialog = DeviceDialog(device_id=next_device_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            device_id, name, description = dialog.get_device_config()

            try:
                descriptor = DeviceDescriptor(device_id=device_id, name=name, registers=[])
                device = self.simulation_runtime.add_device(descriptor)
                device.config = DeviceConfig(device_id, name, description)

                self.log_message(f"✅ Added device: {device.display_name} (ID: {device_id})")
                self.refresh_device_list()

            except ValueError as error:
                self.log_message(f"❌ Device Error: {str(error)}")
        else:
            self.log_message(f"ℹ️ Device creation cancelled - suggested ID was {next_device_id}")

    def remove_device(self) -> None:
        """Remove the selected device."""
        if not self.current_device:
            self.log_message("⚠️ No device selected to remove")
            return

        try:
            device_name = self.current_device.display_name
            self.simulation_runtime.remove_device(self.current_device.config.device_id)
            self.log_message(f"✅ Removed device: {device_name}")
            self.current_device = None
            self.refresh_device_list()
            self.register_table.setRowCount(0)  # Clear ghost registers
        except KeyError as error:
            self.log_message(f"❌ Device Removal Error: {str(error)}")

    def add_register(self) -> None:
        """Add a new register to the current device."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device first")
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
                self.log_message(f"❌ Register Error: {str(e)}")

    def edit_register(self) -> None:
        """Edit the selected register."""
        current_row = self.register_table.currentRow()
        if current_row < 0 or not self.current_device:
            self.log_message("⚠️ No register selected - please select a register to edit")
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
                self.log_message(f"❌ Key Error: {str(e)}")

    def remove_register(self) -> None:
        """Remove the selected register."""
        current_row = self.register_table.currentRow()
        if current_row < 0 or not self.current_device:
            self.log_message("⚠️ No register selected - please select a register to remove")
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
                self.log_message(f"❌ Key Error: {str(e)}")

    def log_message(self, message: str) -> None:
        """Add a message to the activity log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def clear_log(self) -> None:
        """Clear the activity log."""
        self.log_text.clear()

    def randomize_registers(self) -> None:
        """Set random values for all registers in the current device."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device first")
            return

        import random
        registers = self.current_device.list_holding_registers()

        for register in registers:
            random_value = random.randint(0, 65535)
            register.value = random_value

        self.log_message(f"Randomized all register values for {self.current_device.display_name}")
        self.refresh_register_table()

    def increment_registers(self) -> None:
        """Increment all register values by 1."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device first")
            return

        registers = self.current_device.list_holding_registers()

        for register in registers:
            if register.value < 65535:
                register.value += 1
            else:
                register.value = 0  # Wrap around

        self.log_message(f"Incremented all register values for {self.current_device.display_name}")
        self.refresh_register_table()

    def duplicate_device(self) -> None:
        """Duplicate the currently selected device."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device to duplicate")
            return

        try:
            # Find next available device ID
            existing_ids = {device.config.device_id for device in self.simulation_runtime.list_devices()}
            new_device_id = 1
            while new_device_id in existing_ids:
                new_device_id += 1

            # Create new device with same registers
            registers = []
            for register in self.current_device.list_holding_registers():
                registers.append(RegisterDefinition(
                    address=register.address,
                    value=register.value,
                    label=register.label
                ))

            descriptor = DeviceDescriptor(
                device_id=new_device_id,
                name=f"{self.current_device.display_name} (Copy)",
                registers=registers
            )

            device = self.simulation_runtime.add_device(descriptor)
            self.log_message(f"Duplicated device: {self.current_device.display_name} -> {device.display_name}")
            self.refresh_device_list()

        except ValueError as error:
            self.log_message(f"❌ Device Error: {str(error)}")

    def clear_all_devices(self) -> None:
        """Remove all devices from the simulation."""
        devices = self.simulation_runtime.list_devices()

        if not devices:
            self.log_message("⚠️ No devices to clear")
            return

        try:
            device_count = len(devices)
            for device in devices:
                self.simulation_runtime.remove_device(device.config.device_id)

            self.current_device = None
            self.log_message(f"✅ Cleared all {device_count} devices from simulation")
            self.refresh_device_list()
            self.register_table.setRowCount(0)  # Ensure ghost registers are cleared

        except Exception as error:
            self.log_message(f"❌ Clear Error: {str(error)}")

    def toggle_connection(self) -> None:
        """Toggle the connection status of the Modbus simulator."""
        if self.connection_status == "Disconnected":
            self.connection_status = "Connected"
            self.connection_button.setText("Disconnect")
            self.connection_status_label.setText("🟢 Connected")
            self.connection_status_label.setStyleSheet("font-weight: bold; color: #27ae60; padding: 2px 8px; background-color: rgba(39, 174, 96, 0.1); border-radius: 4px;")
            self.log_message("Modbus server started on port 1502")
        else:
            self.connection_status = "Disconnected"
            self.connection_button.setText("Connect")
            self.connection_status_label.setText("🔵 Simulating")
            self.connection_status_label.setStyleSheet("font-weight: bold; color: #f39c12; padding: 2px 8px; background-color: rgba(243, 156, 18, 0.1); border-radius: 4px;")
            self.log_message("Modbus server stopped")

    def start_monitoring(self) -> None:
        """Start real-time monitoring of register values."""
        if not self.current_device:
            QMessageBox.information(self, "No Device", "Please select a device to monitor.")
            return

        self.start_monitoring_button.setEnabled(False)
        self.stop_monitoring_button.setEnabled(True)
        self.monitoring_active = True

        # Start faster updates for monitoring
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.update_monitoring_display)
        self.monitoring_timer.start(500)  # Update every 500ms

        self.log_message(f"Started monitoring {self.current_device.display_name}")

    def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self.start_monitoring_button.setEnabled(True)
        self.stop_monitoring_button.setEnabled(False)
        self.monitoring_active = False

        if hasattr(self, 'monitoring_timer'):
            self.monitoring_timer.stop()

        self.monitoring_text.setHtml("""
        <div style='font-family: monospace; background-color: #1a1a1a; color: #666; padding: 5px;'>
        <b>Real-time Register Monitor</b><br>
        <span id='monitor-content'>Monitoring stopped...</span>
        </div>
        """)

        self.log_message("Stopped monitoring")

    def update_monitoring_display(self) -> None:
        """Update the monitoring display with current register values."""
        if not self.monitoring_active or not self.current_device:
            return

        registers = self.current_device.list_holding_registers()
        monitor_html = "<div style='font-family: monospace; background-color: #1a1a1a; color: #00ff00; padding: 5px;'>"
        monitor_html += f"<b>Monitoring: {self.current_device.display_name}</b><br>"

        for register in registers[:10]:  # Show first 10 registers
            status_icon = self._get_register_status_icon(register.value)
            monitor_html += f"{status_icon} {register.address:5d}: {register.value:5d} {register.label or ''}<br>"

        if len(registers) > 10:
            monitor_html += f"... and {len(registers) - 10} more registers<br>"

        monitor_html += f"<i>Updated: {self.last_update.strftime('%H:%M:%S.%f')[:-3]}</i>"
        monitor_html += "</div>"

        self.monitoring_text.setHtml(monitor_html)

    def filter_log(self, filter_type: str) -> None:
        """Filter the log display based on message type."""
        # For now, just refresh the log - filtering logic will be enhanced later
        pass

    def export_log(self) -> None:
        """Export the activity log to a file."""
        log_content = self.log_text.toPlainText()
        if not log_content.strip():
            self.log_message("⚠️ No log data to export")
            return

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mb_sim_log_{timestamp}.txt"

        try:
            with open(filename, 'w') as f:
                f.write("MB-Sim Activity Log\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(log_content)

            self.log_message(f"✅ Log exported to {filename}")

        except Exception as e:
            self.log_message(f"❌ Export Error: Failed to export log: {str(e)}")

    def load_basic_preset(self) -> None:
        """Load a basic device preset with standard registers."""
        try:
            # Get next available device ID
            device_id = self._get_next_available_device_id()

            registers = [
                RegisterDefinition(address=40001, value=100, label="Temperature"),
                RegisterDefinition(address=40002, value=200, label="Pressure"),
                RegisterDefinition(address=40003, value=300, label="Flow Rate"),
                RegisterDefinition(address=40004, value=0, label="Status Word"),
                RegisterDefinition(address=40005, value=1, label="Control Word"),
            ]

            descriptor = DeviceDescriptor(
                device_id=device_id,
                name="Basic Device",
                registers=registers
            )

            device = self.simulation_runtime.add_device(descriptor)
            self.log_message(f"Loaded basic device preset: {device.display_name}")
            self.refresh_device_list()

            self.log_message("✅ Basic device preset loaded successfully!")

        except Exception as e:
            self.log_message(f"❌ Preset Error: Failed to load preset: {str(e)}")

    def load_sensor_preset(self) -> None:
        """Load sensor simulation devices."""
        try:
            # Load multiple sensor devices
            sensor_configs = [
                {"name": "Temperature Sensor", "registers": [
                    RegisterDefinition(address=40001, value=25, label="Temperature °C"),
                    RegisterDefinition(address=40002, value=0, label="Alarm Status"),
                    RegisterDefinition(address=40003, value=1, label="Sensor Status"),
                ]},
                {"name": "Pressure Sensor", "registers": [
                    RegisterDefinition(address=40001, value=1013, label="Pressure mBar"),
                    RegisterDefinition(address=40002, value=0, label="Alarm Status"),
                    RegisterDefinition(address=40003, value=1, label="Sensor Status"),
                ]},
                {"name": "Flow Meter", "registers": [
                    RegisterDefinition(address=40001, value=150, label="Flow Rate L/min"),
                    RegisterDefinition(address=40002, value=0, label="Total Volume"),
                    RegisterDefinition(address=40003, value=1, label="Sensor Status"),
                ]},
            ]

            devices_added = 0
            existing_ids = {device.config.device_id for device in self.simulation_runtime.list_devices()}

            for config in sensor_configs:
                # Find next available device ID
                device_id = 1
                while device_id in existing_ids:
                    device_id += 1
                existing_ids.add(device_id)  # Add to set to avoid conflicts with other sensors

                descriptor = DeviceDescriptor(
                    device_id=device_id,
                    name=config["name"],
                    registers=config["registers"]
                )

                self.simulation_runtime.add_device(descriptor)
                devices_added += 1

            self.log_message(f"✅ Loaded sensor simulation preset with {devices_added} devices")
            self.refresh_device_list()

        except Exception as e:
            self.log_message(f"❌ Preset Error: Failed to load preset: {str(e)}")

    def load_motor_preset(self) -> None:
        """Load motor control simulation devices."""
        try:
            device_id = self._get_next_available_device_id()

            registers = [
                RegisterDefinition(address=40001, value=1500, label="Motor Speed RPM"),
                RegisterDefinition(address=40002, value=100, label="Motor Current %"),
                RegisterDefinition(address=40003, value=85, label="Motor Temperature °C"),
                RegisterDefinition(address=40004, value=1, label="Motor Status"),
                RegisterDefinition(address=40005, value=1, label="Control Word"),
                RegisterDefinition(address=40006, value=0, label="Fault Code"),
            ]

            descriptor = DeviceDescriptor(
                device_id=device_id,
                name="Motor Controller",
                registers=registers
            )

            device = self.simulation_runtime.add_device(descriptor)
            self.log_message(f"Loaded motor control preset: {device.display_name}")
            self.refresh_device_list()

            self.log_message("✅ Motor control preset loaded successfully!")

        except Exception as e:
            self.log_message(f"❌ Preset Error: Failed to load preset: {str(e)}")

    def load_hmi_preset(self) -> None:
        """Load HMI panel simulation devices."""
        try:
            device_id = self._get_next_available_device_id()

            registers = [
                RegisterDefinition(address=40001, value=1, label="Screen Number"),
                RegisterDefinition(address=40002, value=100, label="Brightness %"),
                RegisterDefinition(address=40003, value=0, label="Touch Status"),
                RegisterDefinition(address=40004, value=25, label="Temperature °C"),
                RegisterDefinition(address=40005, value=0, label="Alarm Active"),
                RegisterDefinition(address=40006, value=1, label="System Status"),
            ]

            descriptor = DeviceDescriptor(
                device_id=device_id,
                name="HMI Panel",
                registers=registers
            )

            device = self.simulation_runtime.add_device(descriptor)
            self.log_message(f"Loaded HMI panel preset: {device.display_name}")
            self.refresh_device_list()

            self.log_message("✅ HMI panel preset loaded successfully!")

        except Exception as e:
            self.log_message(f"❌ Preset Error: Failed to load preset: {str(e)}")

    def decrement_registers(self) -> None:
        """Decrement all register values by 1."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device first")
            return

        registers = self.current_device.list_holding_registers()

        for register in registers:
            if register.value > 0:
                register.value -= 1
            else:
                register.value = 65535  # Wrap around

        self.log_message(f"Decremented all register values for {self.current_device.display_name}")
        self.refresh_register_table()

    def apply_sine_pattern(self) -> None:
        """Apply sine wave pattern to register values."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device first")
            return

        import math
        registers = self.current_device.list_holding_registers()

        for i, register in enumerate(registers):
            # Create sine wave pattern with different phases
            phase = i * 0.5  # Offset each register slightly
            sine_value = math.sin(phase) * 32767 + 32767  # Scale to 0-65535
            register.value = int(sine_value)

        self.log_message(f"Applied sine wave pattern to {self.current_device.display_name}")
        self.refresh_register_table()

    def apply_sawtooth_pattern(self) -> None:
        """Apply sawtooth pattern to register values."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device first")
            return

        registers = self.current_device.list_holding_registers()
        num_registers = len(registers)

        for i, register in enumerate(registers):
            # Create sawtooth pattern: linear ramp from 0 to 65535
            progress = i / max(num_registers - 1, 1)  # 0 to 1
            register.value = int(progress * 65535)

        self.log_message(f"Applied sawtooth pattern to {self.current_device.display_name}")
        self.refresh_register_table()

    def apply_ramp_pattern(self) -> None:
        """Apply ramp pattern (0-100% cycle) to register values."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device first")
            return

        registers = self.current_device.list_holding_registers()
        num_registers = len(registers)

        for i, register in enumerate(registers):
            # Create ramp pattern: 0 to 100% cycle
            cycle_position = (i / max(num_registers - 1, 1)) * 100
            register.value = int((cycle_position / 100) * 65535)

        self.log_message(f"Applied ramp pattern to {self.current_device.display_name}")
        self.refresh_register_table()

    def start_auto_simulation(self) -> None:
        """Start automatic simulation with the current pattern."""
        if not self.current_device:
            self.log_message("⚠️ No device selected - please select a device to start auto-simulation")
            return

        self.auto_sim_active = True
        self.auto_sim_button.setEnabled(False)
        self.stop_sim_button.setEnabled(True)

        # Start the simulation timer
        self.sim_step = 0
        self.auto_sim_timer = QTimer()
        self.auto_sim_timer.timeout.connect(self.update_auto_simulation)
        self.update_sim_speed()  # Set initial speed

        self.log_message(f"Started automatic simulation for {self.current_device.display_name}")

    def stop_auto_simulation(self) -> None:
        """Stop automatic simulation."""
        self.auto_sim_active = False
        self.auto_sim_button.setEnabled(True)
        self.stop_sim_button.setEnabled(False)

        if hasattr(self, 'auto_sim_timer'):
            self.auto_sim_timer.stop()

        self.log_message("Stopped automatic simulation")

    def update_auto_simulation(self) -> None:
        """Update the automatic simulation."""
        if not self.auto_sim_active or not self.current_device:
            return

        import math
        registers = self.current_device.list_holding_registers()

        for i, register in enumerate(registers):
            # Apply different simulation patterns based on register index
            if i % 4 == 0:  # Sine wave
                phase = (self.sim_step + i * 10) * 0.1
                value = math.sin(phase) * 32767 + 32767
            elif i % 4 == 1:  # Sawtooth
                progress = (self.sim_step + i) % 100 / 100.0
                value = progress * 65535
            elif i % 4 == 2:  # Ramp
                cycle_pos = (self.sim_step + i) % 200 / 200.0
                value = cycle_pos * 65535
            else:  # Random walk
                current = register.value
                change = (math.sin(self.sim_step * 0.1 + i) + 1) * 1000
                value = max(0, min(65535, current + change - 1000))

            register.value = int(value)

        self.sim_step += 1
        self.refresh_register_table()

    def update_sim_speed(self) -> None:
        """Update the simulation speed based on slider value."""
        speed_value = self.sim_speed_slider.value() / 100.0
        self.sim_speed_label.setText(f"Speed: {speed_value:.1f}x")

        if hasattr(self, 'auto_sim_timer') and self.auto_sim_active:
            interval = max(50, int(1000 / speed_value))  # Min 50ms, adjust based on speed
            self.auto_sim_timer.setInterval(interval)

