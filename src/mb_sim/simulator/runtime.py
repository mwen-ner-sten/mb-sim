"""Runtime management for the Modbus simulator MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from mb_sim.models.device import Device, DeviceConfig
from mb_sim.models.register_map import RegisterDefinition


@dataclass
class DeviceDescriptor:
    device_id: int
    name: str
    registers: Iterable[RegisterDefinition] = field(default_factory=list)


class SimulationRuntime:
    """Maintains simulated devices and register state."""

    def __init__(self) -> None:
        self.devices: Dict[int, Device] = {}

    def add_device(self, descriptor: DeviceDescriptor) -> Device:
        if descriptor.device_id in self.devices:
            raise ValueError(f"Device {descriptor.device_id} already exists")

        device = Device(DeviceConfig(device_id=descriptor.device_id, name=descriptor.name))
        for register in descriptor.registers:
            device.add_holding_register(register)

        self.devices[descriptor.device_id] = device
        return device

    def list_devices(self) -> List[Device]:
        return list(self.devices.values())

    def get_device(self, device_id: int) -> Device:
        if device_id not in self.devices:
            raise KeyError(f"Device {device_id} not found")
        return self.devices[device_id]

    def remove_device(self, device_id: int) -> None:
        if device_id not in self.devices:
            raise KeyError(f"Device {device_id} not found")
        del self.devices[device_id]

