"""Scenario manager for loading and saving device configurations."""

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from mb_sim.models.device import Device, DeviceConfig
from mb_sim.models.register_map import RegisterDefinition


@dataclass
class Scenario:
    """Represents a scenario with devices and configuration."""
    name: str
    description: str
    version: str = "0.0.1"
    devices: Dict[int, Device] = None

    def __post_init__(self):
        if self.devices is None:
            self.devices = {}


class ScenarioManager:
    """Manages loading and saving scenarios from YAML files."""

    def __init__(self, scenario_dir: str = "scenarios") -> None:
        self.scenario_dir = Path(scenario_dir)
        self.scenario_dir.mkdir(exist_ok=True)

    def load_scenario(self, name: str) -> Scenario:
        """Load a scenario from a YAML file."""
        # Handle both .yml extension and no extension
        if not name.endswith('.yml'):
            name = f"{name}.yml"

        scenario_path = self.scenario_dir / name

        if not scenario_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {scenario_path}")

        with open(scenario_path, 'r') as f:
            data = yaml.safe_load(f)

        scenario = Scenario(
            name=data.get('name', name),
            description=data.get('description', ''),
            version=data.get('version', '0.0.1')
        )

        # Load devices
        devices_data = data.get('devices', {})
        for device_id, device_info in devices_data.items():
            device_id = int(device_id)

            config = DeviceConfig(
                device_id=device_id,
                name=device_info.get('name', f"Device {device_id}"),
                description=device_info.get('description', '')
            )

            device = Device(config)

            # Load registers
            registers_data = device_info.get('registers', {})
            for reg_type, registers in registers_data.items():
                if reg_type == 'holding_registers':
                    for reg_info in registers:
                        reg_def = RegisterDefinition(
                            address=reg_info['address'],
                            value=reg_info.get('value', 0),
                            label=reg_info.get('label')
                        )
                        device.add_holding_register(reg_def)

            scenario.devices[device_id] = device

        return scenario

    def save_scenario(self, scenario: Scenario, name: Optional[str] = None) -> None:
        """Save a scenario to a YAML file."""
        if name is None:
            name = scenario.name

        scenario_path = self.scenario_dir / f"{name}.yml"

        # Convert devices to serializable format
        devices_data = {}
        for device_id, device in scenario.devices.items():
            device_data = {
                'name': device.config.name,
                'description': device.config.description,
                'registers': {
                    'holding_registers': [
                        {
                            'address': reg.address,
                            'value': reg.value,
                            'label': reg.label
                        }
                        for reg in device.list_holding_registers()
                    ]
                }
            }
            devices_data[device_id] = device_data

        data = {
            'name': scenario.name,
            'description': scenario.description,
            'version': scenario.version,
            'devices': devices_data
        }

        with open(scenario_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def list_scenarios(self) -> List[str]:
        """List all available scenario files."""
        return [f.stem for f in self.scenario_dir.glob("*.yml")]

    def create_scenario(self, name: str, description: str = "") -> Scenario:
        """Create a new empty scenario."""
        return Scenario(
            name=name,
            description=description,
            devices={}
        )